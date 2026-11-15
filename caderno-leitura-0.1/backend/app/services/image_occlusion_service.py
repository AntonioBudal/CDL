"""F0.12.06 (spec 119): oclusão de imagem — retângulos sobre uma imagem do estudo viram cartões de revisão.

A imagem é uma foto do estudo guardada no cofre (``notebook_page``). Salvar é em lote: o editor manda a lista inteira;
quem tem id é atualizado (mantém o histórico), quem não tem é criado e quem sumiu é apagado. Uma foto com cartões passa
a "manter para sempre", senão o cartão perderia a imagem quando o estudo fosse concluído.
"""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models import Book, Chapter, EncryptedMedia, ImageOcclusionCard, Study
from app.schemas.review import OcclusionRegion, ReviewItemRead
from app.services.persistence import commit_changes
from app.services.review_weights import effective_weight, next_weight, queue_key

MAX_CARDS = 50
MIN_SIDE = 0.01
MAX_LABEL = 200
LIVE = ("active", "missing")
QUESTION = "O que está na área destacada?"


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def normalize_box(x: float, y: float, width: float, height: float) -> tuple[float, float, float, float]:
    """Recorta o retângulo aos limites da imagem; lado menor que 1% é recusado."""
    left, top = _clamp(x), _clamp(y)
    right, bottom = _clamp(float(x) + float(width)), _clamp(float(y) + float(height))
    if right - left < MIN_SIDE or bottom - top < MIN_SIDE:
        raise HTTPException(status_code=422, detail="Área pequena demais ou fora da imagem.")
    return round(left, 6), round(top, 6), round(right - left, 6), round(bottom - top, 6)


def own_study_image(session: Session, user_id: str, study_id: int, media_id: str) -> tuple[Study, EncryptedMedia]:
    study = session.get(Study, study_id)
    if study is None or study.user_id != user_id or study.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudo não encontrado.")
    media = session.get(EncryptedMedia, media_id)
    if (
        media is None or media.user_id != user_id or media.study_id != study.id
        or media.kind != "notebook_page" or media.status not in LIVE
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagem não encontrada.")
    return study, media


def _cards_of(session: Session, media_id: str) -> list[ImageOcclusionCard]:
    return list(session.scalars(
        select(ImageOcclusionCard).where(ImageOcclusionCard.media_id == media_id)
        .order_by(ImageOcclusionCard.position, ImageOcclusionCard.id)
    ).all())


def card_payload(card: ImageOcclusionCard) -> dict:
    return {
        "id": card.id, "x": card.x, "y": card.y, "width": card.width, "height": card.height, "label": card.label,
        "position": card.position, "review_count": card.review_count, "last_rating": card.last_rating,
    }


def occlusion_view(session: Session, media: EncryptedMedia) -> dict:
    return {
        "media": {"id": media.id, "width": media.width, "height": media.height, "keep_forever": media.keep_forever},
        "cards": [card_payload(card) for card in _cards_of(session, media.id)],
    }


def get_occlusions(session: Session, user_id: str, study_id: int, media_id: str) -> dict:
    _, media = own_study_image(session, user_id, study_id, media_id)
    return occlusion_view(session, media)


def save_occlusions(session: Session, user_id: str, study_id: int, media_id: str, boxes: list[dict]) -> dict:
    study, media = own_study_image(session, user_id, study_id, media_id)
    if len(boxes) > MAX_CARDS:
        raise HTTPException(
            status_code=422, detail=f"No máximo {MAX_CARDS} áreas por imagem."
        )
    existing = {card.id: card for card in _cards_of(session, media.id)}
    kept: set[int] = set()
    for position, box in enumerate(boxes):
        x, y, width, height = normalize_box(box["x"], box["y"], box["width"], box["height"])
        label = (box.get("label") or "").strip()[:MAX_LABEL]
        card_id = box.get("id")
        if card_id is not None:
            card = existing.get(card_id)
            if card is None or card_id in kept:
                raise HTTPException(status_code=422, detail="Área desconhecida.")
            kept.add(card_id)
        else:
            card = ImageOcclusionCard(user_id=user_id, study_id=study.id, media_id=media.id, review_count=0)
            session.add(card)
        card.x, card.y, card.width, card.height = x, y, width, height
        card.label = label
        card.position = position
    for card_id, card in existing.items():
        if card_id not in kept:
            session.delete(card)
    if boxes and not media.keep_forever:
        media.keep_forever = True
        media.completed_seen_at = None
        media.expires_at = None
    commit_changes(session)
    return occlusion_view(session, media)


def count_by_media(session: Session, media_ids: list[str]) -> dict[str, int]:
    if not media_ids:
        return {}
    rows = session.execute(
        select(ImageOcclusionCard.media_id, func.count(ImageOcclusionCard.id))
        .where(ImageOcclusionCard.media_id.in_(media_ids))
        .group_by(ImageOcclusionCard.media_id)
    ).all()
    return {media_id: count for media_id, count in rows}


# --- Revisão ------------------------------------------------------------------------------------------------------


def _scope(user_id: str, book_id: int | None, chapter_id: int | None) -> list:
    filters = [
        ImageOcclusionCard.user_id == user_id,
        Study.deleted_at.is_(None),
        Book.deleted_at.is_(None),
        EncryptedMedia.status.in_(LIVE),
    ]
    if book_id is not None:
        filters.append(Book.id == book_id)
    if chapter_id is not None:
        filters.append(Chapter.id == chapter_id)
    return filters


def _rows(session: Session, user_id: str, book_id: int | None, chapter_id: int | None):
    return session.execute(
        select(ImageOcclusionCard, Study.title, Book.id, Book.title, Chapter.id, Chapter.name)
        .join(Study, ImageOcclusionCard.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .join(EncryptedMedia, ImageOcclusionCard.media_id == EncryptedMedia.id)
        .where(*_scope(user_id, book_id, chapter_id))
    ).all()


def image_cards(
    session: Session,
    user_id: str,
    *,
    book_id: int | None = None,
    chapter_id: int | None = None,
    bucket: str | None = None,
    limit: int = 10,
) -> list[ReviewItemRead]:
    rows = _rows(session, user_id, book_id, chapter_id)
    regions: dict[str, list[OcclusionRegion]] = {}
    for row in sorted(rows, key=lambda r: (r[0].position, r[0].id)):
        card = row[0]
        regions.setdefault(card.media_id, []).append(
            OcclusionRegion(id=card.id, x=card.x, y=card.y, width=card.width, height=card.height)
        )
    if bucket == "new":
        rows = [r for r in rows if r[0].last_rating is None]
    elif bucket in ("hard", "medium", "easy"):
        rows = [r for r in rows if r[0].last_rating == bucket]
    now = datetime.now(UTC)
    rows = sorted(
        rows,
        key=lambda r: queue_key(effective_weight(r[0].difficulty_weight, r[0].last_rating), r[0].last_reviewed_at,
                                now, r[0].id),
    )[: min(max(1, limit), 50)]
    items: list[ReviewItemRead] = []
    for card, study_title, b_id, b_title, c_id, c_name in rows:
        items.append(ReviewItemRead(
            id=card.id,
            study_id=card.study_id,
            study_title=study_title,
            book_id=b_id,
            book_title=b_title,
            chapter_id=c_id,
            chapter_name=c_name,
            kind="image",
            section="image",
            question_text=QUESTION,
            expected_answer=card.label,
            last_reviewed_at=card.last_reviewed_at,
            review_count=card.review_count or 0,
            last_rating=card.last_rating,
            difficulty_weight=card.difficulty_weight,
            media_id=card.media_id,
            occlusion_id=card.id,
            regions=regions.get(card.media_id, []),
        ))
    return items


def image_bucket_counts(
    session: Session, user_id: str, *, book_id: int | None = None, chapter_id: int | None = None
) -> dict[str, int]:
    counts = {"new": 0, "hard": 0, "medium": 0, "easy": 0, "reviewed_today": 0}
    today = datetime.now(UTC).date()
    for row in _rows(session, user_id, book_id, chapter_id):
        card = row[0]
        counts[card.last_rating or "new"] += 1
        if card.last_reviewed_at is not None:
            stamp = card.last_reviewed_at if card.last_reviewed_at.tzinfo else card.last_reviewed_at.replace(tzinfo=UTC)
            if stamp.date() == today:
                counts["reviewed_today"] += 1
    return counts


def image_counts_by_book(session: Session, user_id: str) -> dict[int, tuple[str, int]]:
    result: dict[int, tuple[str, int]] = {}
    for _, _, b_id, b_title, _, _ in _rows(session, user_id, None, None):
        title, count = result.get(b_id, (b_title, 0))
        result[b_id] = (title, count + 1)
    return result


def record_image_rating(session: Session, user_id: str, card_id: int, rating: str) -> dict:
    if rating not in ("easy", "medium", "hard"):
        raise HTTPException(status_code=422, detail="Classificação inválida.")
    card = session.scalar(
        select(ImageOcclusionCard)
        .join(Study, ImageOcclusionCard.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(ImageOcclusionCard.id == card_id, ImageOcclusionCard.user_id == user_id,
               Study.deleted_at.is_(None), Book.deleted_at.is_(None))
    )
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cartão de imagem não encontrado.")
    card.last_reviewed_at = utc_now()
    card.review_count = (card.review_count or 0) + 1
    card.difficulty_weight = next_weight(effective_weight(card.difficulty_weight, card.last_rating), rating)
    card.last_rating = rating
    commit_changes(session)
    session.refresh(card)
    return {
        "id": card.id, "last_reviewed_at": card.last_reviewed_at, "review_count": card.review_count,
        "last_rating": card.last_rating,
    }
