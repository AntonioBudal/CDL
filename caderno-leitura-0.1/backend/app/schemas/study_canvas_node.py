import math
from datetime import datetime
from pydantic import Field, field_validator

from app.schemas.common import InputModel, OutputModel, RecordId


class CanvasNodeItem(InputModel):
    study_id: RecordId
    pos_x: float = Field(..., description="Coordenada horizontal no mundo 2D")
    pos_y: float = Field(..., description="Coordenada vertical no mundo 2D")
    width: float | None = Field(default=None, gt=0, description="Largura customizada do card em pixels")
    height: float | None = Field(default=None, gt=0, description="Altura customizada do card em pixels")
    z_index: int = Field(default=0, ge=0, description="Ordem de empilhamento visual")
    color_tag: str | None = Field(default=None, max_length=32, description="Identificador cromático para agrupamento")

    @field_validator("pos_x", "pos_y", "width", "height")
    @classmethod
    def validate_finite_number(cls, v: float | None) -> float | None:
        if v is not None and (math.isnan(v) or math.isinf(v)):
            raise ValueError("As coordenadas e dimensões devem ser números finitos.")
        return v


class CanvasNodePatchRequest(InputModel):
    pos_x: float | None = None
    pos_y: float | None = None
    width: float | None = Field(default=None, gt=0)
    height: float | None = Field(default=None, gt=0)
    z_index: int | None = Field(default=None, ge=0)
    color_tag: str | None = Field(default=None, max_length=32)

    @field_validator("pos_x", "pos_y", "width", "height")
    @classmethod
    def validate_finite_number(cls, v: float | None) -> float | None:
        if v is not None and (math.isnan(v) or math.isinf(v)):
            raise ValueError("As coordenadas e dimensões devem ser números finitos.")
        return v


class CanvasBatchUpdateRequest(InputModel):
    nodes: list[CanvasNodeItem] = Field(..., min_length=1, description="Lista de coordenadas a sincronizar")


class CanvasNodeRead(OutputModel):
    id: RecordId
    study_id: RecordId
    book_id: RecordId
    pos_x: float
    pos_y: float
    width: float | None
    height: float | None
    z_index: int
    color_tag: str | None
    updated_at: datetime


class BookCanvasResponse(OutputModel):
    book_id: RecordId
    nodes: list[CanvasNodeRead]
