"""Modelo Pydantic do LDF 2.0.

A fonte normativa é o JSON Schema (``schemas/ldf-2.0.schema.json``). Este modelo é um espelho
tipado para uso em Python; ``tests/ldf/test_models_parity.py`` falha se ele divergir do schema.
As regras R1–R9 não estão aqui: use ``leitorum_di.contracts.ldf.validate``.

Campos opcionais são declarados com ``Field(default=None)`` sem ``| None`` no tipo: assim o campo
pode faltar, mas ``null`` explícito é rejeitado, como no schema. Serialize com ``to_dict()``.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

IDENTIFIER = r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
TIMESTAMP = (
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"
)
POINTER = r"^(/[^/]*)*$"

Identifier = Annotated[str, Field(pattern=IDENTIFIER)]
Timestamp = Annotated[str, Field(pattern=TIMESTAMP)]
Confidence = Annotated[float, Field(ge=0, le=1)]
Point = Annotated[list[float], Field(min_length=2, max_length=2)]
BBox = Annotated[list[float], Field(min_length=4, max_length=4)]
Polygon = Annotated[list[Point], Field(min_length=3)]
NonEmpty = Annotated[str, Field(min_length=1)]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SourceImage(_Model):
    filename: NonEmpty
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    dpi: int = Field(default=None, ge=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class Rectification(_Model):
    method: NonEmpty
    source_quad: list[Point] = Field(min_length=4, max_length=4)
    output_size: list[Annotated[int, Field(ge=1)]] = Field(min_length=2, max_length=2)
    homography: list[Annotated[list[float], Field(min_length=3, max_length=3)]] = Field(
        min_length=3, max_length=3
    )


class CoordinateSpace(_Model):
    frame: Literal["source_image"]
    unit: Literal["pixel"]
    rectification: Rectification = Field(default=None)


class Component(_Model):
    name: NonEmpty
    version: NonEmpty
    revision: NonEmpty = Field(default=None)
    license: NonEmpty
    license_status: Literal["VERIFIED", "NEEDS VALIDATION", "N/A"]


class Stage(_Model):
    status: Literal["completed", "not_run", "failed"]
    component: Component = Field(default=None)
    elapsed_ms: float = Field(default=None, ge=0)
    error: NonEmpty = Field(default=None)


class Stages(_Model):
    layout: Stage
    reading_order: Stage
    recognition: Stage
    semantics: Stage
    diagrams: Stage


class Pipeline(_Model):
    stages: Stages


class Line(_Model):
    id: Identifier
    bbox: BBox
    polygon: Polygon = Field(default=None)
    detection_confidence: Confidence = Field(default=None)
    text: str = Field(default=None)
    confidence: Confidence = Field(default=None)
    is_handwritten: bool = Field(default=None)


class Recognition(_Model):
    lines: list[Line]


class Region(_Model):
    id: Identifier
    type: Literal["title", "paragraph", "margin_note", "graphic"]
    bbox: BBox
    polygon: Polygon = Field(default=None)
    line_ids: list[Identifier]
    confidence: Confidence = Field(default=None)


class DiagramNode(_Model):
    id: Identifier
    label: str
    bbox: BBox
    line_ids: list[Identifier] = Field(default=None)


class DiagramEdge(_Model):
    id: Identifier
    source: Identifier
    target: Identifier
    type: Literal["arrow", "line", "bidirectional_arrow", "dashed_line"]
    label: str = Field(default=None)
    confidence: Confidence = Field(default=None)


class Diagram(_Model):
    id: Identifier
    region_id: Identifier
    nodes: list[DiagramNode]
    edges: list[DiagramEdge]


class Structure(_Model):
    regions: list[Region]
    reading_order: list[Identifier]
    diagrams: list[Diagram]


class Section(_Model):
    id: Identifier
    role: Literal[
        "title", "summary", "concept", "question", "quote", "example", "margin_note", "other"
    ]
    region_ids: list[Identifier]
    label: str = Field(default=None)
    confidence: Confidence = Field(default=None)


class Entity(_Model):
    id: Identifier
    type: NonEmpty
    text_reference: str
    region_ids: list[Identifier]
    confidence: Confidence = Field(default=None)


class Semantics(_Model):
    """Provisória até o EXP-004."""

    sections: list[Section]
    entities: list[Entity]


class CorrectionTarget(_Model):
    collection: Literal[
        "recognition.lines",
        "structure.regions",
        "structure.reading_order",
        "structure.diagrams",
        "semantics.sections",
        "semantics.entities",
    ]
    id: Identifier = Field(default=None)


class Operation(_Model):
    op: Literal["add", "remove", "replace", "move", "copy", "test"]
    path: str = Field(pattern=POINTER)
    from_: str = Field(default=None, alias="from", pattern=POINTER)
    value: Any = Field(default=None)


class Correction(_Model):
    id: Identifier
    author: NonEmpty
    timestamp: Timestamp
    reason: str = Field(default=None)
    target: CorrectionTarget
    ops: list[Operation] = Field(min_length=1)


class LDFDocument(_Model):
    """Documento LDF 2.0: uma página, coordenadas na fotografia original."""

    ldf_version: str = Field(pattern=r"^2\.0\.[0-9]+$")
    document_id: Identifier
    created_at: Timestamp
    source_image: SourceImage
    coordinate_space: CoordinateSpace
    pipeline: Pipeline
    recognition: Recognition
    structure: Structure
    semantics: Semantics = Field(default=None)
    human_corrections: list[Correction]

    def to_dict(self) -> dict[str, Any]:
        """Serializa só os campos presentes, com os nomes do schema."""
        return self.model_dump(by_alias=True, exclude_unset=True)
