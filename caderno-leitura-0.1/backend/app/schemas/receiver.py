"""F0.11.09 (spec 111): token de recepção e corpo compatível com a API v2 do Readwise."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

MAX_HIGHLIGHTS = 1000
MAX_TEXT = 20_000


class ReceiverTokenStatus(BaseModel):
    active: bool
    hint: str | None = None
    created_at: datetime | None = None
    last_used_at: datetime | None = None


class ReceiverTokenIssued(BaseModel):
    token: str = Field(..., description="Mostrado uma única vez")
    status: ReceiverTokenStatus


class ReadwiseHighlightIn(BaseModel):
    """Um destaque como o Readest (e o Readwise) envia; campos desconhecidos são ignorados."""

    model_config = ConfigDict(extra="ignore")

    text: str = Field(default="", max_length=MAX_TEXT)
    title: str | None = Field(default=None, max_length=2000)
    author: str | None = Field(default=None, max_length=2000)
    note: str | None = Field(default=None, max_length=MAX_TEXT)
    location: int | float | str | None = None
    location_type: str | None = Field(default=None, max_length=40)
    highlighted_at: str | None = Field(default=None, max_length=64)
    source_type: str | None = Field(default=None, max_length=60)
    chapter: str | None = Field(default=None, max_length=500)


class ReadwiseHighlightsIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    highlights: list[ReadwiseHighlightIn] = Field(default_factory=list)


class ReadwiseBookOut(BaseModel):
    """Resumo por livro no formato de resposta do Readwise."""

    id: int
    title: str
    author: str | None = None
    category: str = "books"
    source: str = "leitorum"
    modified_highlights: list[int] = Field(default_factory=list)
