from __future__ import annotations

from pydantic import Field

from app.schemas.common import InputModel, NonBlankText, OutputModel


class CategoryCreate(InputModel):
    id: str | None = Field(default=None, max_length=100)
    name: NonBlankText
    parent_id: str | None = None


class CategoryRead(OutputModel):
    id: str
    name: str
    parent_id: str | None = None
    path: str
    user_id: str | None = None


class CategoryTree(CategoryRead):
    children: list[CategoryTree] = []
