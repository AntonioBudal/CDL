"""Prévia e importação de destaques do Kindle e do Kobo para a Mesa de Triagem (F0.11.03, spec 105).

Sem estado no servidor: a prévia só lê; a importação recebe o arquivo de novo com as escolhas por livro. Cada destaque
vira uma captura ``status = inbox`` no livro escolhido (sem capítulo). Duplicata = mesmo livro + mesmo texto
(espaços normalizados) + mesma origem/localização.
"""
from __future__ import annotations

import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.book import Book
from app.models.inbox_capture import InboxCapture
from app.schemas.ereader_import import (
    EreaderBookPreview,
    EreaderChoice,
    EreaderImportedBook,
    EreaderImportResponse,
    EreaderPreviewResponse,
)
from app.services.ereader_import import (
    EreaderBook,
    EreaderEntry,
    EreaderFormatError,
    EreaderParseResult,
    detect_format,
)
from app.services.ereader_import.kindle import parse_kindle_clippings
from app.services.ereader_import.kobo import parse_kobo_database
from app.services.ereader_import.koreader import parse_koreader_json
from app.services.in_common_service import first_author_surname_key, normalize_title_key

KINDLE_MAX_BYTES = 20 * 1024 * 1024
KOBO_MAX_BYTES = 200 * 1024 * 1024
SOURCE_LABELS = {"kindle": "Kindle", "kobo": "Kobo", "koreader": "KOReader", "readest": "Readest"}


def parse_upload(data: bytes) -> EreaderParseResult:
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O arquivo está vazio.")
    try:
        kind = detect_format(data)
        if kind == "kindle":
            if len(data) > KINDLE_MAX_BYTES:
                raise HTTPException(status_code=413, detail="O My Clippings.txt passa de 20 MB.")
            return parse_kindle_clippings(data)
        if kind == "koreader":
            if len(data) > KINDLE_MAX_BYTES:
                raise HTTPException(status_code=413, detail="O JSON do KOReader passa de 20 MB.")
            return parse_koreader_json(data)
        if len(data) > KOBO_MAX_BYTES:
            raise HTTPException(status_code=413, detail="O KoboReader.sqlite passa de 200 MB.")
        return parse_kobo_database(data)
    except EreaderFormatError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def entry_content(entry: EreaderEntry) -> str:
    text = (entry.text or "").strip()
    note = (entry.note or "").strip()
    if text and note:
        return f"{text}\n\nNota: {note}"
    if note:
        return f"Nota: {note}"
    return text


def entry_source_hint(source: str, entry: EreaderEntry) -> str:
    parts = [SOURCE_LABELS.get(source, source)]
    if entry.page:
        parts.append(f"p. {entry.page}")
    if entry.location:
        parts.append(f"pos. {entry.location.replace('-', '–')}")
    if entry.chapter:
        parts.append(f"cap. {entry.chapter}")
    if entry.created_at:
        parts.append(entry.created_at.strftime("%d/%m/%Y"))
    return " · ".join(parts)[:500]


def _dedupe_key(content: str, source_hint: str | None) -> tuple[str, str]:
    return _clean(content), (source_hint or "").strip()


def _title_keys(title: str) -> set[str]:
    """Chave do título e a mesma sem grupos finais entre parênteses (o Kindle anexa edição/série: "Livro (Ed. 2)")."""
    keys = {normalize_title_key(title)}
    trimmed = title
    while (stripped := re.sub(r"\s*\([^()]*\)\s*$", "", trimmed)) != trimmed and stripped:
        trimmed = stripped
        keys.add(normalize_title_key(trimmed))
    keys.discard("")
    return keys


def _suggest(book: EreaderBook, my_books: list[Book]) -> Book | None:
    keys = _title_keys(book.title)
    if not keys:
        return None
    author_key = first_author_surname_key(book.author)
    for candidate in my_books:
        if not keys & _title_keys(candidate.title):
            continue
        candidate_author = first_author_surname_key(candidate.author)
        if author_key and candidate_author and author_key != candidate_author:
            continue
        return candidate
    return None


def _existing_keys(session: Session, user_id: str, book_id: int) -> set[tuple[str, str]]:
    rows = session.execute(
        select(InboxCapture.content, InboxCapture.source_hint).where(
            InboxCapture.user_id == user_id, InboxCapture.book_id == book_id
        )
    ).all()
    return {_dedupe_key(content, hint) for content, hint in rows}


def _my_books(session: Session, user_id: str) -> list[Book]:
    return list(
        session.scalars(
            select(Book).where(Book.user_id == user_id, Book.deleted_at.is_(None)).order_by(Book.id)
        ).all()
    )


def build_preview(session: Session, user_id: str, parsed: EreaderParseResult) -> EreaderPreviewResponse:
    my_books = _my_books(session, user_id)
    previews: list[EreaderBookPreview] = []
    total = 0
    for index, book in enumerate(parsed.books):
        suggestion = _suggest(book, my_books)
        existing = _existing_keys(session, user_id, suggestion.id) if suggestion else set()
        duplicates = 0
        seen: set[tuple[str, str]] = set()
        for entry in book.entries:
            key = _dedupe_key(entry_content(entry), entry_source_hint(parsed.source, entry))
            if key in existing or key in seen:
                duplicates += 1
            seen.add(key)
        total += len(book.entries)
        previews.append(
            EreaderBookPreview(
                key=str(index),
                title=book.title,
                author=book.author,
                highlights=sum(1 for e in book.entries if e.kind == "highlight"),
                notes=sum(1 for e in book.entries if e.note),
                new_count=len(book.entries) - duplicates,
                duplicate_count=duplicates,
                suggested_action="existing" if suggestion else "create",
                suggested_book_id=suggestion.id if suggestion else None,
                suggested_book_title=suggestion.title if suggestion else None,
            )
        )
    return EreaderPreviewResponse(source=parsed.source, books=previews, skipped=parsed.skipped, total_entries=total)


def run_import(
    session: Session, user_id: str, parsed: EreaderParseResult, choices: list[EreaderChoice]
) -> EreaderImportResponse:
    by_key = {choice.key: choice for choice in choices}
    result = EreaderImportResponse(source=parsed.source)
    now = utc_now()
    for index, book in enumerate(parsed.books):
        choice = by_key.get(str(index))
        if choice is None or choice.action == "skip":
            continue
        created_book = False
        if choice.action == "existing":
            target = session.scalar(
                select(Book).where(Book.id == choice.book_id, Book.user_id == user_id, Book.deleted_at.is_(None))
            ) if choice.book_id else None
            if target is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro de destino não encontrado.")
        else:
            target = Book(user_id=user_id, title=book.title.strip()[:500] or "Livro sem título", author=book.author)
            session.add(target)
            session.flush()
            created_book = True

        existing = set() if created_book else _existing_keys(session, user_id, target.id)
        created = duplicates = 0
        for entry in book.entries:
            content = entry_content(entry)
            hint = entry_source_hint(parsed.source, entry)
            key = _dedupe_key(content, hint)
            if not content or key in existing:
                duplicates += 1
                continue
            existing.add(key)
            session.add(
                InboxCapture(
                    user_id=user_id,
                    book_id=target.id,
                    content=content,
                    source_hint=hint,
                    status="inbox",
                    created_at=now,
                    updated_at=now,
                )
            )
            created += 1
        result.books.append(
            EreaderImportedBook(
                key=str(index), book_id=target.id, book_title=target.title,
                book_created=created_book, created=created, duplicates=duplicates,
            )
        )
        result.created += created
        result.duplicates += duplicates
    session.commit()
    return result


def receive_parsed(session: Session, user_id: str, parsed: EreaderParseResult) -> EreaderImportResponse:
    """F0.11.09: envio automático (sem prévia): livro sugerido pela regra de título/autor, senão livro novo."""
    my_books = _my_books(session, user_id)
    choices: list[EreaderChoice] = []
    for index, book in enumerate(parsed.books):
        suggestion = _suggest(book, my_books)
        choices.append(
            EreaderChoice(key=str(index), action="existing", book_id=suggestion.id)
            if suggestion is not None
            else EreaderChoice(key=str(index), action="create")
        )
    return run_import(session, user_id, parsed, choices)
