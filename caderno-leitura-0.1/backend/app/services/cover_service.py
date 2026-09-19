"""Serviço de validação, processamento gráfico, download seguro e persistência de capas."""
import io
import ipaddress
import os
import re
import socket
import uuid
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps
from sqlalchemy.orm import Session

from app.core.config import get_covers_dir
from app.models.book import Book
from app.services.persistence import commit_changes, get_or_404

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_COVER_WIDTH = 800
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP", "GIF", "BMP", "TIFF", "ICO"}
SAFE_FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+\.(webp|jpg|jpeg|png|gif|bmp|tiff|tif|ico)$", re.IGNORECASE)


def validate_and_optimize_image(data: bytes, max_width: int = MAX_COVER_WIDTH) -> bytes:
    """Valida integridade, formato e redimensiona imagem para largura máxima de 800px no formato WebP."""
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Arquivo de imagem vazio.")

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="O arquivo de imagem excede o limite máximo permitido de 5 MB.")

    try:
        image_stream = io.BytesIO(data)
        with Image.open(image_stream) as img:
            image_format = img.format
            if not image_format or image_format.upper() not in ALLOWED_IMAGE_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de imagem não suportado. Utilize JPEG, JPG, PNG, WebP, GIF, BMP ou TIFF.",
                )

            # Para formatos com múltiplos quadros (GIF animado ou TIFF multipágina), posiciona no primeiro quadro
            try:
                img.seek(0)
            except Exception:
                pass

            # Corrige orientação EXIF se presente
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # Redimensiona mantendo proporção de aspecto se a largura for superior ao limite
            width, height = img.size
            if width > max_width:
                new_width = max_width
                new_height = int(round((height * max_width) / width))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Normalização de canais de cor para saída WebP:
            # - Se RGBA ou LA: converte LA para RGBA ou preserva RGBA
            # - Se P (paletizado, ex: GIF ou PNG 8-bit): converte para RGBA se houver transparência, senão RGB
            # - Se CMYK (comum em capas para gráfica): converte para RGB
            # - Se 1 ou L (monocromático / escala de cinza): converte para RGB
            # - Demais modos: converte para RGB
            if img.mode in ("RGBA", "LA"):
                converted = img.convert("RGBA") if img.mode == "LA" else img
            elif img.mode == "P":
                if "transparency" in img.info:
                    converted = img.convert("RGBA")
                else:
                    converted = img.convert("RGB")
            elif img.mode in ("CMYK", "1", "L"):
                converted = img.convert("RGB")
            else:
                converted = img.convert("RGB")

            output_stream = io.BytesIO()
            converted.save(output_stream, format="WEBP", quality=85, method=4)
            return output_stream.getvalue()

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível processar o arquivo de imagem: {exc}",
        ) from exc


def process_and_save_cover(data: bytes) -> str:
    """Processa o binário da imagem, otimiza para WebP e salva no diretório persistente de capas."""
    optimized_bytes = validate_and_optimize_image(data)
    filename = f"{uuid.uuid4().hex}.webp"
    covers_dir = get_covers_dir()
    file_path = covers_dir / filename
    file_path.write_bytes(optimized_bytes)
    return filename


def validate_safe_url(url_str: str) -> str:
    """Valida a URL contra ataques de SSRF, inspecionando protocolo e resolução de endereços IP."""
    try:
        parsed = urlparse(url_str)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="URL informada inválida.") from exc

    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Protocolo inválido. Apenas HTTP e HTTPS são suportados.")

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="A URL informada não contém um host válido.")

    port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)

    # Resolução DNS e checagem de IP anti-SSRF
    try:
        addr_info = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise HTTPException(status_code=400, detail="Não foi possível resolver o endereço do servidor informado.") from exc

    for entry in addr_info:
        sockaddr = entry[4]
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_multicast
                or ip_obj.is_reserved
                or ip_obj.is_unspecified
            ):
                raise HTTPException(
                    status_code=400,
                    detail="O endereço informado não é permitido por motivos de segurança.",
                )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Endereço IP inválido detectado na resolução da URL.") from exc

    return url_str


def download_cover_from_url(url_str: str) -> str:
    """Baixa com segurança uma imagem a partir de uma URL direta e persiste como capa."""
    safe_url = validate_safe_url(url_str)

    timeout = httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=5.0)
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            # Re-valida redirects para evitar DNS rebinding ou redirecionamento aberto para localhost
            response = client.get(safe_url)
            
            # Valida redirect final se houver
            if str(response.url) != safe_url:
                validate_safe_url(str(response.url))

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Falha ao baixar imagem: o servidor retornou código {response.status_code}.",
                )

            content_type = response.headers.get("content-type", "").lower()
            if not content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail="O endereço informado não retornou uma imagem válida.",
                )

            data = response.content
            if len(data) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail="O arquivo de imagem excede o limite máximo permitido de 5 MB.",
                )

            return process_and_save_cover(data)

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Tempo limite excedido ao tentar baixar a imagem da URL informada.",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Erro de conexão ao acessar a URL de imagem: {exc}",
        ) from exc


def delete_cover_file_if_orphan(session: Session, filename: str | None, current_book_id: int | None = None) -> bool:
    """Remove o arquivo físico de capa do disco se nenhum outro livro estiver referenciando-o."""
    if not filename:
        return False

    base_name = os.path.basename(filename)
    if not SAFE_FILENAME_REGEX.match(base_name):
        return False

    # Verifica se algum outro livro usa este mesmo arquivo
    query = session.query(Book).filter(Book.cover_image == base_name)
    if current_book_id is not None:
        query = query.filter(Book.id != current_book_id)

    still_used = query.count() > 0
    if not still_used:
        covers_dir = get_covers_dir()
        target_file = (covers_dir / base_name).resolve()
        if target_file.is_file() and str(target_file).startswith(str(covers_dir)):
            try:
                target_file.unlink(missing_ok=True)
                return True
            except Exception:
                pass

    return False


def set_book_cover(session: Session, book_id: int, filename: str) -> Book:
    """Associa uma nova capa ao livro e remove a anterior do disco se órfã."""
    book = get_or_404(session, Book, book_id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    old_cover = book.cover_image

    book.cover_image = filename
    commit_changes(session)
    session.refresh(book)

    if old_cover and old_cover != filename:
        delete_cover_file_if_orphan(session, old_cover, current_book_id=book.id)

    return book


def remove_book_cover(session: Session, book_id: int) -> Book:
    """Remove a capa do livro e exclui o arquivo físico do disco se órfão."""
    book = get_or_404(session, Book, book_id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    old_cover = book.cover_image
    if not old_cover:
        return book

    book.cover_image = None
    commit_changes(session)
    session.refresh(book)

    delete_cover_file_if_orphan(session, old_cover, current_book_id=book.id)
    return book
