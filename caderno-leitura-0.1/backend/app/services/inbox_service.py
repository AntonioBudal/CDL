"""Serviço para gerenciamento da Caixa de Entrada de Capturas (Inbox de Conhecimento)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.db.types import utc_now
from app.models.book import Book
from app.models.inbox_capture import InboxCapture
from app.models.study import Study
from app.schemas.inbox_capture import (
    InboxCaptureCreate,
    InboxCapturePatch,
    InboxCaptureRead,
    InboxCountResponse,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _build_read_model(capture: InboxCapture) -> InboxCaptureRead:
    book_title = capture.book.title if capture.book and capture.book.deleted_at is None else None
    promoted_study_title = (
        capture.promoted_study.title
        if capture.promoted_study and capture.promoted_study.deleted_at is None
        else None
    )
    return InboxCaptureRead(
        id=capture.id,
        user_id=capture.user_id,
        book_id=capture.book_id,
        book_title=book_title,
        content=capture.content,
        source_hint=capture.source_hint,
        status=capture.status,  # type: ignore[arg-type]
        promoted_study_id=capture.promoted_study_id,
        promoted_study_title=promoted_study_title,
        created_at=capture.created_at,
        updated_at=capture.updated_at,
    )


def list_inbox_captures(
    session: Session,
    user_id: str,
    status_filter: str | None = "inbox",
    q: str | None = None,
    book_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[InboxCaptureRead]:
    stmt = (
        select(InboxCapture)
        .options(
            selectinload(InboxCapture.book),
            selectinload(InboxCapture.promoted_study),
        )
        .where(InboxCapture.user_id == user_id)
    )

    if status_filter and status_filter != "all":
        stmt = stmt.where(InboxCapture.status == status_filter)

    if book_id is not None:
        stmt = stmt.where(InboxCapture.book_id == book_id)

    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                InboxCapture.content.ilike(term),
                InboxCapture.source_hint.ilike(term),
            )
        )

    stmt = stmt.order_by(InboxCapture.created_at.desc()).offset(offset).limit(limit)
    captures = session.scalars(stmt).all()
    return [_build_read_model(c) for c in captures]


def count_inbox_captures(session: Session, user_id: str) -> InboxCountResponse:
    stmt = select(func.count(InboxCapture.id)).where(
        InboxCapture.user_id == user_id,
        InboxCapture.status == "inbox",
    )
    total = session.scalar(stmt) or 0
    return InboxCountResponse(count=total)


def get_inbox_capture(session: Session, user_id: str, capture_id: int) -> InboxCapture:
    stmt = (
        select(InboxCapture)
        .options(
            selectinload(InboxCapture.book),
            selectinload(InboxCapture.promoted_study),
        )
        .where(InboxCapture.id == capture_id, InboxCapture.user_id == user_id)
    )
    capture = session.scalar(stmt)
    if not capture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Captura não encontrada.",
        )
    return capture


def create_inbox_capture(
    session: Session,
    user_id: str,
    payload: InboxCaptureCreate,
) -> InboxCaptureRead:
    if payload.book_id is not None:
        book = session.scalar(
            select(Book).where(
                Book.id == payload.book_id,
                Book.user_id == user_id,
                Book.deleted_at.is_(None),
            )
        )
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro associado não encontrado.",
            )

    capture = InboxCapture(
        user_id=user_id,
        book_id=payload.book_id,
        content=payload.content.strip(),
        source_hint=payload.source_hint.strip() if payload.source_hint else None,
        status="inbox",
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    session.add(capture)
    session.commit()
    session.refresh(capture)
    return _build_read_model(capture)


def update_inbox_capture(
    session: Session,
    user_id: str,
    capture_id: int,
    payload: InboxCapturePatch,
) -> InboxCaptureRead:
    capture = get_inbox_capture(session, user_id, capture_id)

    if payload.book_id is not None:
        book = session.scalar(
            select(Book).where(
                Book.id == payload.book_id,
                Book.user_id == user_id,
                Book.deleted_at.is_(None),
            )
        )
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro associado não encontrado.",
            )
        capture.book_id = payload.book_id

    if payload.content is not None:
        capture.content = payload.content.strip()

    if payload.source_hint is not None:
        capture.source_hint = payload.source_hint.strip() if payload.source_hint.strip() else None

    if payload.status is not None:
        capture.status = payload.status

    capture.updated_at = utc_now()
    session.commit()
    session.refresh(capture)
    return _build_read_model(capture)


def delete_inbox_capture(session: Session, user_id: str, capture_id: int) -> None:
    capture = get_inbox_capture(session, user_id, capture_id)
    session.delete(capture)
    session.commit()


def promote_inbox_capture(
    session: Session,
    user_id: str,
    capture_id: int,
    study_id: int,
) -> InboxCaptureRead:
    capture = get_inbox_capture(session, user_id, capture_id)

    study = session.scalar(
        select(Study).where(
            Study.id == study_id,
            Study.user_id == user_id,
            Study.deleted_at.is_(None),
        )
    )
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudo promovido não encontrado ou na lixeira.",
        )

    capture.status = "promoted"
    capture.promoted_study_id = study.id
    capture.updated_at = utc_now()
    session.commit()
    session.refresh(capture)
    return _build_read_model(capture)


def link_inbox_capture(
    session: Session,
    user_id: str,
    capture_id: int,
    target_study_id: int,
    target_section: str = "references",
) -> InboxCaptureRead:
    capture = get_inbox_capture(session, user_id, capture_id)

    study = session.scalar(
        select(Study).where(
            Study.id == target_study_id,
            Study.user_id == user_id,
            Study.deleted_at.is_(None),
        )
    )
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudo de destino não encontrado ou na lixeira.",
        )

    valid_sections = {"summary", "explanation", "concepts", "references", "notes"}
    if target_section not in valid_sections:
        target_section = "references"

    source_desc = f" — Fonte: {capture.source_hint}" if capture.source_hint else ""
    snippet = f"\n\n---\n> {capture.content}\n*Nota capturada do Inbox{source_desc}*\n"

    current_val = getattr(study, target_section) or ""
    new_val = f"{current_val.rstrip()}{snippet}" if current_val.strip() else snippet.strip()
    setattr(study, target_section, new_val)
    study.updated_at = utc_now()

    capture.status = "linked"
    capture.promoted_study_id = study.id
    capture.updated_at = utc_now()

    session.commit()
    session.refresh(capture)
    return _build_read_model(capture)
