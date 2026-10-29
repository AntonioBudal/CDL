from typing import Literal

from pydantic import Field

from app.schemas.common import InputModel, OutputModel

Section = Literal["summary", "explanation", "concepts", "references"]


class OrganizeLineInput(InputModel):
    text: str = Field(max_length=5_000)
    bbox: list[float] | None = Field(default=None, min_length=4, max_length=4, description="Caixa [x0, y0, x1, y1] da linha lida.")
    confidence: float | None = Field(default=None, ge=0, le=1)


class OrganizeRequest(InputModel):
    text: str = Field(description="Texto a distribuir entre as 4 seções; até 50 000 caracteres.")
    lines: list[OrganizeLineInput] | None = Field(
        default=None, max_length=2_000, description="Linhas lidas na digitalização, para usar a posição na página."
    )


class OrganizeSegmentRead(OutputModel):
    index: int
    start: int = Field(description="Início no texto recebido (pontos de código).")
    end: int
    text: str = Field(description="Igual a text[start:end]; o cliente usa este campo.")
    section: Section
    confidence: float = Field(ge=0, le=1)
    review: bool


class OrganizeSectionsRead(OutputModel):
    summary: str
    explanation: str
    concepts: str
    references: str


class OrganizeEngineRead(OutputModel):
    name: str
    version: str
    sha256: str
    adapter: int | None = None  # feature 091-C: estudos revisados, quando a sugestão veio do adaptador


class OrganizeWarningRead(OutputModel):
    code: Literal["suggestion", "single_section"]
    message: str


class OrganizeRead(OutputModel):
    sections: OrganizeSectionsRead
    segments: list[OrganizeSegmentRead]
    explicit_headings: bool
    review_count: int
    engine: OrganizeEngineRead
    elapsed_ms: int
    warnings: list[OrganizeWarningRead]


class OrganizeStatusRead(OutputModel):
    available: bool
    reason: Literal["not_installed", "integrity_failed"] | None
    version: str | None
