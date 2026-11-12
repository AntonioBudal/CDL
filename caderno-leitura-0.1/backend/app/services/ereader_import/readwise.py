"""Corpo compatível com a API v2 do Readwise, como o Readest envia (F0.11.09, spec 111).

``{"highlights": [{text, title, author, note, location, location_type, highlighted_at, source_type, …}]}``; os
destaques vêm soltos e são agrupados por título e autor. Marcadores de página ("Page 12", "Position …") sem nota são
pulados: não são destaques.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime

from app.schemas.receiver import ReadwiseHighlightIn
from app.services.ereader_import import EreaderBook, EreaderEntry, EreaderParseResult

BOOKMARK = re.compile(r"^(page|position)\s+\S+$", re.IGNORECASE)
KNOWN_SOURCES = {"readest": "readest", "koreader": "koreader"}


def _date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _location(value: int | float | str | None) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, float):
        value = int(value)
    text = str(value).strip()
    return text or None


def _clean_author(value: str | None) -> str | None:
    text = (value or "").strip()
    return text or None


def parse_readwise_highlights(items: list[ReadwiseHighlightIn]) -> EreaderParseResult:
    source = "readest"
    for item in items:
        if item.source_type and item.source_type.strip().lower() in KNOWN_SOURCES:
            source = KNOWN_SOURCES[item.source_type.strip().lower()]
            break
    books: dict[tuple[str, str], EreaderBook] = {}
    skipped = 0
    for item in items:
        text, note = (item.text or "").strip(), (item.note or "").strip()
        if not text and not note:
            skipped += 1
            continue
        if not note and BOOKMARK.match(text):
            skipped += 1
            continue
        title = (item.title or "").strip() or "Livro sem título"
        author = _clean_author(item.author)
        key = (title.casefold(), (author or "").casefold())
        book = books.setdefault(key, EreaderBook(title=title, author=author))
        location = _location(item.location)
        by_page = (item.location_type or "").strip().lower() == "page"
        book.entries.append(EreaderEntry(
            kind="note" if note and not text else "highlight",
            text=text,
            note=note,
            page=location if by_page else None,
            location=None if by_page else location,
            chapter=(item.chapter or "").strip() or None,
            created_at=_date(item.highlighted_at),
        ))
    return EreaderParseResult(source=source, books=list(books.values()), skipped=skipped)
