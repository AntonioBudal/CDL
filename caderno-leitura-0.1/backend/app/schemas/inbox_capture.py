from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import InputModel, NonBlankText, OutputModel, RecordId

InboxStatus = Literal["inbox", "promoted", "linked", "archived"]


class InboxCaptureCreate(InputModel):
    content: NonBlankText
    source_hint: str | None = Field(default=None, max_length=500)
    book_id: RecordId | None = None


class InboxCapturePatch(InputModel):
    content: NonBlankText | None = None
    source_hint: str | None = Field(default=None, max_length=500)
    book_id: RecordId | None = None
    status: InboxStatus | None = None


class InboxCaptureRead(OutputModel):
    id: RecordId
    user_id: str
    book_id: RecordId | None = None
    book_title: str | None = None
    content: str
    source_hint: str | None = None
    status: InboxStatus
    promoted_study_id: RecordId | None = None
    promoted_study_title: str | None = None
    created_at: datetime
    updated_at: datetime


class InboxCountResponse(OutputModel):
    count: int = Field(..., ge=0)


class InboxPromoteRequest(InputModel):
    study_id: RecordId


class InboxLinkRequest(InputModel):
    target_study_id: RecordId
    target_section: Literal["summary", "explanation", "concepts", "references", "notes"] = "references"
