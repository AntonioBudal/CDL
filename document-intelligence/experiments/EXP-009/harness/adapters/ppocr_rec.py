"""Adaptadores de leitura com o PP-OCRv6 (via ``rapidocr``). Rodam em ``EXP-008/envs/ppocr``.

* ``PPOCRLineReader``: recebe o recorte de uma linha e devolve o texto lido (só reconhecimento).
* ``PPOCRPageReader``: recebe a página, detecta as linhas, une os fragmentos com a fusão
  calibrada no EXP-008, recorta cada linha e a lê.

Os modelos são os embutidos no wheel, com SHA-256 conferido; o classificador de orientação não é
usado e nenhuma rede é acessada.
"""

from __future__ import annotations

import hashlib
import logging
from importlib import metadata
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from crop import box_points, crop_line
from merge import MergeParams, merge_lines


def _check(models: Path, options: dict[str, Any]) -> None:
    for name, expected in options["models"].items():
        if hashlib.sha256((models / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"SHA-256 do modelo não confere: {name}")


class _Base:
    def load(self, context: dict[str, Any]) -> None:
        import rapidocr
        from rapidocr import RapidOCR

        logging.getLogger("RapidOCR").setLevel(logging.ERROR)
        options = context["options"]
        _check(Path(rapidocr.__file__).parent / "models", options)
        self._options = options
        self._engine = RapidOCR()

    def _read(self, image: np.ndarray) -> tuple[str, float]:
        result = self._engine(image, use_det=False, use_cls=False, use_rec=True)
        texts = list(getattr(result, "txts", None) or [])
        scores = list(getattr(result, "scores", None) or [])
        if not texts:
            return "", 0.0
        return str(texts[0]), float(scores[0]) if scores else 0.0

    def describe(self) -> dict[str, Any]:
        import onnxruntime

        return {
            "id": self._options.get("id"),
            "library": f"rapidocr {metadata.version('rapidocr')}",
            "onnxruntime": onnxruntime.__version__,
            "models": sorted(self._options["models"]),
        }


class PPOCRLineReader(_Base):
    def predict(self, image_path: str) -> dict[str, Any]:
        text, score = self._read(cv2.imread(image_path, cv2.IMREAD_COLOR))
        return {"lines": [{"text": text, "score": score}], "blocks": []}


class PPOCRPageReader(_Base):
    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        self._merge = MergeParams(**self._options["merge"])

    def predict(self, image_path: str) -> dict[str, Any]:
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        detected = self._engine(image, use_det=True, use_cls=False, use_rec=False)
        boxes = getattr(detected, "boxes", None)
        scores = getattr(detected, "scores", None)
        lines = []
        if boxes is not None:
            for index, box in enumerate(np.asarray(boxes, dtype=np.float64).reshape(-1, 4, 2)):
                x0, y0 = box.min(axis=0)
                x1, y1 = box.max(axis=0)
                if x1 > x0 and y1 > y0:
                    lines.append(
                        {
                            "bbox": [round(x0), round(y0), round(x1), round(y1)],
                            "polygon": [[round(x), round(y)] for x, y in box],
                            "score": float(scores[index]) if scores is not None else 1.0,
                        }
                    )
        out = []
        for line in merge_lines(lines, self._merge):
            points = line.get("polygon") or box_points(line["bbox"])
            text, rec_score = self._read(crop_line(image, points))
            out.append({**line, "text": text, "rec_score": rec_score})
        return {"lines": out, "blocks": []}
