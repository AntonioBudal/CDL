from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import InputModel, OutputModel, RecordId

ReviewRating = Literal["easy", "medium", "hard"]


class ReviewRecordRequest(InputModel):
    rating: ReviewRating


class ReviewRecordResponse(OutputModel):
    id: RecordId
    last_reviewed_at: datetime
    review_count: int
    last_rating: ReviewRating


class ReviewItemRead(OutputModel):
    id: RecordId
    study_id: RecordId
    study_title: str
    book_id: RecordId
    book_title: str
    chapter_id: RecordId
    chapter_name: str
    kind: str
    section: str
    question_text: str
    expected_answer: str
    context_prefix: str = ""
    context_suffix: str = ""
    last_reviewed_at: datetime | None = None
    review_count: int = 0
    last_rating: ReviewRating | None = None


class ReviewBookItem(OutputModel):
    book_id: RecordId
    title: str
    items_count: int


class ReviewStatsResponse(OutputModel):
    total_eligible: int
    total_questions: int
    total_hidden: int
    reviewed_today: int
    pending_review: int
    books: list[ReviewBookItem] = Field(default_factory=list)
