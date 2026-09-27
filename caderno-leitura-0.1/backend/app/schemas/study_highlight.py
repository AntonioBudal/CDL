from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import InputModel, NonBlankText, OutputModel, RecordId

HighlightKind = Literal["highlight", "note", "quote", "hidden", "question"]
HighlightColor = Literal["yellow", "green", "blue", "pink", "purple"]
SectionName = Literal["summary", "explanation", "concepts", "references", "source_response"]


class StudyHighlightCreate(InputModel):
    section: SectionName
    start_offset: int = Field(default=0, ge=0)
    end_offset: int = Field(default=0, ge=0)
    selected_text: NonBlankText
    prefix: str = Field(default="", max_length=150)
    suffix: str = Field(default="", max_length=150)
    color: HighlightColor = "yellow"
    kind: HighlightKind = "highlight"
    note: str = Field(default="", max_length=10000)


class StudyHighlightUpdate(InputModel):
    color: HighlightColor | None = None
    kind: HighlightKind | None = None
    note: str | None = Field(default=None, max_length=10000)


class StudyHighlightRead(OutputModel):
    id: RecordId
    study_id: RecordId
    user_id: str
    section: SectionName
    start_offset: int
    end_offset: int
    selected_text: str
    prefix: str
    suffix: str
    color: HighlightColor
    kind: HighlightKind
    note: str
    created_at: datetime
    updated_at: datetime
