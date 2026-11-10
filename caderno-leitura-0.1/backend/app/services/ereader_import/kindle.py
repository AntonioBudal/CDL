"""Leitura do ``My Clippings.txt`` do Kindle (F0.11.03).

Blocos separados por ``==========``; cada bloco: linha do título ``Título (Autor)``, linha de metadados e o texto.
Metadados em inglês ("- Your Highlight on page 32 | Location 488-489 | Added on Monday, March 3, 2025 10:12:01 AM")
ou português ("- Seu destaque na página 32 | posição 488-489 | Adicionado: segunda-feira, 3 de março de 2025
10:12:01").
"""
from __future__ import annotations

import re
from datetime import datetime

from app.services.ereader_import import EreaderBook, EreaderEntry, EreaderFormatError, EreaderParseResult

SEPARATOR = "=========="

_PAGE = re.compile(r"(?:\bpage|\bp[áa]gina)\s+([0-9ivxlcdm]+(?:-[0-9ivxlcdm]+)?)", re.IGNORECASE)
_LOCATION = re.compile(r"(?:\blocation|\bloc\.|\bposi[çc][ãa]o)\s+(\d+(?:-\d+)?)", re.IGNORECASE)
_ADDED_EN = re.compile(r"added on\s+(.+)$", re.IGNORECASE)
_ADDED_PT = re.compile(r"adicionado:?\s+(?:em\s+)?(.+)$", re.IGNORECASE)

_PT_MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
    "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def _kind(meta: str) -> str | None:
    lower = meta.lower()
    if "highlight" in lower or "destaque" in lower:
        return "highlight"
    if "note" in lower or "nota" in lower:
        return "note"
    if "bookmark" in lower or "marcador" in lower:
        return "bookmark"
    return None


def _normalize_location(raw: str) -> str:
    """'488-89' → '488-489' (o Kindle antigo abreviava o fim do intervalo)."""
    if "-" not in raw:
        return raw
    start, end = raw.split("-", 1)
    if len(end) < len(start) and int(end) < int(start):
        end = start[: len(start) - len(end)] + end
    return f"{start}-{end}"


def _parse_date(meta: str) -> datetime | None:
    match = _ADDED_EN.search(meta)
    if match:
        text = match.group(1).strip()
        for fmt in ("%A, %B %d, %Y %I:%M:%S %p", "%A, %d %B %Y %H:%M:%S", "%A, %B %d, %Y, %I:%M %p"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None
    match = _ADDED_PT.search(meta)
    if match:
        found = re.search(
            r"(\d{1,2}) de (\w+) de (\d{4})(?:,?\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?", match.group(1), re.IGNORECASE
        )
        if found:
            day, month_name, year, hour, minute, second = found.groups()
            month = _PT_MONTHS.get(month_name.lower())
            if month:
                try:
                    return datetime(int(year), month, int(day), int(hour or 0), int(minute or 0), int(second or 0))
                except ValueError:
                    return None
    return None


def _split_title(line: str) -> tuple[str, str | None]:
    """'Título (Edição) (Autor)' → ('Título (Edição)', 'Autor'); sem parênteses no fim → autor ausente."""
    text = line.replace("﻿", "").strip()
    if text.endswith(")"):
        depth = 0
        for index in range(len(text) - 1, -1, -1):
            if text[index] == ")":
                depth += 1
            elif text[index] == "(":
                depth -= 1
                if depth == 0:
                    title = text[:index].strip()
                    author = text[index + 1:-1].strip()
                    if title:
                        return title, author or None
                    break
    return text or "Livro sem título (Kindle)", None


def _location_range(location: str | None) -> tuple[int, int] | None:
    if not location:
        return None
    start, _, end = location.partition("-")
    try:
        return int(start), int(end or start)
    except ValueError:
        return None


def parse_kindle_clippings(data: bytes) -> EreaderParseResult:
    text = data.decode("utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    if SEPARATOR not in text:
        raise EreaderFormatError("Não reconheci este arquivo como My Clippings.txt do Kindle.")

    books: dict[tuple[str, str | None], EreaderBook] = {}
    skipped = 0
    for block in text.split(SEPARATOR):
        lines = [line for line in block.split("\n")]
        while lines and not lines[0].strip():
            lines.pop(0)
        if len(lines) < 2:
            if any(line.strip() for line in lines):
                skipped += 1
            continue
        title, author = _split_title(lines[0])
        meta = lines[1].strip()
        kind = _kind(meta)
        body = "\n".join(lines[2:]).strip()
        if kind in (None, "bookmark") or not body:
            skipped += 1
            continue
        page_match = _PAGE.search(meta)
        loc_match = _LOCATION.search(meta)
        entry = EreaderEntry(
            kind=kind,
            page=page_match.group(1) if page_match else None,
            location=_normalize_location(loc_match.group(1)) if loc_match else None,
            created_at=_parse_date(meta),
        )
        if kind == "highlight":
            entry.text = body
        else:
            entry.note = body
        book = books.setdefault((title, author), EreaderBook(title=title, author=author))
        book.entries.append(entry)

    for book in books.values():
        book.entries = _merge_entries(book.entries)
    return EreaderParseResult(source="kindle", books=list(books.values()), skipped=skipped)


def _merge_entries(entries: list[EreaderEntry]) -> list[EreaderEntry]:
    """Remove destaques repetidos por ajuste de seleção e junta cada nota ao destaque do mesmo lugar."""
    highlights: list[EreaderEntry] = []
    for entry in (e for e in entries if e.kind == "highlight"):
        start = _location_range(entry.location)
        replaced = False
        for index, kept in enumerate(highlights):
            kept_start = _location_range(kept.location)
            same_start = start is not None and kept_start is not None and start[0] == kept_start[0]
            if same_start and (entry.text in kept.text or kept.text in entry.text):
                if len(entry.text) > len(kept.text):
                    highlights[index] = entry
                replaced = True
                break
        if not replaced:
            highlights.append(entry)

    merged: list[EreaderEntry] = list(highlights)
    for note in (e for e in entries if e.kind == "note"):
        note_range = _location_range(note.location)
        target = None
        if note_range is not None:
            for highlight in highlights:
                h_range = _location_range(highlight.location)
                if h_range and h_range[0] <= note_range[0] <= h_range[1] and not highlight.note:
                    target = highlight
        if target is not None:
            target.note = note.note
        else:
            merged.append(note)
    return merged
