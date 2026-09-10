from datetime import datetime
from typing import Self

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.common import InputModel, NonBlankText, OutputModel, RecordId

ANALYSIS_FIELDS = ("summary", "explanation", "concepts", "references")
ANALYSIS_REQUIRED_MESSAGE = "Preencha pelo menos uma das quatro seções da análise."


class StudyCreate(InputModel):
    chapter_id: RecordId
    title: str | None = Field(default=None, description="Se vazio ou omitido, será gerado a partir do capítulo e da localização.")
    location: str = ""
    source_response: str = ""
    summary: str = ""
    explanation: str = ""
    concepts: str = ""
    references: str = ""
    notes: str = ""

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @model_validator(mode="after")
    def require_analysis(self) -> Self:
        if not any(getattr(self, name).strip() for name in ANALYSIS_FIELDS):
            raise ValueError(ANALYSIS_REQUIRED_MESSAGE)
        return self


class StudyPatch(InputModel):
    """Omitir conserva o valor atual; usar string vazia limpa um campo opcional."""

    model_config = ConfigDict(json_schema_extra={"examples": [{"explanation": "Explicação revisada."}]})

    title: NonBlankText | None = None
    location: str | None = None
    summary: str | None = None
    explanation: str | None = None
    concepts: str | None = None
    references: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def require_changes_without_null(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Envie pelo menos um campo para alterar.")
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"O campo '{name}' não aceita null. Omita-o para preservar o valor atual.")
        return self


class StudySummary(OutputModel):
    id: int
    chapter_id: int
    title: str
    location: str
    created_at: datetime
    updated_at: datetime


class StudyRead(StudySummary):
    source_response: str
    summary: str
    explanation: str
    concepts: str
    references: str
    notes: str
