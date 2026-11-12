"""F0.11.07 (spec 109): fontes do validador de paráfrase."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

ParaphraseSourceKind = Literal["quote", "capture"]


class ParaphraseSource(BaseModel):
    kind: ParaphraseSourceKind
    label: str
    text: str


class DeclaredQuote(BaseModel):
    """Trecho que o leitor marcou como citação literal neste estudo: não é verificado."""

    section: str
    text: str


class ParaphraseSources(BaseModel):
    sources: list[ParaphraseSource]
    declared_quotes: list[DeclaredQuote] = []
