"""Adaptador do detector de linhas de texto PP-OCR (via ``rapidocr`` + ONNX Runtime).

Roda em ``envs/ppocr``. Usa só a etapa de detecção: o classificador de orientação e o
reconhecedor de texto do pacote não são chamados. O modelo é o que vem dentro do wheel
(``PP-OCRv6_det_small.onnx``); o SHA-256 é conferido antes da carga, e nenhuma rede é usada.
"""

from __future__ import annotations

import hashlib
import logging
from importlib import metadata
from pathlib import Path
from typing import Any

import cv2
import numpy as np


class PPOCRDetector:
    def load(self, context: dict[str, Any]) -> None:
        import rapidocr
        from rapidocr import RapidOCR

        options = context["options"]
        logging.getLogger("RapidOCR").setLevel(logging.ERROR)
        model = Path(rapidocr.__file__).parent / "models" / options["model_file"]
        digest = hashlib.sha256(model.read_bytes()).hexdigest()
        if digest != options["model_sha256"]:
            raise ValueError(f"SHA-256 do modelo não confere: {model.name}")
        self._id = options.get("id")
        self._model = model.name
        self._version = metadata.version("rapidocr")
        self._engine = RapidOCR()

    def predict(self, image_path: str) -> dict[str, Any]:
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        result = self._engine(image, use_det=True, use_cls=False, use_rec=False)
        boxes = getattr(result, "boxes", None)
        scores = getattr(result, "scores", None)
        lines = []
        if boxes is not None:
            for index, box in enumerate(np.asarray(boxes, dtype=np.float64).reshape(-1, 4, 2)):
                x0, y0 = box.min(axis=0)
                x1, y1 = box.max(axis=0)
                if x1 <= x0 or y1 <= y0:
                    continue
                lines.append(
                    {
                        "bbox": [round(x0), round(y0), round(x1), round(y1)],
                        "polygon": [[round(x), round(y)] for x, y in box],
                        "score": float(scores[index]) if scores is not None else 1.0,
                    }
                )
        return {"lines": lines, "blocks": []}

    def describe(self) -> dict[str, Any]:
        import onnxruntime

        return {
            "id": self._id,
            "family": "DBNet (PP-OCR)",
            "library": f"rapidocr {self._version}",
            "onnxruntime": onnxruntime.__version__,
            "model": self._model,
        }
