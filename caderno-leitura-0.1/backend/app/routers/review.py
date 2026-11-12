"""Rotas da API para a Central de Revisão de Perguntas e Clozes."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.review import (
    ConceptRecordResponse,
    FragileConcept,
    ReviewBucket,
    ReviewBucketCounts,
    ReviewItemRead,
    ReviewRecordRequest,
    ReviewRecordResponse,
    ReviewStatsResponse,
)
from app.services.concept_review_service import (
    concept_bucket_counts,
    concept_cards,
    fragile_concepts,
    record_concept_rating,
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
    book_id: int | None = Query(default=None, description="Filtra só a contagem dos baldes"),
    chapter_id: int | None = Query(default=None, description="Filtra só a contagem dos baldes"),
    kind: str | None = Query(default=None, description="Filtra só a contagem dos baldes (question, hidden ou concept)"),
):
    stats = get_review_stats(
        session=session,
        user_id=current_user.id,
        book_id=book_id,
        chapter_id=chapter_id,
        kind=None if kind == "concept" else kind,
    )
    if kind == "concept":  # F0.11.08: com "Conceitos", baldes e totais são dos cartões de conceito
        counts = concept_bucket_counts(session, current_user.id, book_id=book_id, chapter_id=chapter_id)
        reviewed_today = counts.pop("reviewed_today")
        stats.buckets = ReviewBucketCounts(**counts)
        stats.total_eligible = sum(counts.values())
        stats.reviewed_today = reviewed_today
        stats.pending_review = max(0, stats.total_eligible - reviewed_today)
    return stats


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
    kind: str | None = Query(default=None, description="Filtrar por tipo (question, hidden ou concept)"),
    limit: int = Query(default=10, ge=1, le=50, description="Quantidade de itens no lote"),
    bucket: ReviewBucket | None = Query(default=None, description="Só itens de um balde: new, hard, medium ou easy"),
    fragile: bool = Query(default=False, description="Só conceitos frágeis (com kind=concept)"),
):
    if kind == "concept":  # F0.11.08: cartões de conceito
        return concept_cards(
            session, current_user.id, book_id=book_id, chapter_id=chapter_id, bucket=bucket, fragile=fragile,
            limit=limit,
        )
    return get_review_items(
        session=session,
        user_id=current_user.id,
        book_id=book_id,
        chapter_id=chapter_id,
        kind=kind,
        limit=limit,
        bucket=bucket,
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


@router.post(
    "/concepts/{key}/record",
    response_model=ConceptRecordResponse,
    summary="Registrar avaliação de um cartão de conceito (F0.11.08)",
)
def record_concept(key: str, payload: ReviewRecordRequest, session: DatabaseSession, current_user: CurrentUser):
    return record_concept_rating(session, current_user.id, key, payload.rating)


@router.get(
    "/fragile-concepts",
    response_model=list[FragileConcept],
    summary="Conceitos frágeis do leitor (F0.11.08)",
)
def list_fragile_concepts(
    session: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=5, ge=1, le=50),
):
    return fragile_concepts(session, current_user.id, limit)
