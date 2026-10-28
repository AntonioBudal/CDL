"""Mídias cifradas do usuário (features 090-B e C): uso, listar, ver, manter, apagar e fotos do estudo.

Toda resposta de imagem é decifrada em memória e nunca guardada em cache. Mídia que o usuário não pode
ver responde 404, para não revelar que existe.
"""

from __future__ import annotations

import math
from datetime import timedelta
from typing import Literal

from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator

from app.core.config import get_media_completed_grace_days, get_media_delete_on_completed, get_media_retention_days
from app.db.types import utc_now
from app.dependencies import CurrentUser, DatabaseSession
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.encrypted_media import EncryptedMedia
from app.models.study import Study
from app.models.user_profile import UserProfile
from app.services import media_quota, media_service

router = APIRouter(prefix="/media", tags=["Mídia"])

LIVE = ("active", "missing")

IMAGE_HEADERS = {
    "Cache-Control": "private, no-store, no-cache, max-age=0",
    "Pragma": "no-cache",
    "X-Content-Type-Options": "nosniff",
    "Content-Disposition": "inline",
}
VAULT_MESSAGES = {
    "key_missing": "O cofre de imagens está trancado: a chave não está instalada neste computador.",
    "key_mismatch": "O cofre de imagens está trancado: a chave instalada não é a deste acervo.",
    "storage_unavailable": "O cofre de imagens não está disponível: confira o HD de armazenamento.",
}


def error_response(status: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"detail": detail, "code": code}, headers={"Cache-Control": "no-store"})


def media_response(session, row: EncryptedMedia, *, thumb: bool = False) -> Response:
    """Decifra e devolve a imagem, ou o erro do contrato (503 trancado, 409 ausente, 422 adulterado)."""
    try:
        data = media_service.read_thumbnail(session, row) if thumb else media_service.read(session, row)
    except media_service.VaultLocked as locked:
        return error_response(503, "vault_locked", VAULT_MESSAGES.get(locked.state, VAULT_MESSAGES["key_missing"]))
    except media_service.MediaMissing:
        return error_response(409, "missing", "O arquivo desta imagem não foi encontrado no cofre.")
    except media_service.MediaIntegrity:
        return error_response(422, "integrity_failed", "O arquivo desta imagem está danificado.")
    return Response(content=data, media_type="image/webp", headers=IMAGE_HEADERS)


def visible_or_404(session, current_user, media_id: str) -> EncryptedMedia:
    row = media_service.by_reference(session, media_id)
    if row is None or not media_service.can_view(session, current_user.id, row):
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return row


def media_items(session, rows: list[EncryptedMedia]) -> list[dict]:
    """Itens da lista com livro, estudo e dias até sair, sem uma consulta por item."""
    from app.services.media_retention import effective_expiry

    book_ids = {row.book_id for row in rows if row.book_id}
    study_ids = {row.study_id for row in rows if row.study_id}
    books = {book.id: book for book in session.query(Book).filter(Book.id.in_(book_ids)).all()} if book_ids else {}
    studies = (
        {study.id: study for study in session.query(Study).filter(Study.id.in_(study_ids)).all()} if study_ids else {}
    )
    grace = get_media_completed_grace_days()
    on_completed = get_media_delete_on_completed()
    now = utc_now()
    items = []
    for row in rows:
        book, study = books.get(row.book_id), studies.get(row.study_id)
        expiry = effective_expiry(row, grace_days=grace, delete_on_completed=on_completed)
        items.append({
            "id": row.id,
            "kind": row.kind,
            "status": row.status,
            "book": {"id": book.id, "title": book.title, "in_trash": book.deleted_at is not None} if book else None,
            "study": (
                {"id": study.id, "title": study.title, "reading_status": study.reading_status,
                 "in_trash": study.deleted_at is not None}
                if study else None
            ),
            "byte_size": row.byte_size,
            "width": row.width,
            "height": row.height,
            "keep_forever": row.keep_forever,
            "created_at": row.created_at.isoformat(),
            "expires_at": expiry.isoformat() if expiry else None,
            "days_left": max(0, math.ceil((expiry - now).total_seconds() / 86400)) if expiry else None,
        })
    return items


def no_store(content, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=content, headers={"Cache-Control": "no-store"})


def usage_for(session, current_user) -> dict:
    current = media_quota.usage(session, current_user.id)
    return media_quota.view_for(current, is_admin=current_user.role == "admin")


@router.get("/usage", summary="Uso do espaço de imagens (cota) e estado do cofre")
def media_usage(current_user: CurrentUser, session: DatabaseSession):
    return no_store({**usage_for(session, current_user), "vault": {"state": media_service.peek_status(session)}})


SORTS = {
    "created_desc": (EncryptedMedia.created_at.desc(), EncryptedMedia.id),
    "size_desc": (EncryptedMedia.byte_size.desc(), EncryptedMedia.id),
    "expires_asc": (EncryptedMedia.expires_at.is_(None), EncryptedMedia.expires_at.asc(), EncryptedMedia.id),
}


@router.get("", summary="Listar as próprias imagens guardadas no cofre")
def list_media(
    current_user: CurrentUser,
    session: DatabaseSession,
    kind: str | None = Query(default=None, pattern="^(notebook_page|avatar|cover)$"),
    book_id: int | None = Query(default=None, ge=1),
    sort: str = Query(default="created_desc", pattern="^(created_desc|size_desc|expires_asc)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    query = session.query(EncryptedMedia).filter(
        EncryptedMedia.user_id == current_user.id, EncryptedMedia.status.in_(LIVE)
    )
    if kind:
        query = query.filter(EncryptedMedia.kind == kind)
    if book_id:
        query = query.filter(EncryptedMedia.book_id == book_id)
    rows = query.order_by(*SORTS[sort]).offset(offset).limit(limit + 1).all()
    next_offset = offset + limit if len(rows) > limit else None
    return no_store({"items": media_items(session, rows[:limit]), "next_offset": next_offset})


@router.get("/{media_id}/content", summary="Ver uma imagem (decifrada em memória)")
def media_content(media_id: str, current_user: CurrentUser, session: DatabaseSession):
    return media_response(session, visible_or_404(session, current_user, media_id))


@router.get("/{media_id}/thumbnail", summary="Miniatura de uma imagem (até 320 px)")
def media_thumbnail(media_id: str, current_user: CurrentUser, session: DatabaseSession):
    return media_response(session, visible_or_404(session, current_user, media_id), thumb=True)


@router.delete("/{media_id}", summary="Apagar uma imagem própria")
def delete_media(media_id: str, current_user: CurrentUser, session: DatabaseSession):
    row = media_service.by_reference(session, media_id)
    if row is None or row.user_id != current_user.id or row.status == "deleting":
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    # Só a referência some: o livro e o perfil continuam (sem capa ou sem avatar).
    if row.kind == "cover":
        for book in session.query(Book).filter(Book.cover_image == row.id).all():
            book.cover_image = None
    if row.kind == "avatar":
        for profile in session.query(UserProfile).filter(UserProfile.avatar_url == f"/api/avatars/{row.id}").all():
            profile.avatar_url = None
    freed = media_service.delete(session, row)
    session.commit()
    return JSONResponse(content={"freed_bytes": freed}, headers={"Cache-Control": "no-store"})


def own_page_or_404(session, current_user, media_id: str) -> EncryptedMedia:
    row = media_service.by_reference(session, media_id)
    if row is None or row.user_id != current_user.id or row.kind != "notebook_page" or row.status not in LIVE:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return row


class KeepRequest(BaseModel):
    keep_forever: bool


@router.patch("/{media_id}", summary="Manter uma foto de página permanentemente, ou voltar a expirar")
def set_keep_forever(media_id: str, payload: KeepRequest, current_user: CurrentUser, session: DatabaseSession):
    row = own_page_or_404(session, current_user, media_id)
    row.keep_forever = payload.keep_forever
    row.completed_seen_at = None
    row.expires_at = None if payload.keep_forever else utc_now() + timedelta(days=get_media_retention_days())
    session.commit()
    return no_store(media_items(session, [row])[0])


class BulkDeleteRequest(BaseModel):
    filter: Literal["completed_studies", "older_than_days"] | None = None
    days: int | None = Field(default=None, ge=1, le=3650)
    ids: list[str] | None = Field(default=None, min_length=1, max_length=500)
    dry_run: bool = True

    @model_validator(mode="after")
    def one_selection(self):
        if (self.filter is None) == (self.ids is None):
            raise ValueError("Informe um filtro ou uma lista de imagens, não os dois.")
        if self.filter == "older_than_days" and self.days is None:
            raise ValueError("Informe quantos dias.")
        return self


@router.post("/bulk-delete", summary="Apagar fotos de páginas em lote, com prévia")
def bulk_delete(payload: BulkDeleteRequest, current_user: CurrentUser, session: DatabaseSession):
    query = session.query(EncryptedMedia).filter(
        EncryptedMedia.user_id == current_user.id,
        EncryptedMedia.kind == "notebook_page",
        EncryptedMedia.status.in_(LIVE),
    )
    if payload.ids is not None:
        query = query.filter(EncryptedMedia.id.in_(payload.ids))
    else:
        # "Manter permanentemente" fica fora dos filtros; o lote de concluídos não espera os 7 dias (C-Q3).
        query = query.filter(EncryptedMedia.keep_forever.is_(False))
        if payload.filter == "completed_studies":
            query = query.join(Study, Study.id == EncryptedMedia.study_id).filter(Study.reading_status == "concluido")
        else:
            query = query.filter(EncryptedMedia.created_at <= utc_now() - timedelta(days=payload.days))
    rows = query.all()
    if payload.dry_run:
        return no_store({"matched": len(rows), "freed_bytes": sum(row.byte_size for row in rows), "deleted": 0})
    deleted = freed = 0
    for row in rows:
        released = media_service.delete(session, row)
        if released:
            deleted += 1
            freed += released
    session.commit()
    return no_store({"matched": len(rows), "freed_bytes": freed, "deleted": deleted})


# --- Fotos de conferência de um estudo (feature 090-C) ------------------------------------------

study_router = APIRouter(prefix="/studies", tags=["Mídia"])


@study_router.post("/{study_id}/media", status_code=201, summary="Guardar a foto da página com o estudo")
async def store_study_photo(
    study_id: int,
    current_user: CurrentUser,
    session: DatabaseSession,
    file: UploadFile = File(...),
):
    from app.services.digitize_service import DigitizeError, read_upload_limited

    study = session.get(Study, study_id)
    if study is None or study.user_id != current_user.id or study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    try:
        data = await read_upload_limited(file, media_service.PAGE_MAX_BYTES)
    except DigitizeError as error:
        return error_response(error.status, error.code, error.detail)
    webp = await run_in_threadpool(media_service.prepare_page, data)
    chapter = session.get(Chapter, study.chapter_id)
    row = media_service.store(
        session, user_id=current_user.id, kind="notebook_page", webp=webp,
        book_id=chapter.book_id if chapter else None, study_id=study.id,
    )
    row.expires_at = utc_now() + timedelta(days=get_media_retention_days())
    session.commit()
    return no_store({"item": media_items(session, [row])[0], "usage": usage_for(session, current_user)}, 201)


@study_router.get("/{study_id}/media", summary="Fotos de conferência guardadas com o estudo")
def list_study_photos(study_id: int, current_user: CurrentUser, session: DatabaseSession):
    study = session.get(Study, study_id)
    if study is None or study.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    rows = (
        session.query(EncryptedMedia)
        .filter(EncryptedMedia.study_id == study.id, EncryptedMedia.kind == "notebook_page",
                EncryptedMedia.status.in_(LIVE))
        .order_by(EncryptedMedia.created_at, EncryptedMedia.id)
        .all()
    )
    return no_store({"items": media_items(session, rows)})
