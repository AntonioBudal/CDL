"""Roteador para a Caixa de Entrada de Capturas (Inbox de Conhecimento)."""
from __future__ import annotations

import json

from fastapi import APIRouter, File, Form, HTTPException, Query, Response, UploadFile, status
from pydantic import TypeAdapter, ValidationError

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.inbox_capture import (
    InboxBookTrayResponse,
    InboxCaptureCreate,
    InboxCapturePatch,
    InboxCaptureRead,
    InboxCountResponse,
    InboxLinkRequest,
    InboxPromoteRequest,
)
from app.services.inbox_service import (
    count_inbox_captures,
    create_inbox_capture,
    delete_inbox_capture,
    get_book_tray,
    get_inbox_capture,
    link_inbox_capture,
    list_inbox_captures,
    promote_inbox_capture,
    update_inbox_capture,
    _build_read_model,
)

router = APIRouter(prefix="/inbox", tags=["Caixa de Entrada de Capturas (Inbox)"])


# --- F0.11.03: destaques do Kindle e do Kobo -------------------------------------------------------------------------

from app.schemas.ereader_import import EreaderChoice, EreaderImportResponse, EreaderPreviewResponse  # noqa: E402
from app.services.ereader_import.service import (  # noqa: E402
    KOBO_MAX_BYTES,
    build_preview,
    parse_upload,
    run_import,
)

_CHOICES = TypeAdapter(list[EreaderChoice])


async def _read_upload(upload: UploadFile) -> bytes:
    """Lê em blocos de 1 MB e recusa acima do maior limite (Kobo); o limite do Kindle é conferido no serviço."""
    chunks: list[bytes] = []
    size = 0
    while chunk := await upload.read(1024 * 1024):
        size += len(chunk)
        if size > KOBO_MAX_BYTES:
            raise HTTPException(status_code=413, detail="O arquivo passa de 200 MB.")
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/ereader/preview", response_model=EreaderPreviewResponse, summary="Prévia de destaques do Kindle ou Kobo")
async def ereader_preview_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    """Só lê o arquivo: nada é gravado e o arquivo não fica no disco."""
    parsed = parse_upload(await _read_upload(file))
    return build_preview(session, current_user.id, parsed)


@router.post("/ereader/import", response_model=EreaderImportResponse, summary="Importar destaques do Kindle ou Kobo")
async def ereader_import_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    choices: str = Form(..., description="JSON: lista de {key, action: existing|create|skip, book_id}"),
):
    try:
        parsed_choices = _CHOICES.validate_python(json.loads(choices))
    except (ValueError, ValidationError) as exc:
        raise HTTPException(status_code=422, detail="Escolhas inválidas para a importação.") from exc
    parsed = parse_upload(await _read_upload(file))
    return run_import(session, current_user.id, parsed, parsed_choices)


@router.get("", response_model=list[InboxCaptureRead], summary="Listar capturas do usuário")
def list_captures_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
    status_filter: str | None = Query(default="inbox", alias="status", description="Filtro de status"),
    q: str | None = Query(default=None, description="Termo de busca textual"),
    book_id: int | None = Query(default=None, gt=0, description="Filtrar por livro associado"),
    chapter_id: int | None = Query(default=None, gt=0, description="Filtrar por capítulo (F0.11.02)"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return list_inbox_captures(
        session=session,
        user_id=current_user.id,
        status_filter=status_filter,
        q=q,
        book_id=book_id,
        limit=limit,
        offset=offset,
        chapter_id=chapter_id,
    )


@router.get("/book-tray", response_model=InboxBookTrayResponse, summary="Capturas pendentes de um livro por capítulo")
def book_tray_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
    book_id: int = Query(..., gt=0, description="Livro"),
):
    return get_book_tray(session=session, user_id=current_user.id, book_id=book_id)


@router.get("/count", response_model=InboxCountResponse, summary="Obter contagem de itens pendentes no Inbox")
def count_captures_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return count_inbox_captures(session=session, user_id=current_user.id)


@router.post("", response_model=InboxCaptureRead, status_code=status.HTTP_201_CREATED, summary="Criar nova captura rápida")
def create_capture_endpoint(
    payload: InboxCaptureCreate,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return create_inbox_capture(session=session, user_id=current_user.id, payload=payload)


@router.get("/{capture_id}", response_model=InboxCaptureRead, summary="Obter detalhes de uma captura")
def get_capture_endpoint(
    capture_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    capture = get_inbox_capture(session=session, user_id=current_user.id, capture_id=capture_id)
    return _build_read_model(capture)


@router.patch("/{capture_id}", response_model=InboxCaptureRead, summary="Atualizar captura")
def update_capture_endpoint(
    capture_id: Identifier,
    payload: InboxCapturePatch,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return update_inbox_capture(
        session=session,
        user_id=current_user.id,
        capture_id=capture_id,
        payload=payload,
    )


@router.delete("/{capture_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir captura")
def delete_capture_endpoint(
    capture_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    delete_inbox_capture(session=session, user_id=current_user.id, capture_id=capture_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{capture_id}/promote", response_model=InboxCaptureRead, summary="Promover captura para estudo")
def promote_capture_endpoint(
    capture_id: Identifier,
    payload: InboxPromoteRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return promote_inbox_capture(
        session=session,
        user_id=current_user.id,
        capture_id=capture_id,
        study_id=payload.study_id,
    )


@router.post("/{capture_id}/link", response_model=InboxCaptureRead, summary="Vincular captura a estudo existente")
def link_capture_endpoint(
    capture_id: Identifier,
    payload: InboxLinkRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return link_inbox_capture(
        session=session,
        user_id=current_user.id,
        capture_id=capture_id,
        target_study_id=payload.target_study_id,
        target_section=payload.target_section,
    )
