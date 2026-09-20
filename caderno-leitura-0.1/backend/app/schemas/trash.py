from datetime import datetime

from app.schemas.common import OutputModel


class TrashBookItem(OutputModel):
    id: int
    title: str
    author: str | None = None
    deleted_at: datetime
    days_until_purge: int
    chapters_count: int = 0
    studies_count: int = 0


class TrashStudyItem(OutputModel):
    id: int
    title: str
    book_id: int
    book_title: str
    chapter_name: str
    deleted_at: datetime
    days_until_purge: int


class TrashSummaryResponse(OutputModel):
    books: list[TrashBookItem]
    studies: list[TrashStudyItem]
    total_items: int


class TrashActionResponse(OutputModel):
    id: int
    title: str
    deleted_at: datetime | None = None
    book_restored: bool = False


class TrashEmptyResponse(OutputModel):
    purged_books: int
    purged_studies: int
    message: str


class TrashPurgeResponse(OutputModel):
    purged_books: int
    purged_studies: int
