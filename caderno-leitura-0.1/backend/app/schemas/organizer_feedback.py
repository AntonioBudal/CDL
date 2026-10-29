"""Corpo do envio silencioso do feedback do organizador (feature 091-B, ``POST /api/studies/{id}/organizer-feedback``)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Section = Literal["summary", "explanation", "concepts", "references"]


class FeedbackEngine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(max_length=16)
    sha256: str = Field(max_length=64)
    adapter: int | None = None


class FeedbackSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    index: int = Field(ge=0)
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    section: Section
    confidence: float = Field(ge=0.0, le=1.0)
    review: bool


class FeedbackLine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(max_length=5_000)
    bbox: list[float] | None = Field(default=None, min_length=4, max_length=4)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class FeedbackSuggestion(BaseModel):
    """O que o organizador sugeriu, como o navegador recebeu: o texto organizado e os trechos."""

    model_config = ConfigDict(extra="forbid")

    engine: FeedbackEngine
    outcome: Literal["saved", "reverted"]
    text: str = Field(max_length=50_000)
    segments: list[FeedbackSegment] = Field(max_length=400)
    # Linhas com posição enviadas ao organizador (091-C, C-Q4): sem elas, o adaptador não realinha a página.
    lines: list[FeedbackLine] | None = Field(default=None, max_length=400)

    @model_validator(mode="after")
    def segments_inside_text(self) -> FeedbackSuggestion:
        for segment in self.segments:
            if not segment.start < segment.end <= len(self.text):
                raise ValueError("Trecho fora do texto organizado.")
        return self


class OrganizerFeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin: Literal["digitize", "import"]
    organizer: FeedbackSuggestion | None = None
