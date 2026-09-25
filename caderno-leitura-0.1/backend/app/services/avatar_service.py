from __future__ import annotations

import io
import logging
from pathlib import Path
import uuid

from fastapi import HTTPException
from PIL import Image, ImageOps

from app.core.config import get_avatars_dir

logger = logging.getLogger(__name__)

MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB
AVATAR_DIMENSIONS = (256, 256)
ALLOWED_AVATAR_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_and_crop_avatar(data: bytes, dimensions: tuple[int, int] = AVATAR_DIMENSIONS) -> bytes:
    """Valida formato, tamanho e recorta imagem no centro para formato quadrado 256x256 em WebP."""
    if not data or len(data) == 0:
        raise HTTPException(status_code=400, detail="Arquivo de imagem vazio.")

    if len(data) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="O arquivo excede o limite máximo permitido de 2 MB.")

    try:
        stream = io.BytesIO(data)
        with Image.open(stream) as img:
            fmt = img.format
            if not fmt or fmt.upper() not in ALLOWED_AVATAR_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de imagem não suportado. Utilize PNG, JPEG ou WebP.",
                )

            # Corrige orientação EXIF se presente
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # Recorte quadrado centralizado (square center-crop)
            cropped = ImageOps.fit(img, dimensions, method=Image.Resampling.LANCZOS)

            # Converte para RGB ou RGBA para saída WebP
            if cropped.mode in ("RGBA", "LA"):
                converted = cropped.convert("RGBA")
            else:
                converted = cropped.convert("RGB")

            output_buf = io.BytesIO()
            converted.save(output_buf, format="WEBP", quality=85, method=6)
            return output_buf.getvalue()
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Falha ao processar imagem de avatar: %s", exc)
        raise HTTPException(
            status_code=400,
            detail="Arquivo de imagem inválido ou corrompido.",
        ) from exc


def save_avatar_file(user_id: str, image_bytes: bytes, avatars_dir: Path | None = None) -> str:
    """Salva arquivo WebP no diretório de avatares e retorna a URL relativa."""
    target_dir = avatars_dir or get_avatars_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.webp"
    file_path = target_dir / filename
    file_path.write_bytes(image_bytes)
    return f"/api/avatars/{filename}"


def delete_avatar_file(avatar_url: str | None, avatars_dir: Path | None = None) -> None:
    """Remove arquivo de avatar antigo do disco caso seja um upload local."""
    if not avatar_url or not avatar_url.startswith("/api/avatars/"):
        return
    filename = avatar_url.split("/")[-1]
    target_dir = avatars_dir or get_avatars_dir()
    file_path = target_dir / filename
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as exc:
        logger.warning("Não foi possível excluir avatar antigo %s: %s", file_path, exc)
