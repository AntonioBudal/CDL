"""F0.12.03 (spec 116): prévia e importação da biblioteca (Goodreads, StoryGraph, BookWyrm).

Prévia não grava. Casamento com o acervo: mesmo ISBN, ou mesmo título normalizado + sobrenome do primeiro autor (regra
da F0.10.07/F0.11.03). Ações por livro: criar, atualizar estado e datas (só já existentes) ou pular. Resenhas,
opcionais, viram capturas na Mesa. Notas em estrelas não são importadas (o Leitorum não tem esse campo).
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.book import Book
from app.models.inbox_capture import InboxCapture
from app.schemas.library_import import (
    LibraryChoice,
    LibraryImportResponse,
    LibraryPreviewResponse,
    LibraryPreviewRow,
)
from app.services.ereader_import.service import _title_keys
from app.services.in_common_service import first_author_surname_key
from app.services.library_import import (
    SERVICE_LABELS,
    LibraryFormatError,
    LibraryParseResult,
    LibraryRow,
    normalize_isbn,
    parse_library,
)

STATE_LABELS = {"quero_ler": "Quero ler", "lendo": "Lendo", "lido": "Lido", "abandonado": "Abandonado"}


def parse_upload(data: bytes) -> LibraryParseResult:
    try:
        return parse_library(data)
    except LibraryFormatError as exc:
        code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if "passa de" in str(exc) else status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(status_code=code, detail=str(exc)) from exc


def _my_books(session: Session, user_id: str) -> list[Book]:
    return list(session.scalars(
        select(Book).where(Book.user_id == user_id, Book.deleted_at.is_(None)).order_by(Book.id)
    ).all())


def match_book(row: LibraryRow, books: list[Book]) -> Book | None:
    if row.isbn:
        for book in books:
            if normalize_isbn(book.isbn) == row.isbn:
                return book
    keys = _title_keys(row.title)
    author = first_author_surname_key(row.author)
    for book in books:
        if not keys & _title_keys(book.title):
            continue
        other = first_author_surname_key(book.author)
        if author and other and author != other:
            continue
        return book
    return None


def build_preview(session: Session, user_id: str, parsed: LibraryParseResult) -> LibraryPreviewResponse:
    books = _my_books(session, user_id)
    rows: list[LibraryPreviewRow] = []
    for index, row in enumerate(parsed.rows):
        existing = match_book(row, books)
        rows.append(LibraryPreviewRow(
            key=str(index),
            title=row.title,
            author=row.author,
            isbn=row.isbn,
            year=row.year,
            state=row.state,
            state_label=STATE_LABELS.get(row.state or "", "Sem estado"),
            shelf=row.shelf,
            started_on=row.started_on,
            finished_on=row.finished_on,
            has_review=bool(row.review),
            existing_book_id=existing.id if existing else None,
            existing_book_title=existing.title if existing else None,
            suggested_action="skip" if existing else "create",
        ))
    return LibraryPreviewResponse(
        service=parsed.service,
        service_label=SERVICE_LABELS[parsed.service],
        rows=rows,
        skipped=parsed.skipped,
    )


def _apply_reading(book: Book, row: LibraryRow) -> None:
    """Estado e datas do arquivo; nunca apaga uma data que o arquivo não traz."""
    if row.state:
        book.reading_state = row.state
    if row.started_on:
        book.reading_started_on = row.started_on
    if row.finished_on:
        book.reading_finished_on = row.finished_on


def _add_review(session: Session, user_id: str, book: Book, row: LibraryRow, label: str) -> bool:
    text = row.review.strip()
    if not text:
        return False
    hint = f"Resenha do {label}" + (f" · {row.review_date.strftime('%d/%m/%Y')}" if row.review_date else "")
    exists = session.scalar(select(InboxCapture.id).where(
        InboxCapture.user_id == user_id, InboxCapture.book_id == book.id,
        InboxCapture.content == text, InboxCapture.source_hint == hint,
    ))
    if exists:
        return False
    now = utc_now()
    session.add(InboxCapture(user_id=user_id, book_id=book.id, content=text, source_hint=hint[:500], status="inbox",
                             created_at=now, updated_at=now))
    return True


def run_import(
    session: Session, user_id: str, parsed: LibraryParseResult, choices: list[LibraryChoice], with_reviews: bool
) -> LibraryImportResponse:
    by_key = {c.key: c for c in choices}
    books = _my_books(session, user_id)
    label = SERVICE_LABELS[parsed.service]
    result = LibraryImportResponse(service=parsed.service)
    for index, row in enumerate(parsed.rows):
        choice = by_key.get(str(index))
        if choice is None or choice.action == "skip":
            result.skipped += 1
            continue
        if choice.action == "update":
            book = match_book(row, books)
            if book is None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail=f"“{row.title}” não está mais no acervo; refaça a prévia.")
            _apply_reading(book, row)
            result.updated += 1
        else:
            book = Book(
                user_id=user_id,
                title=row.title[:500],
                author=row.author,
                isbn=row.isbn,
                year=row.year if row.year and 1000 <= row.year <= 2100 else None,
                publisher=row.publisher,
            )
            _apply_reading(book, row)
            session.add(book)
            session.flush()
            books.append(book)
            result.created += 1
        if with_reviews and _add_review(session, user_id, book, row, label):
            result.reviews += 1
    session.commit()
    return result
