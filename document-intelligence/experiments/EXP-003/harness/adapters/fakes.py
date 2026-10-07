"""Detectores falsos para testar o supervisor e o avaliador. Não são modelos."""

from __future__ import annotations

import time
from typing import Any

from adapters.reference import ReferenceDetector

_CHUNK = 16 * 1024 * 1024


class ShiftedDetector(ReferenceDetector):
    """Desloca todas as caixas ``dx`` pixels para a direita (IoU conhecida: (w - dx) / (w + dx))."""

    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        self._dx = int(context["options"].get("dx", 0))
        self._drop_blocks = bool(context["options"].get("drop_blocks", False))

    def predict(self, image_path: str) -> dict[str, Any]:
        result = super().predict(image_path)
        dx = self._dx
        for item in result["lines"] + result["blocks"]:
            x0, y0, x1, y1 = item["bbox"]
            item["bbox"] = [x0 + dx, y0, x1 + dx, y1]
            if item.get("polygon"):
                item["polygon"] = [[x + dx, y] for x, y in item["polygon"]]
        if self._drop_blocks:
            result["blocks"] = []
        return result


class MemoryHogDetector(ReferenceDetector):
    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        total = int(context["options"].get("total_mib", 320)) * 1024 * 1024
        self._blocks = []
        while len(self._blocks) * _CHUNK < total:
            self._blocks.append(bytearray(b"\x01") * _CHUNK)
            time.sleep(0.03)


class SlowLoadDetector(ReferenceDetector):
    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        time.sleep(float(context["options"].get("load_seconds", 30)))


class SlowPageDetector(ReferenceDetector):
    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        self._delay = float(context["options"].get("page_seconds", 0.2))

    def predict(self, image_path: str) -> dict[str, Any]:
        time.sleep(self._delay)
        return super().predict(image_path)


class CrashingDetector(ReferenceDetector):
    def load(self, context: dict[str, Any]) -> None:
        raise RuntimeError("falha simulada na carga")
