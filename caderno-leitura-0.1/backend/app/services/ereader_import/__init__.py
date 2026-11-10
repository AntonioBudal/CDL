"""Importação de destaques de leitores digitais (F0.11.03, spec 105): Kindle (``My Clippings.txt``) e Kobo
(``KoboReader.sqlite``). Os parsers são puros: recebem bytes e devolvem livros com entradas."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

SQLITE_MAGIC = b"SQLite format 3\x00"


@dataclass
class EreaderEntry:
    kind: str  # "highlight" ou "note"
    text: str = ""
    note: str = ""
    page: str | None = None
    location: str | None = None  # "488-489" ou "489"
    percent: int | None = None
    chapter: str | None = None
    created_at: datetime | None = None


@dataclass
class EreaderBook:
    title: str
    author: str | None
    entries: list[EreaderEntry] = field(default_factory=list)


@dataclass
class EreaderParseResult:
    source: str  # "kindle" ou "kobo"
    books: list[EreaderBook]
    skipped: int = 0  # marcadores e blocos não reconhecidos


class EreaderFormatError(ValueError):
    """Arquivo que não é ``My Clippings.txt`` do Kindle nem ``KoboReader.sqlite``."""


def detect_format(data: bytes) -> str:
    if data.startswith(SQLITE_MAGIC):
        return "kobo"
    head = data[:200_000].decode("utf-8-sig", errors="replace")
    if "==========" in head:
        return "kindle"
    raise EreaderFormatError(
        "Não reconheci este arquivo como My Clippings.txt do Kindle nem como KoboReader.sqlite."
    )
