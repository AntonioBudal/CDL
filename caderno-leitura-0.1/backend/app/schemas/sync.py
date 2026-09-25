from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import Field

from app.schemas.book import BookRead
from app.schemas.common import OutputModel
from app.schemas.preferences import UserPreferenceRead
from app.schemas.study import StudyRead
from app.schemas.study_canvas_node import CanvasNodeRead


class ConflictErrorResponse(OutputModel):
    detail: str = Field(
        default="Conflito de concorrência: o registro foi modificado em outro dispositivo.",
        description="Mensagem descritiva do conflito de escrita.",
    )
    entity_id: int
    entity_type: str = Field(..., description="Tipo da entidade em conflito: 'study', 'book' ou 'preference'")
    server_version: int = Field(..., description="Versão atualizada vigente no servidor.")
    server_updated_at: datetime = Field(..., description="Timestamp de atualização no servidor.")
    server_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Estado completo do registro no servidor para comparação.",
    )


class SyncDeletedItems(OutputModel):
    book_ids: list[int] = Field(default_factory=list)
    study_ids: list[int] = Field(default_factory=list)


class SyncUpdatedItems(OutputModel):
    books: list[BookRead] = Field(default_factory=list)
    studies: list[StudyRead] = Field(default_factory=list)
    canvas_nodes: list[CanvasNodeRead] = Field(default_factory=list)
    preferences: UserPreferenceRead | None = None


class SyncChangesResponse(OutputModel):
    server_time: datetime = Field(..., description="Carimbo temporal UTC emitido pelo servidor.")
    updated: SyncUpdatedItems = Field(default_factory=SyncUpdatedItems)
    deleted: SyncDeletedItems = Field(default_factory=SyncDeletedItems)
