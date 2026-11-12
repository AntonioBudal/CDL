"""Arquivo JSON do exportador do KOReader (F0.11.09, spec 111).

``exporter.koplugin/target/json.lua``: um livro (``title``, ``author``, ``entries`` e ``version: "json/1.0.0"`` no
topo) ou vários (``{"version": …, "documents": [livro, …]}``). Cada entrada: ``text``, ``note``, ``page``,
``chapter``, ``time`` (época Unix). Puro: recebe bytes e devolve livros com entradas.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from app.services.ereader_import import EreaderBook, EreaderEntry, EreaderFormatError, EreaderParseResult


def looks_like_koreader_json(data: bytes) -> bool:
    head = data[:64].lstrip(b"\xef\xbb\xbf \t\r\n")
    if not head.startswith(b"{"):
        return False
    try:
        doc = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError):
        return False
    return isinstance(doc, dict) and str(doc.get("version", "")).startswith("json/")


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _time(value: Any) -> datetime | None:
    if isinstance(value, (int, float)) and value > 0:
        try:
            return datetime.fromtimestamp(value, tz=UTC)
        except (OverflowError, OSError, ValueError):
            return None
    return None


def _page(value: Any) -> str | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return str(int(value))
    text = _text(value)
    return text or None


def parse_koreader_json(data: bytes) -> EreaderParseResult:
    try:
        doc = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise EreaderFormatError("Não reconheci este arquivo como o JSON do exportador do KOReader.") from exc
    if not isinstance(doc, dict) or not str(doc.get("version", "")).startswith("json/"):
        raise EreaderFormatError("Não reconheci este arquivo como o JSON do exportador do KOReader.")
    documents = doc.get("documents")
    raw_books = documents if isinstance(documents, list) else [doc]
    books: list[EreaderBook] = []
    skipped = 0
    for raw in raw_books:
        if not isinstance(raw, dict):
            continue
        title = _text(raw.get("title")) or "Livro sem título"
        author = _text(raw.get("author")) or None
        book = EreaderBook(title=title, author=author)
        for item in raw.get("entries") or []:
            if not isinstance(item, dict):
                skipped += 1
                continue
            text, note = _text(item.get("text")), _text(item.get("note"))
            if not text and not note:
                skipped += 1
                continue
            book.entries.append(EreaderEntry(
                kind="note" if note and not text else "highlight",
                text=text,
                note=note,
                page=_page(item.get("page")),
                chapter=_text(item.get("chapter")) or None,
                created_at=_time(item.get("time")),
            ))
        if book.entries:
            books.append(book)
    return EreaderParseResult(source="koreader", books=books, skipped=skipped)
