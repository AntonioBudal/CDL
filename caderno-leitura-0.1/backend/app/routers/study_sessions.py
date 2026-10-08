"""Rotas da API para Sessões Estruturadas de Estudo e Auditoria de Aprendizado."""
from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.study_session import (
    StudySessionCompleteRequest,
    StudySessionDetailResponse,
    StudySessionItemAnswerRequest,
    StudySessionItemResponse,
    StudySessionResponse,
    StudySessionStartRequest,
    StudySessionSummaryResponse,
)
from app.services.study_session_service import (
    complete_study_session,
    get_study_session,
    get_study_session_summary,
    get_study_sessions_history,
    interrupt_study_session,
    record_session_item,
    start_study_session,
)

router = APIRouter(prefix="/study-sessions", tags=["Sessões de Estudo"])


@router.post(
    "/start",
    response_model=StudySessionDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar uma nova sessão de estudo com escopo definido",
)
def start_session(
    payload: StudySessionStartRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return start_study_session(
        session=session,
        user_id=current_user.id,
        scope_type=payload.scope_type,
        book_id=payload.book_id,
        limit=payload.limit or 10,
    )


@router.get(
    "/history",
    response_model=list[StudySessionResponse],
    summary="Listar histórico retrospectivo de sessões do usuário",
)
def list_history(
    session: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100, description="Quantidade por página"),
    offset: int = Query(default=0, ge=0, description="Deslocamento para paginação"),
):
    return get_study_sessions_history(
        session=session,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{id}",
    response_model=StudySessionDetailResponse,
    summary="Obter estado detalhado de uma sessão e seus cartões",
)
def get_session(
    id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return get_study_session(
        session=session,
        user_id=current_user.id,
        session_id=id,
    )


@router.post(
    "/{id}/items",
    response_model=StudySessionItemResponse,
    summary="Registrar resposta de um cartão na sessão",
)
def answer_item(
    id: Identifier,
    payload: StudySessionItemAnswerRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return record_session_item(
        session=session,
        user_id=current_user.id,
        session_id=id,
        highlight_id=payload.highlight_id,
        rating=payload.rating,
        time_spent_seconds=payload.time_spent_seconds,
    )


@router.post(
    "/{id}/complete",
    response_model=StudySessionSummaryResponse,
    summary="Concluir formalmente uma sessão de estudo",
)
def complete_session(
    id: Identifier,
    payload: StudySessionCompleteRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return complete_study_session(
        session=session,
        user_id=current_user.id,
        session_id=id,
        duration_seconds=payload.duration_seconds,
    )


@router.post(
    "/{id}/interrupt",
    response_model=StudySessionResponse,
    summary="Interromper uma sessão em andamento preservando respostas",
)
def interrupt_session(
    id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return interrupt_study_session(
        session=session,
        user_id=current_user.id,
        session_id=id,
    )


@router.get(
    "/{id}/summary",
    response_model=StudySessionSummaryResponse,
    summary="Obter resumo e feedback cognitivo da sessão",
)
def get_summary(
    id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return get_study_session_summary(
        session=session,
        user_id=current_user.id,
        session_id=id,
    )
