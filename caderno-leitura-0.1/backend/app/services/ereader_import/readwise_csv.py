"""CSV de destaques do Readwise (F0.12.03, spec 116).

O cabeçalho real não pôde ser conferido (a página de exportação exige login); o leitor é tolerante: nomes de coluna sem
diferença de maiúsculas, colunas extras ignoradas, BOM, `;` e CRLF. Colunas usadas: `Highlight` (obrigatória), `Book
Title` (obrigatória), `Book Author`, `Note`, `Location`, `Location Type`, `Highlighted at`.
"""
from __future__ import annotations

from datetime import UTC, datetime

from app.services.ereader_import import EreaderBook, EreaderEntry, EreaderFormatError, EreaderParseResult
from app.services.library_import import LibraryFormatError, read_rows

REQUIRED = {"highlight", "book title"}


def looks_like_readwise(data: bytes) -> bool:
    head = data[:4096].decode("utf-8-sig", errors="replace").split("\n", 1)[0].lower()
    return all(name in head for name in REQUIRED)


def _datetime(value: str | None) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def parse_readwise_csv(data: bytes) -> EreaderParseResult:
    try:
        keys, rows = read_rows(data)
    except LibraryFormatError as exc:
        raise EreaderFormatError(str(exc)) from exc
    if not REQUIRED <= set(keys):
        raise EreaderFormatError("O CSV do Readwise precisa das colunas Highlight e Book Title.")
    books: dict[tuple[str, str], EreaderBook] = {}
    skipped = 0
    for row in rows:
        text, note = (row.get("highlight") or "").strip(), (row.get("note") or "").strip()
        title = (row.get("book title") or "").strip()
        if not title or (not text and not note):
            skipped += 1
            continue
        author = (row.get("book author") or "").strip() or None
        key = (title.casefold(), (author or "").casefold())
        book = books.setdefault(key, EreaderBook(title=title, author=author))
        location = (row.get("location") or "").strip() or None
        by_page = (row.get("location type") or "").strip().lower() == "page"
        book.entries.append(EreaderEntry(
            kind="note" if note and not text else "highlight",
            text=text,
            note=note,
            page=location if by_page else None,
            location=None if by_page else location,
            created_at=_datetime(row.get("highlighted at")),
        ))
    return EreaderParseResult(source="readwise", books=list(books.values()), skipped=skipped)
