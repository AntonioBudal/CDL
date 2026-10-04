"""Serviço de agregação, priorização e avaliação para a Central de Revisão."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.study_highlight import StudyHighlight
from app.schemas.review import (
    ReviewBookItem,
    ReviewItemRead,
    ReviewStatsResponse,
)
from app.services.persistence import commit_changes


def get_review_stats(session: Session, user_id: str) -> ReviewStatsResponse:
    """Calcula estatísticas consolidadas de itens de revisão para o usuário ativo."""
    base_filter = [
        StudyHighlight.user_id == user_id,
        StudyHighlight.kind.in_(["question", "hidden"]),
        Study.deleted_at.is_(None),
        Book.deleted_at.is_(None),
    ]

    now = datetime.now(UTC)
    today_start = datetime(now.year, now.month, now.day, tzinfo=UTC)

    stats_stmt = (
        select(
            func.count(StudyHighlight.id).label("total_eligible"),
            func.count(case((StudyHighlight.kind == "question", StudyHighlight.id))).label("total_questions"),
            func.count(case((StudyHighlight.kind == "hidden", StudyHighlight.id))).label("total_hidden"),
            func.count(case((StudyHighlight.last_reviewed_at >= today_start, StudyHighlight.id))).label("reviewed_today"),
        )
        .join(Study, StudyHighlight.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(*base_filter)
    )

    row = session.execute(stats_stmt).one()
    total_eligible = row.total_eligible or 0
    total_questions = row.total_questions or 0
    total_hidden = row.total_hidden or 0
    reviewed_today = row.reviewed_today or 0
    pending_review = max(0, total_eligible - reviewed_today)

    books_stmt = (
        select(
            Book.id,
            Book.title,
            func.count(StudyHighlight.id).label("items_count"),
        )
        .join(Chapter, Chapter.book_id == Book.id)
        .join(Study, Study.chapter_id == Chapter.id)
        .join(StudyHighlight, StudyHighlight.study_id == Study.id)
        .where(*base_filter)
        .group_by(Book.id, Book.title)
        .order_by(Book.title.asc())
    )

    book_rows = session.execute(books_stmt).all()
    books = [
        ReviewBookItem(book_id=b_row.id, title=b_row.title, items_count=b_row.items_count)
        for b_row in book_rows
    ]

    return ReviewStatsResponse(
        total_eligible=total_eligible,
        total_questions=total_questions,
        total_hidden=total_hidden,
        reviewed_today=reviewed_today,
        pending_review=pending_review,
        books=books,
    )


def get_review_items(
    session: Session,
    user_id: str,
    book_id: int | None = None,
    chapter_id: int | None = None,
    kind: str | None = None,
    limit: int = 10,
) -> list[ReviewItemRead]:
    """Retorna itens de estudo priorizados para a sessão de Active Recall."""
    safe_limit = min(max(1, limit), 50)

    filters = [
        StudyHighlight.user_id == user_id,
        Study.deleted_at.is_(None),
        Book.deleted_at.is_(None),
    ]

    if kind in ("question", "hidden"):
        filters.append(StudyHighlight.kind == kind)
    else:
        filters.append(StudyHighlight.kind.in_(["question", "hidden"]))

    if book_id is not None:
        filters.append(Book.id == book_id)
    if chapter_id is not None:
        filters.append(Chapter.id == chapter_id)

    stmt = (
        select(
            StudyHighlight,
            Study.title.label("study_title"),
            Book.id.label("book_id"),
            Book.title.label("book_title"),
            Chapter.id.label("chapter_id"),
            Chapter.name.label("chapter_name"),
        )
        .join(Study, StudyHighlight.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(*filters)
        .order_by(
            case((StudyHighlight.last_reviewed_at.is_(None), 0), else_=1).asc(),
            case((StudyHighlight.last_rating == "hard", 0), else_=1).asc(),
            StudyHighlight.last_reviewed_at.asc(),
            StudyHighlight.id.asc(),
        )
        .limit(safe_limit)
    )

    rows = session.execute(stmt).all()
    items: list[ReviewItemRead] = []

    for row in rows:
        hl = row[0]
        study_title = row.study_title
        b_id = row.book_id
        b_title = row.book_title
        c_id = row.chapter_id
        c_name = row.chapter_name

        if hl.kind == "question":
            q_text = hl.note.strip() if hl.note and hl.note.strip() else "O que este trecho expressa?"
            expected_ans = hl.selected_text
        else:
            prefix_part = hl.prefix.strip() if hl.prefix else ""
            suffix_part = hl.suffix.strip() if hl.suffix else ""
            if prefix_part or suffix_part:
                q_text = f"{prefix_part} [...] {suffix_part}".strip()
            else:
                q_text = "Complete a lacuna: [...]"
            expected_ans = hl.selected_text

        items.append(
            ReviewItemRead(
                id=hl.id,
                study_id=hl.study_id,
                study_title=study_title,
                book_id=b_id,
                book_title=b_title,
                chapter_id=c_id,
                chapter_name=c_name,
                kind=hl.kind,
                section=hl.section,
                question_text=q_text,
                expected_answer=expected_ans,
                context_prefix=hl.prefix or "",
                context_suffix=hl.suffix or "",
                last_reviewed_at=hl.last_reviewed_at,
                review_count=hl.review_count or 0,
                last_rating=hl.last_rating,
            )
        )

    return items


def record_review_rating(
    session: Session,
    user_id: str,
    highlight_id: int,
    rating: str,
) -> StudyHighlight:
    """Registra atomicamente a avaliação atribuída pelo usuário a um item."""
    if rating not in ("easy", "medium", "hard"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Classificação inválida. Deve ser 'easy', 'medium' ou 'hard'.",
        )

    stmt = (
        select(StudyHighlight)
        .join(Study, StudyHighlight.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            StudyHighlight.id == highlight_id,
            StudyHighlight.user_id == user_id,
            StudyHighlight.kind.in_(["question", "hidden"]),
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
    )
    highlight = session.scalar(stmt)
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de estudo não encontrado ou pertence a estudo na lixeira.",
        )

    highlight.last_reviewed_at = utc_now()
    highlight.review_count = (highlight.review_count or 0) + 1
    highlight.last_rating = rating
    commit_changes(session)
    session.refresh(highlight)
    return highlight
