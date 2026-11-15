"""Importação de destaques de leitores digitais (F0.11.03, spec 105): Kindle (``My Clippings.txt``) e Kobo
(``KoboReader.sqlite``); F0.11.09 (spec 111): JSON do exportador do KOReader e envio do Readest (formato Readwise).
Os parsers são puros: recebem bytes (ou o corpo já validado) e devolvem livros com entradas."""
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
    source: str  # "kindle", "kobo", "koreader", "readest", "readwise" ou "omnivore"
    books: list[EreaderBook]
    skipped: int = 0  # marcadores e blocos não reconhecidos


class EreaderFormatError(ValueError):
    """Arquivo que não é de nenhum dos formatos reconhecidos."""


def detect_format(data: bytes) -> str:
    if data.startswith(SQLITE_MAGIC):
        return "kobo"
    from app.services.ereader_import.koreader import looks_like_koreader_json
    from app.services.ereader_import.omnivore import looks_like_omnivore
    from app.services.ereader_import.readwise_csv import looks_like_readwise

    if looks_like_omnivore(data):
        return "omnivore"
    if looks_like_koreader_json(data):
        return "koreader"
    if looks_like_readwise(data):
        return "readwise"
    head = data[:200_000].decode("utf-8-sig", errors="replace")
    if "==========" in head:
        return "kindle"
    raise EreaderFormatError(
        "Não reconheci este arquivo. Aceitos: My Clippings.txt (Kindle), KoboReader.sqlite (Kobo), JSON do "
        "exportador do KOReader, CSV do Readwise e ZIP do Omnivore."
    )
