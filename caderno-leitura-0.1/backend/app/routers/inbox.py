"""Roteador para a Caixa de Entrada de Capturas (Inbox de Conhecimento)."""
from __future__ import annotations

from fastapi import APIRouter, Query, Response, status

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.inbox_capture import (
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
    get_inbox_capture,
    link_inbox_capture,
    list_inbox_captures,
    promote_inbox_capture,
    update_inbox_capture,
    _build_read_model,
)

router = APIRouter(prefix="/inbox", tags=["Caixa de Entrada de Capturas (Inbox)"])


@router.get("", response_model=list[InboxCaptureRead], summary="Listar capturas do usuário")
def list_captures_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
    status_filter: str | None = Query(default="inbox", alias="status", description="Filtro de status"),
    q: str | None = Query(default=None, description="Termo de busca textual"),
    book_id: int | None = Query(default=None, gt=0, description="Filtrar por livro associado"),
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
    )


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
