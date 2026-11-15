"""F0.12.03 (spec 116): importar a biblioteca de outro serviço (Goodreads, StoryGraph, BookWyrm) a partir do CSV exportado.

Leitores puros: recebem bytes e devolvem livros com estado e datas de leitura. A detecção é pelo cabeçalho (os nomes
dos arquivos mudam; as colunas são estáveis). Formatos conferidos nos arquivos de exemplo e no código do BookWyrm.
"""
from __future__ import annotations

import csv
import html
import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime

MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 20_000

STATE_BY_SHELF = {
    "to-read": "quero_ler",
    "want to read": "quero_ler",
    "want-to-read": "quero_ler",
    "currently-reading": "lendo",
    "currently reading": "lendo",
    "reading": "lendo",
    "read": "lido",
    "already read": "lido",
    "did-not-finish": "abandonado",
    "did not finish": "abandonado",
    "dnf": "abandonado",
    "stopped-reading": "abandonado",
    "stopped reading": "abandonado",
}
SERVICE_LABELS = {"goodreads": "Goodreads", "storygraph": "StoryGraph", "bookwyrm": "BookWyrm"}


class LibraryFormatError(ValueError):
    """Arquivo que não é o CSV de biblioteca de nenhum dos serviços reconhecidos."""


@dataclass
class LibraryRow:
    title: str
    author: str | None = None
    isbn: str | None = None
    year: int | None = None
    publisher: str | None = None
    state: str | None = None
    shelf: str | None = None  # valor original, para a prévia
    started_on: date | None = None
    finished_on: date | None = None
    review: str = ""
    review_date: date | None = None


@dataclass
class LibraryParseResult:
    service: str
    rows: list[LibraryRow] = field(default_factory=list)
    skipped: int = 0


# ---------------------------------------------------------------------------------------------- utilidades

def normalize_isbn(value: str | None) -> str | None:
    """`="9781250313195"` → `9781250313195`; aceita ISBN-10 com X; descarta o que não tiver 10 ou 13 dígitos."""
    digits = re.sub(r"[^0-9Xx]", "", value or "").upper()
    return digits if len(digits) in (10, 13) else None


def parse_date(value: str | None) -> date | None:
    text = (value or "").strip()
    if not text:
        return None
    match = re.match(r"^(\d{4})[/-](\d{1,2})[/-](\d{1,2})", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def parse_year(value: str | None) -> int | None:
    match = re.search(r"\b(1\d{3}|20\d{2}|2100)\b", value or "")
    return int(match.group(1)) if match else None


def clean_html(text: str | None) -> str:
    value = re.sub(r"<br\s*/?>", "\n", text or "", flags=re.IGNORECASE)
    value = re.sub(r"</p\s*>", "\n\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\n{3,}", "\n\n", html.unescape(value)).strip()


def join_authors(*parts: str | None, split_commas: bool = False) -> str | None:
    names: list[str] = []
    for part in parts:
        for name in re.split(r"\s*,\s*" if split_commas else r"\s*;\s*", part or ""):
            name = name.strip()
            if name and name not in names:
                names.append(name)
    return "; ".join(names) or None


def state_for(shelf: str | None) -> str | None:
    return STATE_BY_SHELF.get((shelf or "").strip().lower())


def read_rows(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    if len(data) > MAX_BYTES:
        raise LibraryFormatError("O arquivo passa de 10 MB.")
    text = data.decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
    first = text.split("\n", 1)[0]
    delimiter = ";" if first.count(";") > first.count(",") else ","
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    try:
        header = next(reader)
    except StopIteration as exc:
        raise LibraryFormatError("O arquivo está vazio.") from exc
    keys = [h.strip().lower() for h in header]
    rows: list[dict[str, str]] = []
    for index, values in enumerate(reader):
        if index >= MAX_ROWS:
            raise LibraryFormatError(f"O arquivo passa de {MAX_ROWS} linhas.")
        if not any(v.strip() for v in values):
            continue
        rows.append({keys[i]: (values[i] if i < len(values) else "") for i in range(len(keys))})
    return keys, rows


# ---------------------------------------------------------------------------------------------- detecção e leitores

def detect_library_format(data: bytes) -> str:
    keys, _ = read_rows(data[:200_000] if len(data) > 200_000 else data)
    names = set(keys)
    if {"title", "exclusive shelf"} <= names and ("author" in names or "author l-f" in names):
        return "goodreads"
    if {"title", "authors", "read status"} <= names:
        return "storygraph"
    if {"title", "author_text", "shelf"} <= names:
        return "bookwyrm"
    raise LibraryFormatError(
        "Não reconheci este arquivo como o CSV de biblioteca do Goodreads, do StoryGraph ou do BookWyrm."
    )


def _finish(service: str, rows: list[LibraryRow], skipped: int) -> LibraryParseResult:
    unique: dict[tuple[str, str], LibraryRow] = {}
    for row in rows:
        key = (row.isbn or "", row.title.casefold()) if row.isbn else ("", f"{row.title.casefold()}|{(row.author or '').casefold()}")
        if key in unique:
            skipped += 1
            continue
        unique[key] = row
    return LibraryParseResult(service=service, rows=list(unique.values()), skipped=skipped)


def parse_goodreads(data: bytes) -> LibraryParseResult:
    _, raw = read_rows(data)
    rows: list[LibraryRow] = []
    skipped = 0
    for r in raw:
        title = (r.get("title") or "").strip()
        if not title:
            skipped += 1
            continue
        shelf = (r.get("exclusive shelf") or "").strip()
        state = state_for(shelf)
        rows.append(LibraryRow(
            title=title,
            author=join_authors(r.get("author"), r.get("additional authors"), split_commas=True),
            isbn=normalize_isbn(r.get("isbn13")) or normalize_isbn(r.get("isbn")),
            year=parse_year(r.get("year published")) or parse_year(r.get("original publication year")),
            publisher=(r.get("publisher") or "").strip() or None,
            state=state,
            shelf=shelf or None,
            finished_on=parse_date(r.get("date read")) if state in ("lido", None) else None,
            review=clean_html(r.get("my review")),
            review_date=parse_date(r.get("date read")) or parse_date(r.get("date added")),
        ))
    return _finish("goodreads", rows, skipped)


def parse_storygraph(data: bytes) -> LibraryParseResult:
    _, raw = read_rows(data)
    rows: list[LibraryRow] = []
    skipped = 0
    for r in raw:
        title = (r.get("title") or "").strip()
        if not title:
            skipped += 1
            continue
        shelf = (r.get("read status") or "").strip()
        state = state_for(shelf)
        last = parse_date(r.get("last date read"))
        rows.append(LibraryRow(
            title=title,
            author=join_authors(r.get("authors"), split_commas=True),
            isbn=normalize_isbn(r.get("isbn/uid")),
            state=state,
            shelf=shelf or None,
            finished_on=last if state == "lido" else None,
            review=clean_html(r.get("review")),
            review_date=last or parse_date(r.get("date added")),
        ))
    return _finish("storygraph", rows, skipped)


def parse_bookwyrm(data: bytes) -> LibraryParseResult:
    _, raw = read_rows(data)
    rows: list[LibraryRow] = []
    skipped = 0
    for r in raw:
        title = (r.get("title") or "").strip()
        if not title:
            skipped += 1
            continue
        shelf = (r.get("shelf") or "").strip()
        state = state_for(shelf) or state_for(r.get("shelf_name"))
        started = parse_date(r.get("start_date"))
        finished = parse_date(r.get("finish_date"))
        stopped = parse_date(r.get("stopped_date"))
        rows.append(LibraryRow(
            title=title,
            author=join_authors(r.get("author_text"), split_commas=True),
            isbn=normalize_isbn(r.get("isbn_13")) or normalize_isbn(r.get("isbn_10")),
            state=state,
            shelf=shelf or None,
            started_on=started if state in ("lendo", "lido", "abandonado") else None,
            finished_on=(stopped if state == "abandonado" else finished) if state in ("lido", "abandonado") else None,
            review=clean_html(r.get("review_content")),
            review_date=parse_date(r.get("review_published")),
        ))
    return _finish("bookwyrm", rows, skipped)


def parse_library(data: bytes) -> LibraryParseResult:
    if not data:
        raise LibraryFormatError("O arquivo está vazio.")
    service = detect_library_format(data)
    return {"goodreads": parse_goodreads, "storygraph": parse_storygraph, "bookwyrm": parse_bookwyrm}[service](data)
