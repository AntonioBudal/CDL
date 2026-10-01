"""Modelos Pydantic para o Leitorum Document Format (LDF 1.0).

Este arquivo estabelece os contratos de dados estáticos para troca de informações
entre o Document Intelligence e o produto principal Leitorum.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Caixa delimitadora normalizada ou em coordenadas de pixel [x_min, y_min, x_max, y_max]."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float


class LineRecognition(BaseModel):
    """Linha de texto individual reconhecida."""

    id: str
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    bounding_box: list[float] | None = None


class RecognitionPayload(BaseModel):
    """Camada 1: Reconhecimento físico direto (OCR/HTR de baixo nível)."""

    engine: str
    lines: list[LineRecognition] = Field(default_factory=list)


class StructuralBlock(BaseModel):
    """Bloco ou região espacial agrupada."""

    id: str
    type: Literal["paragraph", "title", "list", "diagram_region", "margin_note"]
    line_ids: list[str] = Field(default_factory=list)
    reading_order: int


class StructurePayload(BaseModel):
    """Camada 2: Análise espacial, blocos e ordem de leitura."""

    blocks: list[StructuralBlock] = Field(default_factory=list)


class SemanticConcept(BaseModel):
    """Elemento semântico de alto nível classificado."""

    id: str
    category: Literal[
        "concept",
        "explanation",
        "summary",
        "reference",
        "citation",
        "question",
        "observation",
        "example",
    ]
    text: str
    source_block_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class DiagramConnection(BaseModel):
    """Relação ou aresta orientada em um diagrama ou mapa conceitual."""

    source_id: str
    target_id: str
    relation_type: str = "points_to"


class SemanticsPayload(BaseModel):
    """Camada 3: Interpretação semântica e relações conceituais."""

    concepts: list[SemanticConcept] = Field(default_factory=list)
    diagram_connections: list[DiagramConnection] = Field(default_factory=list)


class DocumentPayload(BaseModel):
    """Container para as três camadas de análise documental."""

    recognition: RecognitionPayload
    structure: StructurePayload
    semantics: SemanticsPayload


class LDFDocument(BaseModel):
    """Documento no formato oficial Leitorum Document Format (LDF 1.0)."""

    version: str = "1.0.0"
    document: DocumentPayload
    human_corrections: list[dict[str, Any]] = Field(default_factory=list)
