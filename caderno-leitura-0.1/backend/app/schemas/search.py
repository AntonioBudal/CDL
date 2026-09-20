from datetime import datetime
from typing import Literal

from app.schemas.common import OutputModel


class SearchMatchItem(OutputModel):
    study_id: int
    study_title: str
    book_id: int
    book_title: str
    chapter_id: int | None = None
    chapter_name: str | None = None
    reading_status: str = "rascunho"
    matched_field: str
    snippet: str
    updated_at: datetime


class SearchResponse(OutputModel):
    query: str
    mode: Literal["and", "or"] = "and"
    total: int = 0
    results: list[SearchMatchItem] = []
    suggest_or: bool = False


class SearchHistoryItem(OutputModel):
    id: int
    query: str
    created_at: datetime
    updated_at: datetime


class SearchHistoryResponse(OutputModel):
    items: list[SearchHistoryItem] = []
