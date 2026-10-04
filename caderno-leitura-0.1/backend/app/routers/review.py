"""Rotas da API para a Central de Revisão de Perguntas e Clozes."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.review import (
    ReviewItemRead,
    ReviewRecordRequest,
    ReviewRecordResponse,
    ReviewStatsResponse,
)
from app.services.review_service import (
    get_review_items,
    get_review_stats,
    record_review_rating,
)

router = APIRouter(prefix="/review", tags=["Central de Revisão"])


@router.get(
    "/stats",
    response_model=ReviewStatsResponse,
    summary="Estatísticas agregadas da central de revisão",
)
def get_stats(
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return get_review_stats(session=session, user_id=current_user.id)


@router.get(
    "/items",
    response_model=list[ReviewItemRead],
    summary="Listar itens priorizados para a sessão de revisão",
)
def get_items(
    session: DatabaseSession,
    current_user: CurrentUser,
    book_id: int | None = Query(default=None, description="Filtrar por ID do livro"),
    chapter_id: int | None = Query(default=None, description="Filtrar por ID do capítulo"),
    kind: str | None = Query(default=None, description="Filtrar por tipo (question ou hidden)"),
    limit: int = Query(default=10, ge=1, le=50, description="Quantidade de itens no lote"),
):
    return get_review_items(
        session=session,
        user_id=current_user.id,
        book_id=book_id,
        chapter_id=chapter_id,
        kind=kind,
        limit=limit,
    )


@router.post(
    "/items/{highlight_id}/record",
    response_model=ReviewRecordResponse,
    summary="Registrar avaliação e assimilação do item de revisão",
)
def record_rating(
    highlight_id: Identifier,
    payload: ReviewRecordRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return record_review_rating(
        session=session,
        user_id=current_user.id,
        highlight_id=highlight_id,
        rating=payload.rating,
    )
