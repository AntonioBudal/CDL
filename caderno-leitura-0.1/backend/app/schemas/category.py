from __future__ import annotations

from app.schemas.common import OutputModel


class CategoryRead(OutputModel):
    id: str
    name: str
    parent_id: str | None = None
    path: str


class CategoryTree(CategoryRead):
    children: list[CategoryTree] = []
