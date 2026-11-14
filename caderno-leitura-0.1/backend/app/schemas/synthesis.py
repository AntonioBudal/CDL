"""F0.11.11 (spec 113): cadernos de síntese com transclusão."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, StringConstraints
from typing_extensions import Annotated

from app.schemas.common import InputModel, OutputModel, RecordId

MAX_BODY = 500_000
SynthesisTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]


class SynthesisCreate(InputModel):
    title: SynthesisTitle
    body: str = Field(default="", max_length=MAX_BODY)


class SynthesisPatch(InputModel):
    title: SynthesisTitle | None = None
    body: str | None = Field(default=None, max_length=MAX_BODY)
    version: int | None = Field(default=None, ge=1)


class SynthesisSummary(OutputModel):
    id: RecordId
    title: str
    embeds: int = 0
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class SynthesisRead(OutputModel):
    id: RecordId
    title: str
    body: str
    version: int
    created_at: datetime
    updated_at: datetime


class EmbedResolved(OutputModel):
    key: str
    kind: Literal["study", "section", "highlight"]
    available: bool
    study_id: int | None = None
    book_id: int | None = None
    title: str = ""
    book_title: str = ""
    chapter_name: str = ""
    section_label: str = ""
    markdown: str = ""
    note: str = ""


class SynthesisResolved(OutputModel):
    synthesis: SynthesisRead
    embeds: dict[str, EmbedResolved] = Field(default_factory=dict)
