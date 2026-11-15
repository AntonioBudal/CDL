"""Rotas da API para a Central de Revisão de Perguntas e Clozes."""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.review import (
    ConceptRecordResponse,
    ReviewBookItem,
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
from app.services.image_occlusion_service import (
    image_bucket_counts,
    image_cards,
    image_counts_by_book,
    record_image_rating,
)
from app.services.review_service import (
    get_review_items,
    get_review_stats,
    record_review_rating,
)
from app.services.review_weights import effective_weight, queue_key

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
    kind: str | None = Query(default=None, description="Filtra só a contagem dos baldes (question, hidden, concept ou image)"),
):
    stats = get_review_stats(
        session=session,
        user_id=current_user.id,
        book_id=book_id,
        chapter_id=chapter_id,
        kind=None if kind in ("concept", "image") else kind,
    )
    # F0.12.06: cartões de imagem entram nos totais, nos livros e (em "Todos" ou "Imagens") nos baldes
    images = image_bucket_counts(session, current_user.id, book_id=book_id, chapter_id=chapter_id)
    images.pop("reviewed_today")
    all_images = image_bucket_counts(session, current_user.id)
    images_today = all_images.pop("reviewed_today")
    stats.total_images = sum(all_images.values())
    stats.total_eligible += stats.total_images
    stats.reviewed_today += images_today
    stats.pending_review = max(0, stats.total_eligible - stats.reviewed_today)
    by_book = {item.book_id: item for item in stats.books}
    for b_id, (title, count) in image_counts_by_book(session, current_user.id).items():
        if b_id in by_book:
            by_book[b_id].items_count += count
        else:
            stats.books.append(ReviewBookItem(book_id=b_id, title=title, items_count=count))
    stats.books.sort(key=lambda item: item.title)
    if kind == "image":
        stats.buckets = ReviewBucketCounts(**images)
        stats.total_eligible = sum(images.values())
        stats.reviewed_today = images_today
        stats.pending_review = max(0, stats.total_eligible - images_today)
    elif kind is None:
        merged = stats.buckets.model_dump()
        stats.buckets = ReviewBucketCounts(**{key: merged[key] + images[key] for key in images})
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
    kind: str | None = Query(default=None, description="Filtrar por tipo (question, hidden, concept ou image)"),
    limit: int = Query(default=10, ge=1, le=50, description="Quantidade de itens no lote"),
    bucket: ReviewBucket | None = Query(default=None, description="Só itens de um balde: new, hard, medium ou easy"),
    fragile: bool = Query(default=False, description="Só conceitos frágeis (com kind=concept)"),
):
    if kind == "concept":  # F0.11.08: cartões de conceito
        return concept_cards(
            session, current_user.id, book_id=book_id, chapter_id=chapter_id, bucket=bucket, fragile=fragile,
            limit=limit,
        )
    if kind == "image":  # F0.12.06: cartões de imagem
        return image_cards(session, current_user.id, book_id=book_id, chapter_id=chapter_id, bucket=bucket, limit=limit)
    items = get_review_items(
        session=session,
        user_id=current_user.id,
        book_id=book_id,
        chapter_id=chapter_id,
        kind=kind,
        limit=limit,
        bucket=bucket,
    )
    if kind is not None:
        return items
    # "Todos": perguntas, lacunas e cartões de imagem numa fila só, pela mesma ordem de prioridade.
    items += image_cards(session, current_user.id, book_id=book_id, chapter_id=chapter_id, bucket=bucket, limit=limit)
    now = datetime.now(UTC)
    items.sort(key=lambda item: queue_key(
        effective_weight(item.difficulty_weight, item.last_rating), item.last_reviewed_at, now, (item.kind, item.id)
    ))
    return items[: min(max(1, limit), 50)]


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


@router.post(
    "/images/{card_id}/record",
    response_model=ReviewRecordResponse,
    summary="Registrar avaliação de um cartão de imagem (F0.12.06)",
)
def record_image(card_id: Identifier, payload: ReviewRecordRequest, session: DatabaseSession, current_user: CurrentUser):
    return record_image_rating(session, current_user.id, card_id, payload.rating)


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
