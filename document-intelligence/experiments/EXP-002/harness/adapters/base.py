"""Interface mínima de um detector de layout.

Os adaptadores rodam no processo filho, dentro do ambiente isolado de cada candidato; por isso este
módulo usa só a biblioteca padrão e é compatível com Python 3.10.
"""

from __future__ import annotations

from typing import Any, Protocol


class Detector(Protocol):
    def load(self, context: dict[str, Any]) -> None:
        """Carrega o modelo. ``context`` traz ``manifest``, ``root`` e ``options``."""

    def predict(self, image_path: str) -> dict[str, Any]:
        """Devolve ``{"lines": [...], "blocks": [...]}`` em coordenadas da imagem recebida.

        Cada linha: ``{"bbox": [x0, y0, x1, y1], "polygon": [[x, y], ...] | None, "score": float}``.
        Cada bloco: ``{"type": str, "bbox": [...], "score": float}``.
        """

    def describe(self) -> dict[str, Any]:
        """Identificação do detector (id, revisão, hashes dos pesos, parâmetros)."""
