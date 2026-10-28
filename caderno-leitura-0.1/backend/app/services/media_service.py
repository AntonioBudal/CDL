"""Mídias cifradas do usuário (feature 090-B): gravação, leitura, exclusão e regra de acesso.

Nenhuma imagem fica em claro em disco: depois de sanitizada (metadados removidos) e otimizada em WebP, ela é
cifrada (``app.services.vault``) e gravada como ``<uuid>.enc``. Nada aqui registra em log bytes de imagem,
chaves ou nomes; só tipos de erro e contagens.
"""

from __future__ import annotations

import hashlib
import io
import logging
import re
import threading
import uuid
from pathlib import Path

from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.encrypted_media import EncryptedMedia
from app.models.storage_settings import StorageSettings
from app.services import vault

logger = logging.getLogger("leitorum.media")

PAGE_MAX_SIDE = 2000
PAGE_QUALITY = 80
PAGE_MAX_BYTES = 20 * 1024 * 1024
PAGE_MAX_PIXELS = 40_000_000
THUMB_SIDE = 320
THUMB_VARIANT = b"thumb"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class VaultLocked(RuntimeError):
    def __init__(self, state: str) -> None:
        super().__init__(state)
        self.state = state


class MediaMissing(RuntimeError):
    pass


class MediaIntegrity(RuntimeError):
    pass


# --- estado do cofre ---------------------------------------------------------------------------

_lock = threading.Lock()
_state: dict | None = None


def reset_cache() -> None:
    global _state
    with _lock:
        _state = None


def _vault_dir() -> Path:
    from app.core.config import get_vault_dir

    return get_vault_dir()


def _load_state(session: Session, *, bind: bool = True) -> dict:
    from app.core.media_key import MediaKeyError, fingerprint, load_master_key
    from app.core.storage import StorageError

    try:
        key = load_master_key()
    except MediaKeyError as error:
        logger.warning("cofre: chave inválida (%s)", type(error).__name__)
        return {"state": "key_missing"}
    if key is None:
        return {"state": "key_missing"}
    try:
        folder = _vault_dir()
    except (StorageError, OSError):
        return {"state": "storage_unavailable"}
    current = fingerprint(key)
    settings = session.get(StorageSettings, 1)
    registered = settings.media_key_fingerprint if settings is not None else None
    if not bind:
        # Só consulta: nada é gravado (modo de planejamento dos scripts).
        state = "key_mismatch" if registered not in (None, current) else "ready"
        return {"state": state}
    if settings is None:
        # Instalação sem raiz de HD: a linha só guarda a impressão digital da chave.
        settings = StorageSettings(id=1, storage_id=str(uuid.uuid4()), media_key_fingerprint=current)
        session.add(settings)
        session.commit()
    elif settings.media_key_fingerprint is None:
        settings.media_key_fingerprint = current
        session.commit()
    elif settings.media_key_fingerprint != current:
        logger.warning("cofre: a chave configurada não é a deste acervo (impressão digital diferente)")
        return {"state": "key_mismatch"}
    return {"state": "ready", "key": key, "vault": folder, "epoch": settings.media_key_epoch, "fingerprint": current}


def vault_status(session: Session) -> dict:
    global _state
    with _lock:
        if _state is None or _state["state"] != "ready":
            _state = _load_state(session)
        return _state


def peek_status(session: Session) -> str:
    """Estado do cofre sem gravar a impressão digital nem usar o cache."""
    return _load_state(session, bind=False)["state"]


def require_vault(session: Session) -> dict:
    state = vault_status(session)
    if state["state"] != "ready":
        raise VaultLocked(state["state"])
    return state


# --- imagens -------------------------------------------------------------------------------------


def _clean_webp(image: Image.Image, quality: int) -> bytes:
    """Regrava como WebP sem nenhum metadado de origem (EXIF, GPS, ICC, XMP)."""
    clean = image.copy()
    clean.info = {}
    buffer = io.BytesIO()
    clean.save(buffer, format="WEBP", quality=quality, method=6)
    return buffer.getvalue()


def prepare_page(data: bytes) -> bytes:
    """Página de caderno: orientação da câmera, lado maior até 2000 px, WebP q80, sem metadados."""
    if len(data) > PAGE_MAX_BYTES:
        raise HTTPException(status_code=413, detail="A imagem passa de 20 MB.")
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ("JPEG", "PNG", "WEBP"):
                raise HTTPException(status_code=415, detail="Formato não suportado. Envie JPEG, PNG ou WebP.")
            if image.width * image.height > PAGE_MAX_PIXELS:
                raise HTTPException(status_code=413, detail="A imagem tem resolução grande demais.")
            image.load()
            page = ImageOps.exif_transpose(image).convert("RGB")
    except Image.DecompressionBombError as error:
        raise HTTPException(status_code=413, detail="A imagem tem resolução grande demais.") from error
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(status_code=422, detail="A imagem está corrompida ou incompleta.") from error
    page.thumbnail((PAGE_MAX_SIDE, PAGE_MAX_SIDE), Image.Resampling.LANCZOS)
    return _clean_webp(page, PAGE_QUALITY)


def strip_webp(webp: bytes, quality: int = 85) -> bytes:
    """Garante WebP sem metadados para imagens já otimizadas pelos serviços de avatar e capa."""
    with Image.open(io.BytesIO(webp)) as image:
        image.load()
        if not any(key in image.info for key in ("exif", "icc_profile", "xmp")):
            return webp
        return _clean_webp(image, quality)


def thumbnail(webp: bytes) -> bytes:
    with Image.open(io.BytesIO(webp)) as image:
        image.load()
        small = image.copy()
    small.thumbnail((THUMB_SIDE, THUMB_SIDE), Image.Resampling.LANCZOS)
    return _clean_webp(small, 70)


# --- gravação, leitura e exclusão ----------------------------------------------------------------


def store(session: Session, *, user_id: str, kind: str, webp: bytes, book_id: int | None = None,
          study_id: int | None = None, status: str = "active") -> EncryptedMedia:
    """Cifra e grava a imagem e a miniatura; a linha fica ``pending`` até os arquivos estarem no disco.

    A miniatura sai pronta aqui porque decodificar uma página grande a cada visita passa do orçamento de
    latência. ``byte_size`` soma os dois arquivos e é reservado na cota (fatia C) antes de gravar; sem espaço,
    levanta ``media_quota.QuotaExceeded`` e nada é gravado. O chamador faz o commit.
    """
    from app.services import media_quota

    state = require_vault(session)
    media_id = uuid.uuid4()
    with Image.open(io.BytesIO(webp)) as image:
        width, height = image.size
    blob = vault.encrypt(state["key"], user_id, media_id, webp, state["epoch"])
    thumb_blob = vault.encrypt(state["key"], user_id, media_id, thumbnail(webp), state["epoch"], THUMB_VARIANT)
    media_quota.reserve(session, user_id, str(media_id), len(blob) + len(thumb_blob))
    row = EncryptedMedia(
        id=str(media_id), user_id=user_id, kind=kind, status="pending", book_id=book_id, study_id=study_id,
        byte_size=len(blob) + len(thumb_blob), plain_size=len(webp), width=width, height=height, content_type="image/webp",
        format_version=vault.FORMAT_VERSION, key_epoch=state["epoch"], sha256=hashlib.sha256(blob).hexdigest(),
    )
    session.add(row)
    session.flush()
    try:
        vault.write_atomic(vault.media_path(state["vault"], media_id), blob)
        vault.write_atomic(vault.thumb_path(state["vault"], media_id), thumb_blob)
    except OSError:
        vault.media_path(state["vault"], media_id).unlink(missing_ok=True)
        session.delete(row)
        session.flush()
        raise
    row.status = status
    session.flush()
    return row


def read(session: Session, row: EncryptedMedia) -> bytes:
    state = require_vault(session)
    path = vault.media_path(state["vault"], uuid.UUID(row.id))
    if not path.is_file():
        raise MediaMissing(row.id)
    try:
        return vault.decrypt(state["key"], row.user_id, uuid.UUID(row.id), path.read_bytes())
    except vault.VaultIntegrityError as error:
        raise MediaIntegrity(row.id) from error


def read_thumbnail(session: Session, row: EncryptedMedia) -> bytes:
    """Miniatura guardada; sem ela (arquivo perdido), é gerada da imagem principal na hora."""
    state = require_vault(session)
    media_id = uuid.UUID(row.id)
    if not vault.media_path(state["vault"], media_id).is_file():
        raise MediaMissing(row.id)
    path = vault.thumb_path(state["vault"], media_id)
    if not path.is_file():
        return thumbnail(read(session, row))
    try:
        return vault.decrypt(state["key"], row.user_id, media_id, path.read_bytes(), THUMB_VARIANT)
    except vault.VaultIntegrityError as error:
        raise MediaIntegrity(row.id) from error


def delete(session: Session, row: EncryptedMedia) -> int:
    """Exclusão em duas fases (``deleting`` → arquivo → linha). Devolve os bytes liberados."""
    freed = row.byte_size
    row.status = "deleting"
    session.flush()
    try:
        folder, media_id = _vault_dir(), uuid.UUID(row.id)
        vault.thumb_path(folder, media_id).unlink(missing_ok=True)
        vault.media_path(folder, media_id).unlink(missing_ok=True)
    except OSError as error:
        logger.warning("cofre: arquivo não removido agora (%s); a linha fica em 'deleting'", type(error).__name__)
        return 0
    session.delete(row)
    session.flush()
    return freed


def by_reference(session: Session, name: str | None) -> EncryptedMedia | None:
    """Mídia referenciada por ``cover_image`` ou pelo fim de ``avatar_url`` (um UUID), se existir."""
    if not name:
        return None
    candidate = name.rsplit("/", 1)[-1]
    if not UUID_RE.match(candidate):
        return None
    return session.get(EncryptedMedia, candidate)


# --- regra de acesso -----------------------------------------------------------------------------


def can_view(session: Session, viewer_id: str | None, row: EncryptedMedia) -> bool:
    """Páginas: só o dono. Avatar: logado e sem bloqueio. Capa: quem pode ler o livro que a usa."""
    if viewer_id is None or row.status not in ("active", "missing"):
        return False
    if viewer_id == row.user_id:
        return True
    if row.kind == "avatar":
        from app.services.friendship_service import is_blocked_between

        return not is_blocked_between(session, viewer_id, row.user_id)
    if row.kind == "cover":
        from app.services.sharing_service import can_read_book

        books = session.query(Book).filter(Book.cover_image == row.id, Book.deleted_at.is_(None)).all()
        return any(can_read_book(session, viewer_id, book) for book in books)
    return False
