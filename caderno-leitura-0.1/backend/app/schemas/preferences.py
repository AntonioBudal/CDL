from __future__ import annotations

from datetime import datetime
from pydantic import Field

from app.schemas.common import InputModel, OutputModel


VALID_SUPERCLASSES = ("zero-g", "mecanica", "invisivel", "dimensional", "monolitica")
VALID_VIEW_MODES = ("grid", "list", "tree", "canvas", "cockpit")
VALID_FONT_FAMILIES = ("garamond", "sans", "dyslexic")
VALID_THEME_MODES = ("dark", "light", "e-ink")


import json
from typing import Any
from pydantic import field_validator

class UserPreferenceRead(OutputModel):
    user_id: str
    active_superclass: str = "mecanica"
    superclass_intensity: float = 1.0
    preferred_view_mode: str = "grid"
    tree_collapsed_state: list[int] = Field(default_factory=list)
    font_family: str = "garamond"
    font_scale: float = 1.0
    theme_mode: str = "dark"
    version: int = 1
    updated_at: datetime

    @field_validator("tree_collapsed_state", mode="before")
    @classmethod
    def parse_collapsed_state(cls, value: Any) -> list[int]:
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return [int(x) for x in parsed if isinstance(x, (int, str)) and str(x).isdigit()]
            except (json.JSONDecodeError, ValueError):
                return []
        if isinstance(value, list):
            return [int(x) for x in value]
        return []


class UserPreferenceUpdate(InputModel):
    active_superclass: str | None = Field(default=None, description="Superclasse cinemática ativa")
    superclass_intensity: float | None = Field(default=None, ge=0.0, le=2.0, description="Intensidade física [0.0 - 2.0]")
    preferred_view_mode: str | None = Field(default=None, description="Modo de visualização preferido")
    tree_collapsed_state: list[int] | None = Field(default=None, description="IDs recolhidos na árvore")
    font_family: str | None = Field(default=None, description="Fonte de leitura")
    font_scale: float | None = Field(default=None, ge=0.7, le=1.6, description="Escala de fonte")
    theme_mode: str | None = Field(default=None, description="Tema de interface")
    expected_version: int | None = Field(default=None, ge=1, description="Versão esperada para OCC")
