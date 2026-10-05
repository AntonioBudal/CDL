"""Serviço para gestão de destaques e anotações contextuais de estudos."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import case, func, or_, select

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.study_highlight import StudyHighlight
from app.schemas.study_highlight import (
    HighlightLibraryFilterOption,
    HighlightLibraryItemRead,
    HighlightLibraryResponse,
    HighlightLibrarySummary,
    StudyHighlightCreate,
    StudyHighlightUpdate,
)
from app.services.persistence import commit_changes, get_user_resource_or_404
from app.services.sharing_service import can_read_study

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _check_study_access(session: Session, study_id: int, user_id: str, *, for_mutation: bool = False) -> Study:
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado ou está na lixeira.")

    if study.user_id == user_id:
        return study

    if can_read_study(session, user_id, study):
        if for_mutation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso somente leitura. Apenas o proprietário pode alterar este estudo.",
            )
        return study

    raise HTTPException(status_code=404, detail="Estudo não encontrado.")


def list_study_highlights(
    session: Session,
    study_id: int,
    user_id: str,
    section: str | None = None,
) -> list[StudyHighlight]:
    _check_study_access(session, study_id, user_id, for_mutation=False)

    stmt = select(StudyHighlight).where(
        StudyHighlight.study_id == study_id,
        StudyHighlight.user_id == user_id,
    )
    if section:
        stmt = stmt.where(StudyHighlight.section == section)

    stmt = stmt.order_by(StudyHighlight.start_offset.asc(), StudyHighlight.id.asc())
    return list(session.scalars(stmt).all())


def create_study_highlight(
    session: Session,
    study_id: int,
    user_id: str,
    payload: StudyHighlightCreate,
) -> StudyHighlight:
    _check_study_access(session, study_id, user_id, for_mutation=True)

    if payload.end_offset < payload.start_offset:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O offset de término (end_offset) deve ser maior ou igual ao offset de início (start_offset).",
        )

    highlight = StudyHighlight(
        study_id=study_id,
        user_id=user_id,
        section=payload.section,
        start_offset=payload.start_offset,
        end_offset=payload.end_offset,
        selected_text=payload.selected_text,
        prefix=payload.prefix,
        suffix=payload.suffix,
        color=payload.color,
        kind=payload.kind,
        note=payload.note,
    )
    session.add(highlight)
    commit_changes(session)
    session.refresh(highlight)
    return highlight


def update_study_highlight(
    session: Session,
    study_id: int,
    highlight_id: int,
    user_id: str,
    payload: StudyHighlightUpdate,
) -> StudyHighlight:
    _check_study_access(session, study_id, user_id, for_mutation=True)
    highlight = get_user_resource_or_404(session, StudyHighlight, highlight_id, user_id, "Destaque")
    if highlight.study_id != study_id:
        raise HTTPException(status_code=404, detail="Destaque não pertence a este estudo.")

    if payload.color is not None:
        highlight.color = payload.color
    if payload.kind is not None:
        highlight.kind = payload.kind
    if payload.note is not None:
        highlight.note = payload.note

    commit_changes(session)
    session.refresh(highlight)
    return highlight


def delete_study_highlight(
    session: Session,
    study_id: int,
    highlight_id: int,
    user_id: str,
) -> None:
    _check_study_access(session, study_id, user_id, for_mutation=True)
    highlight = get_user_resource_or_404(session, StudyHighlight, highlight_id, user_id, "Destaque")
    if highlight.study_id != study_id:
        raise HTTPException(status_code=404, detail="Destaque não pertence a este estudo.")

    session.delete(highlight)
    commit_changes(session)


def list_library_highlights(
    session: Session,
    user_id: str,
    *,
    q: str | None = None,
    book_id: int | None = None,
    chapter_id: int | None = None,
    kind: str | None = None,
    color: str | None = None,
    view_mode: str = "recent",
    page: int = 1,
    per_page: int = 20,
) -> HighlightLibraryResponse:
    stmt = (
        select(
            StudyHighlight,
            Study.title.label("study_title"),
            Chapter.id.label("chapter_id"),
            Chapter.name.label("chapter_title"),
            Book.id.label("book_id"),
            Book.title.label("book_title"),
            Book.author.label("book_author"),
        )
        .join(Study, StudyHighlight.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            StudyHighlight.user_id == user_id,
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
    )

    if q and q.strip():
        term = q.strip()
        stmt = stmt.where(
            or_(
                StudyHighlight.selected_text.ilike(f"%{term}%"),
                StudyHighlight.note.ilike(f"%{term}%"),
            )
        )

    if book_id is not None:
        stmt = stmt.where(Book.id == book_id)

    if chapter_id is not None:
        stmt = stmt.where(Chapter.id == chapter_id)

    if kind and kind.strip():
        stmt = stmt.where(StudyHighlight.kind == kind.strip())

    if color and color.strip():
        stmt = stmt.where(StudyHighlight.color == color.strip())

    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = session.scalar(count_stmt) or 0

    if view_mode == "by_book":
        stmt = stmt.order_by(
            Book.title.asc(),
            Chapter.position.asc(),
            Study.position.asc(),
            StudyHighlight.start_offset.asc(),
            StudyHighlight.id.asc(),
        )
    else:
        stmt = stmt.order_by(
            StudyHighlight.created_at.desc(),
            StudyHighlight.id.desc(),
        )

    safe_page = max(1, page)
    safe_per_page = max(1, min(100, per_page))
    offset = (safe_page - 1) * safe_per_page
    stmt = stmt.offset(offset).limit(safe_per_page)

    rows = session.execute(stmt).all()
    items = [
        HighlightLibraryItemRead(
            id=hl.id,
            study_id=hl.study_id,
            study_title=study_title,
            chapter_id=c_id,
            chapter_title=c_title,
            book_id=b_id,
            book_title=b_title,
            book_author=b_author,
            section=hl.section,
            start_offset=hl.start_offset,
            end_offset=hl.end_offset,
            selected_text=hl.selected_text,
            prefix=hl.prefix,
            suffix=hl.suffix,
            color=hl.color,
            kind=hl.kind,
            note=hl.note,
            created_at=hl.created_at,
            updated_at=hl.updated_at,
        )
        for hl, study_title, c_id, c_title, b_id, b_title, b_author in rows
    ]

    books_stmt = (
        select(Book.id, Book.title, func.count(StudyHighlight.id).label("count"))
        .join(Chapter, Chapter.book_id == Book.id)
        .join(Study, Study.chapter_id == Chapter.id)
        .join(StudyHighlight, StudyHighlight.study_id == Study.id)
        .where(
            StudyHighlight.user_id == user_id,
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
        .group_by(Book.id, Book.title)
        .order_by(Book.title.asc())
    )
    available_books = [
        HighlightLibraryFilterOption(id=b_id, title=b_title, count=b_count)
        for b_id, b_title, b_count in session.execute(books_stmt).all()
    ]

    summary_stmt = (
        select(
            func.count(case((StudyHighlight.kind == "highlight", 1))),
            func.count(case((StudyHighlight.kind == "note", 1))),
            func.count(case((StudyHighlight.kind == "quote", 1))),
            func.count(case((StudyHighlight.kind == "hidden", 1))),
            func.count(case((StudyHighlight.kind == "question", 1))),
        )
        .select_from(StudyHighlight)
        .join(Study, StudyHighlight.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            StudyHighlight.user_id == user_id,
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
    )
    sum_row = session.execute(summary_stmt).first()
    summary = HighlightLibrarySummary(
        total_highlights=sum_row[0] if sum_row else 0,
        total_notes=sum_row[1] if sum_row else 0,
        total_quotes=sum_row[2] if sum_row else 0,
        total_hidden=sum_row[3] if sum_row else 0,
        total_questions=sum_row[4] if sum_row else 0,
    )

    pages = max(1, (total + safe_per_page - 1) // safe_per_page) if total > 0 else 1
    return HighlightLibraryResponse(
        items=items,
        total=total,
        page=safe_page,
        per_page=safe_per_page,
        pages=pages,
        has_next=safe_page < pages,
        has_prev=safe_page > 1,
        available_books=available_books,
        summary=summary,
    )
