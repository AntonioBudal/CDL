"""Mídias cifradas do usuário (feature 090-B): listar, ver, miniatura e apagar.

Toda resposta de imagem é decifrada em memória e nunca guardada em cache. Mídia que o usuário não pode
ver responde 404, para não revelar que existe.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.dependencies import CurrentUser, DatabaseSession
from app.models.book import Book
from app.models.encrypted_media import EncryptedMedia
from app.models.user_profile import UserProfile
from app.services import media_service

router = APIRouter(prefix="/media", tags=["Mídia"])

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


class MediaItemRead(BaseModel):
    id: str
    kind: str
    status: str
    book_id: int | None
    study_id: int | None
    byte_size: int
    width: int
    height: int
    keep_forever: bool
    created_at: str
    expires_at: str | None


@router.get("", summary="Listar as próprias imagens guardadas no cofre")
def list_media(
    current_user: CurrentUser,
    session: DatabaseSession,
    kind: str | None = Query(default=None, pattern="^(notebook_page|avatar|cover)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    query = session.query(EncryptedMedia).filter(
        EncryptedMedia.user_id == current_user.id, EncryptedMedia.status.in_(("active", "missing"))
    )
    if kind:
        query = query.filter(EncryptedMedia.kind == kind)
    rows = query.order_by(EncryptedMedia.created_at.desc(), EncryptedMedia.id).offset(offset).limit(limit + 1).all()
    items = [
        MediaItemRead(
            id=r.id, kind=r.kind, status=r.status, book_id=r.book_id, study_id=r.study_id, byte_size=r.byte_size,
            width=r.width, height=r.height, keep_forever=r.keep_forever, created_at=r.created_at.isoformat(),
            expires_at=r.expires_at.isoformat() if r.expires_at else None,
        ).model_dump()
        for r in rows[:limit]
    ]
    next_offset = offset + limit if len(rows) > limit else None
    return JSONResponse(content={"items": items, "next_offset": next_offset}, headers={"Cache-Control": "no-store"})


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
