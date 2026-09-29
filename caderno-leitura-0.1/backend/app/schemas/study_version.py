from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import OutputModel, RecordId


class StudyVersionSummary(OutputModel):
    id: RecordId
    study_id: RecordId
    version_number: int
    user_id: str | None = None
    author_name: str | None = None
    change_summary: str = "Edição"
    char_count: int = 0
    highlights_count: int = 0
    is_current: bool = False
    created_at: datetime
    updated_at: datetime


class StudyVersionDetail(StudyVersionSummary):
    title: str
    summary: str
    explanation: str
    concepts: str
    references: str
    notes: str
    highlights: list[dict[str, Any]] = Field(default_factory=list)


DiffChunkType = Literal["equal", "insert", "delete"]
DiffSectionStatus = Literal["modified", "unchanged", "added", "removed"]


class DiffChunk(OutputModel):
    type: DiffChunkType
    text: str


class SectionDiff(OutputModel):
    status: DiffSectionStatus
    chunks: list[DiffChunk] = Field(default_factory=list)


class StudyDiffResponse(OutputModel):
    version_number: int
    target_version_number: int
    is_target_current: bool
    sections: dict[str, SectionDiff]
