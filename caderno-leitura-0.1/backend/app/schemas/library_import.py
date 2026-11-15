"""F0.12.03 (spec 116): prévia e importação da biblioteca de outro serviço."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import Field

from app.schemas.common import InputModel, OutputModel

LibraryService = Literal["goodreads", "storygraph", "bookwyrm"]
LibraryAction = Literal["create", "update", "skip"]


class LibraryPreviewRow(OutputModel):
    key: str
    title: str
    author: str | None = None
    isbn: str | None = None
    year: int | None = None
    state: str | None = None
    state_label: str = "Sem estado"
    shelf: str | None = None
    started_on: date | None = None
    finished_on: date | None = None
    has_review: bool = False
    existing_book_id: int | None = None
    existing_book_title: str | None = None
    suggested_action: Literal["create", "skip"] = "create"


class LibraryPreviewResponse(OutputModel):
    service: LibraryService
    service_label: str
    rows: list[LibraryPreviewRow] = Field(default_factory=list)
    skipped: int = 0


class LibraryChoice(InputModel):
    key: str
    action: LibraryAction


class LibraryImportResponse(OutputModel):
    service: LibraryService
    created: int = 0
    updated: int = 0
    skipped: int = 0
    reviews: int = 0
