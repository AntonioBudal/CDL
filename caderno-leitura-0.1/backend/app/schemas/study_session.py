from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.review import ReviewItemRead

SessionScopeType = Literal["quick", "book", "all"]
SessionStatus = Literal["in_progress", "completed", "interrupted"]
ItemRating = Literal["easy", "medium", "hard"]
SessionRating = ItemRating



class StudySessionStartRequest(BaseModel):
    scope_type: SessionScopeType = "quick"
    book_id: Optional[int] = None
    limit: Optional[int] = Field(default=10, ge=1, le=100)


class StudySessionItemAnswerRequest(BaseModel):
    highlight_id: int
    rating: ItemRating
    time_spent_seconds: int = 0


class StudySessionCompleteRequest(BaseModel):
    duration_seconds: Optional[int] = None


class StudySessionItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    highlight_id: int
    rating: ItemRating
    time_spent_seconds: int
    answered_at: datetime


class StudySessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    book_id: Optional[int] = None
    book_title: Optional[str] = None
    scope_type: SessionScopeType
    status: SessionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_items: int
    completed_items: int
    easy_count: int
    medium_count: int
    hard_count: int
    duration_seconds: int


class StudySessionDetailResponse(StudySessionResponse):
    items: list[StudySessionItemResponse] = []
    pending_cards: list[ReviewItemRead] = []


class StudySessionSummaryResponse(BaseModel):
    session: StudySessionResponse
    accuracy_rate: float
    next_reviews_summary: dict[str, int]
