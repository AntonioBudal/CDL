"""F0.11.04 (spec 106): sugestão de dados do livro pela busca de ISBN."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.schemas.common import OutputModel, RecordId


class IsbnExistingBook(OutputModel):
    id: RecordId
    title: str


class IsbnLookupResponse(OutputModel):
    isbn: str
    source: Literal["brasilapi", "openlibrary"]
    title: str = ""
    subtitle: str = ""
    authors: list[str] = Field(default_factory=list)
    author: str = Field(default="", description="Autores juntados com '; ' (pronto para o campo Autor)")
    year: int | None = None
    publisher: str = ""
    place: str = ""
    existing_book: IsbnExistingBook | None = None
