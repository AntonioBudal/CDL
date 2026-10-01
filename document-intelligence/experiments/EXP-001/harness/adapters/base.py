"""Interface mínima de um reconhecedor de linha.

Os adaptadores rodam no processo filho, dentro do ambiente isolado de cada candidato; por isso
este módulo usa só a biblioteca padrão e é compatível com Python 3.10.
"""

from __future__ import annotations

from typing import Any, Protocol


class Recognizer(Protocol):
    def load(self, context: dict[str, Any]) -> None:
        """Carrega o modelo. ``context`` traz ``manifest``, ``root`` e ``options``."""

    def recognize(self, image_path: str) -> str:
        """Devolve a transcrição bruta da imagem de linha, sem correção posterior."""

    def describe(self) -> dict[str, Any]:
        """Identificação do reconhecedor (id, revisão, hashes dos pesos, parâmetros)."""
