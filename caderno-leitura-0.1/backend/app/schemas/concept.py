"""F0.11.06 (spec 108): léxico de conceitos derivado dos estudos."""
from __future__ import annotations

from pydantic import Field

from app.schemas.common import OutputModel, RecordId


class ConceptSummary(OutputModel):
    key: str
    term: str
    definitions: int = 0
    mentions: int = 0
    books: int = 0


class ConceptListResponse(OutputModel):
    items: list[ConceptSummary] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 100


class ConceptOccurrenceRead(OutputModel):
    term: str
    text: str
    study_id: RecordId
    study_title: str
    book_id: RecordId
    book_title: str
    chapter_name: str = ""


class ConceptDetail(OutputModel):
    key: str
    term: str
    definitions: list[ConceptOccurrenceRead] = Field(default_factory=list)
    mentions: list[ConceptOccurrenceRead] = Field(default_factory=list)


class ConceptCandidate(OutputModel):
    key: str
    term: str
    definitions: int = 0
