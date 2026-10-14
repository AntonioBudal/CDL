"""Adaptador do baseline clássico (sem aprendizado). Roda no ambiente do harness."""

from __future__ import annotations

from typing import Any

import cv2
from classic import ClassicParams, detect_lines


class ClassicDetector:
    def load(self, context: dict[str, Any]) -> None:
        given = context["options"].get("classic_params") or {}
        self._params = ClassicParams(**given)
        self._id = context["options"].get("id", "classic")

    def predict(self, image_path: str) -> dict[str, Any]:
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        lines, _, _ = detect_lines(image, self._params)
        return {"lines": lines, "blocks": []}

    def describe(self) -> dict[str, Any]:
        return {
            "id": self._id,
            "family": "clássico (OpenCV)",
            "opencv": cv2.__version__,
            "params": self._params.to_dict(),
        }
