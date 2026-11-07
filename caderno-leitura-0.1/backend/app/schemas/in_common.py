"""F0.10.07 (spec 100): leituras e estudos em comum entre amigos."""
from __future__ import annotations

from datetime import datetime

from app.schemas.common import OutputModel


class InCommonStudy(OutputModel):
    id: int
    title: str
    chapter_name: str | None = None
    book_id: int
    updated_at: datetime


class InCommonBook(OutputModel):
    title: str
    author: str | None = None
    my_book_id: int
    friend_book_id: int
    friend_studies: list[InCommonStudy]
    friend_studies_total: int


class InCommonResponse(OutputModel):
    is_friend: bool
    books: list[InCommonBook]
    books_truncated: bool
    shared_with_me_total: int
