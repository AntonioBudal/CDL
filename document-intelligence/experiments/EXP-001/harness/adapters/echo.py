"""Reconhecedor de referência ("eco"): devolve a transcrição de referência do manifesto.

Não é um modelo. Serve para validar o harness de ponta a ponta: lê cada arquivo de imagem,
confere o SHA-256 contra o manifesto e devolve o texto esperado (CER = WER = 0).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


class EchoRecognizer:
    def __init__(self) -> None:
        self._by_path: dict[str, dict[str, Any]] = {}

    def load(self, context: dict[str, Any]) -> None:
        root = Path(context["root"])
        for line in context["manifest"]["lines"]:
            self._by_path[str((root / line["image"]).resolve())] = line

    def recognize(self, image_path: str) -> str:
        line = self._by_path[str(Path(image_path).resolve())]
        digest = hashlib.sha256(Path(image_path).read_bytes()).hexdigest()
        if digest != line["sha256"]:
            raise ValueError(f"SHA-256 divergente do manifesto para a linha {line['id']}")
        return line["text"]

    def describe(self) -> dict[str, Any]:
        return {"id": "echo-reference", "kind": "reference", "weights": None}
