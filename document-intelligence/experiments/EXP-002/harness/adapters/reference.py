"""Detector de referência: devolve a verdade de chão do manifesto. Não é um modelo.

Valida o harness de ponta a ponta: lê cada imagem, confere o SHA-256 contra o manifesto e devolve
linhas e blocos exatos (F1 = mAP = 1).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


class ReferenceDetector:
    def __init__(self) -> None:
        self._by_path: dict[str, dict[str, Any]] = {}

    def load(self, context: dict[str, Any]) -> None:
        root = Path(context["root"])
        for page in context["manifest"]["pages"]:
            self._by_path[str((root / page["image"]).resolve())] = page

    def _page(self, image_path: str) -> dict[str, Any]:
        page = self._by_path[str(Path(image_path).resolve())]
        if hashlib.sha256(Path(image_path).read_bytes()).hexdigest() != page["sha256"]:
            raise ValueError(f"SHA-256 divergente do manifesto para a página {page['id']}")
        return page

    def predict(self, image_path: str) -> dict[str, Any]:
        page = self._page(image_path)
        return {
            "lines": [
                {"bbox": ln["bbox"], "polygon": ln["polygon"], "score": 1.0} for ln in page["lines"]
            ],
            "blocks": [
                {"type": b["type"], "bbox": b["bbox"], "score": 1.0} for b in page["blocks"]
            ],
        }

    def describe(self) -> dict[str, Any]:
        return {"id": "reference", "kind": "reference", "weights": None}
