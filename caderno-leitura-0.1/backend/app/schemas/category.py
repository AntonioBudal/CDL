from __future__ import annotations

from datetime import datetime
from pydantic import Field

from app.schemas.common import InputModel, NonBlankText, OutputModel


class CategoryCreate(InputModel):
    id: str | None = Field(default=None, max_length=100)
    name: NonBlankText = Field(..., min_length=2, max_length=30)
    parent_id: str | None = None


class CategoryRead(OutputModel):
    id: str
    name: str
    parent_id: str | None = None
    path: str = ""
    user_id: str | None = None
    is_canonical: bool = True
    books_count: int = 0
    created_at: datetime | None = None


class CategoryTree(CategoryRead):
    children: list[CategoryTree] = []


class CategorySuggestion(OutputModel):
    input_term: str
    suggested_canonical: str
    is_exact_match: bool
    matching_candidates: list[CategoryRead] = []


class CategoryStats(OutputModel):
    total_categories: int
    canonical_categories: int
    unused_categories: int
    total_book_associations: int
