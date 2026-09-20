from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import InputModel, OutputModel, RecordId

RelationTypeEnum = Literal[
    "relacionado_com",
    "complementa",
    "contradiz",
    "depende_de",
    "mesmo_tema",
    "desdobramento_de",
]


class StudyRelationCreate(InputModel):
    target_study_id: RecordId
    relation_type: RelationTypeEnum
    description: str = Field(default="", max_length=500)


class StudyRelationUpdate(InputModel):
    relation_type: RelationTypeEnum | None = None
    description: str | None = Field(default=None, max_length=500)


class ConnectedStudySummary(OutputModel):
    id: RecordId
    title: str
    book_id: RecordId
    book_title: str
    chapter_id: RecordId
    chapter_title: str


class StudyRelationItem(OutputModel):
    id: RecordId
    source_study_id: RecordId
    target_study_id: RecordId
    relation_type: RelationTypeEnum
    description: str
    created_at: datetime
    connected_study: ConnectedStudySummary


class StudyRelationsResponse(OutputModel):
    study_id: RecordId
    outbound: list[StudyRelationItem]
    inbound: list[StudyRelationItem]


class CandidateStudyItem(OutputModel):
    id: RecordId
    title: str
    book_id: RecordId
    book_title: str
    chapter_id: RecordId
    chapter_title: str


class BookCanvasRelationItem(OutputModel):
    id: RecordId
    source_study_id: RecordId
    target_study_id: RecordId
    relation_type: RelationTypeEnum
    description: str
