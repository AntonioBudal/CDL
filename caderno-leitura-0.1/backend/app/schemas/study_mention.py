from __future__ import annotations

from datetime import datetime

from app.schemas.common import OutputModel, RecordId


class BacklinkItemRead(OutputModel):
    id: RecordId
    source_study_id: RecordId
    source_study_title: str
    book_id: RecordId
    book_title: str
    chapter_id: RecordId
    chapter_name: str
    section: str
    mention_text: str
    context_snippet: str
    created_at: datetime


class BacklinksResponse(OutputModel):
    items: list[BacklinkItemRead]
    total: int


class StudyCandidateOption(OutputModel):
    id: RecordId
    title: str
    book_id: RecordId
    book_title: str
    chapter_id: RecordId
    chapter_name: str
    chapter_title: str = ""
