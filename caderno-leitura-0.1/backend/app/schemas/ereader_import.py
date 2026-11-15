"""F0.11.03 (spec 105): prévia e importação de destaques do Kindle e do Kobo."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.schemas.common import InputModel, OutputModel, RecordId

EreaderSource = Literal["kindle", "kobo", "koreader", "readest", "readwise", "omnivore"]
EreaderAction = Literal["existing", "create", "skip"]


class EreaderBookPreview(OutputModel):
    key: str = Field(..., description="Identificador do livro dentro do arquivo (posição na lista)")
    title: str
    author: str | None = None
    highlights: int = 0
    notes: int = 0
    new_count: int = 0
    duplicate_count: int = 0
    suggested_action: Literal["existing", "create"] = "create"
    suggested_book_id: RecordId | None = None
    suggested_book_title: str | None = None


class EreaderPreviewResponse(OutputModel):
    source: EreaderSource
    books: list[EreaderBookPreview]
    skipped: int = 0
    total_entries: int = 0


class EreaderChoice(InputModel):
    key: str
    action: EreaderAction
    book_id: RecordId | None = None


class EreaderImportedBook(OutputModel):
    key: str
    book_id: RecordId
    book_title: str
    book_created: bool = False
    created: int = 0
    duplicates: int = 0


class EreaderImportResponse(OutputModel):
    source: EreaderSource
    created: int = 0
    duplicates: int = 0
    books: list[EreaderImportedBook] = Field(default_factory=list)
