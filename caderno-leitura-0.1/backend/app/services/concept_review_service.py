"""F0.11.08 (spec 110): cartões de conceito e conceitos frágeis.

Os cartões vêm do léxico derivado (F0.11.06): todo conceito com ao menos uma definição. A tabela ``concept_reviews``
guarda só a avaliação, pela chave normalizada. A fragilidade é derivada: o maior entre o peso do cartão e a média dos
pesos das perguntas e lacunas avaliadas dos estudos que definem o conceito.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models import Book, Chapter, ConceptReview, Study, StudyHighlight
from app.schemas.review import (
    ConceptCardDefinition,
    ConceptRecordResponse,
    FragileConcept,
    ReviewItemRead,
)
from app.services.concept_lexicon import ConceptEntry, build_lexicon, concept_key
from app.services.persistence import commit_changes
from app.services.review_weights import FRAGILE_WEIGHT, effective_weight, next_weight, queue_key

MAX_DEFINITIONS = 3


@dataclass
class Fragility:
    weight: float
    reason: str  # "card" | "questions"


def _reviews(session: Session, user_id: str) -> dict[str, ConceptReview]:
    rows = session.scalars(select(ConceptReview).where(ConceptReview.user_id == user_id)).all()
    return {row.concept_key: row for row in rows}


def _study_item_weights(session: Session, user_id: str) -> dict[int, list[float]]:
    rows = session.execute(
        select(StudyHighlight.study_id, StudyHighlight.difficulty_weight, StudyHighlight.last_rating)
        .join(Study, StudyHighlight.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            StudyHighlight.user_id == user_id,
            StudyHighlight.kind.in_(["question", "hidden"]),
            StudyHighlight.last_rating.is_not(None),
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
    ).all()
    weights: dict[int, list[float]] = {}
    for study_id, weight, rating in rows:
        value = effective_weight(weight, rating)
        if value is not None:
            weights.setdefault(study_id, []).append(value)
    return weights


def fragility_of(
    entry: ConceptEntry, review: ConceptReview | None, study_weights: dict[int, list[float]]
) -> Fragility | None:
    """Peso do conceito e o motivo; ``None`` se não há nenhuma avaliação ligada a ele."""
    card = review.difficulty_weight if review is not None else None
    items = [w for study_id in {d.study_id for d in entry.definitions} for w in study_weights.get(study_id, [])]
    questions = sum(items) / len(items) if items else None
    if card is None and questions is None:
        return None
    if questions is None or (card is not None and card >= questions):
        return Fragility(weight=float(card), reason="card")
    return Fragility(weight=questions, reason="questions")


def fragility_map(session: Session, user_id: str, lexicon: dict[str, ConceptEntry]) -> dict[str, Fragility]:
    reviews = _reviews(session, user_id)
    study_weights = _study_item_weights(session, user_id)
    result: dict[str, Fragility] = {}
    for key, entry in lexicon.items():
        found = fragility_of(entry, reviews.get(key), study_weights)
        if found is not None:
            result[key] = found
    return result


def fragile_keys(session: Session, user_id: str, lexicon: dict[str, ConceptEntry]) -> set[str]:
    return {key for key, f in fragility_map(session, user_id, lexicon).items() if f.weight >= FRAGILE_WEIGHT}


def fragile_concepts(session: Session, user_id: str, limit: int = 5) -> list[FragileConcept]:
    lexicon = build_lexicon(session, user_id)
    found = [
        FragileConcept(key=key, term=lexicon[key].term, weight=round(f.weight, 3), reason=f.reason)
        for key, f in fragility_map(session, user_id, lexicon).items()
        if f.weight >= FRAGILE_WEIGHT
    ]
    found.sort(key=lambda c: (-c.weight, c.key))
    return found[:limit]


def concept_cards(
    session: Session,
    user_id: str,
    *,
    book_id: int | None = None,
    chapter_id: int | None = None,
    bucket: str | None = None,
    fragile: bool = False,
    limit: int = 10,
) -> list[ReviewItemRead]:
    lexicon = build_lexicon(session, user_id)
    reviews = _reviews(session, user_id)
    weak = fragile_keys(session, user_id, lexicon) if fragile else None
    now = datetime.now(UTC)
    cards: list[tuple[tuple, ConceptEntry, list, ConceptReview | None]] = []
    for key, entry in lexicon.items():
        definitions = [
            d for d in entry.definitions
            if (book_id is None or d.book_id == book_id) and (chapter_id is None or d.chapter_id == chapter_id)
        ]
        if not definitions or (weak is not None and key not in weak):
            continue
        review = reviews.get(key)
        rating = review.last_rating if review else None
        if bucket == "new" and rating is not None:
            continue
        if bucket in ("hard", "medium", "easy") and rating != bucket:
            continue
        sort_key = queue_key(
            review.difficulty_weight if review else None, review.last_reviewed_at if review else None, now, key
        )
        cards.append((sort_key, entry, definitions, review))
    cards.sort(key=lambda c: c[0])

    items: list[ReviewItemRead] = []
    for position, (_, entry, definitions, review) in enumerate(cards[: min(max(1, limit), 50)], start=1):
        first = definitions[0]
        shown = definitions[:MAX_DEFINITIONS]
        items.append(
            ReviewItemRead(
                id=position,
                study_id=first.study_id,
                study_title=first.study_title,
                book_id=first.book_id,
                book_title=first.book_title,
                chapter_id=first.chapter_id,
                chapter_name=first.chapter_name,
                kind="concept",
                section="concepts",
                question_text=f"O que é {entry.term}?",
                expected_answer="\n\n".join(d.text for d in shown),
                last_reviewed_at=review.last_reviewed_at if review else None,
                review_count=review.review_count if review else 0,
                last_rating=review.last_rating if review else None,
                difficulty_weight=review.difficulty_weight if review else None,
                concept_key=entry.key,
                definitions=[
                    ConceptCardDefinition(
                        text=d.text, study_id=d.study_id, study_title=d.study_title, book_title=d.book_title,
                        chapter_name=d.chapter_name,
                    )
                    for d in shown
                ],
            )
        )
    return items


def record_concept_rating(session: Session, user_id: str, key: str, rating: str) -> ConceptRecordResponse:
    if rating not in ("easy", "medium", "hard"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Classificação inválida.")
    normalized = concept_key(key)
    entry = build_lexicon(session, user_id).get(normalized)
    if entry is None or not entry.definitions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conceito não encontrado no seu léxico.")
    review = session.scalar(
        select(ConceptReview).where(ConceptReview.user_id == user_id, ConceptReview.concept_key == normalized)
    )
    if review is None:
        review = ConceptReview(user_id=user_id, concept_key=normalized, review_count=0)
        session.add(review)
    review.last_reviewed_at = utc_now()
    review.review_count = (review.review_count or 0) + 1
    review.last_rating = rating
    review.difficulty_weight = next_weight(review.difficulty_weight, rating)
    commit_changes(session)
    session.refresh(review)
    return ConceptRecordResponse(
        concept_key=review.concept_key,
        last_reviewed_at=review.last_reviewed_at,
        review_count=review.review_count,
        last_rating=review.last_rating,
        difficulty_weight=review.difficulty_weight,
    )


def concept_bucket_counts(
    session: Session, user_id: str, *, book_id: int | None = None, chapter_id: int | None = None
) -> dict[str, int]:
    """Baldes dos cartões de conceito (pela última nota) e quantos foram avaliados hoje."""
    reviews = _reviews(session, user_id)
    counts = {"new": 0, "hard": 0, "medium": 0, "easy": 0, "reviewed_today": 0}
    today = datetime.now(UTC).date()
    for key, entry in build_lexicon(session, user_id).items():
        if not any(
            (book_id is None or d.book_id == book_id) and (chapter_id is None or d.chapter_id == chapter_id)
            for d in entry.definitions
        ):
            continue
        review = reviews.get(key)
        counts[(review.last_rating if review else None) or "new"] += 1
        if review and review.last_reviewed_at and _utc(review.last_reviewed_at).date() == today:
            counts["reviewed_today"] += 1
    return counts


def _utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)
