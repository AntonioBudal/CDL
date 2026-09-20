import math
from datetime import datetime
from enum import Enum
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from app.schemas.common import InputModel, OutputModel, RecordId

ReadingStatusLiteral = Literal["rascunho", "em_estudo", "revisado", "concluido"]


class ReadingStatus(str, Enum):
    RASCUNHO = "rascunho"
    EM_ESTUDO = "em_estudo"
    REVISADO = "revisado"
    CONCLUIDO = "concluido"


class StudyStatusUpdate(InputModel):
    reading_status: ReadingStatusLiteral
    expected_updated_at: datetime | None = Field(default=None, strict=False)


class StudyStatusResponse(OutputModel):
    id: int
    reading_status: ReadingStatusLiteral
    updated_at: datetime


class CanvasFrameCreate(InputModel):
    title: str = Field(min_length=1, max_length=100)
    color: str = Field(default="neutral", max_length=32)
    pos_x: float = Field(default=0.0, strict=False)
    pos_y: float = Field(default=0.0, strict=False)
    width: float = Field(default=400.0, ge=100.0, strict=False)
    height: float = Field(default=300.0, ge=80.0, strict=False)

    @field_validator("pos_x", "pos_y", "width", "height")
    @classmethod
    def validate_finite_number(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("As coordenadas e dimensões devem ser números finitos.")
        return v


class CanvasFrameUpdate(InputModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=32)
    pos_x: float | None = Field(default=None, strict=False)
    pos_y: float | None = Field(default=None, strict=False)
    width: float | None = Field(default=None, ge=100.0, strict=False)
    height: float | None = Field(default=None, ge=80.0, strict=False)

    @field_validator("pos_x", "pos_y", "width", "height")
    @classmethod
    def validate_finite_number(cls, v: float | None) -> float | None:
        if v is not None and (math.isnan(v) or math.isinf(v)):
            raise ValueError("As coordenadas e dimensões devem ser números finitos.")
        return v

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> Self:
        payload_fields = self.model_fields_set
        if not payload_fields:
            raise ValueError("Envie pelo menos um campo para alterar na moldura.")
        return self


class CanvasFrameItem(OutputModel):
    id: int
    book_id: int
    title: str
    color: str
    pos_x: float
    pos_y: float
    width: float
    height: float
    created_at: datetime
    updated_at: datetime
