"""Leitor de linha com um reconhecedor PP-OCR escolhido, opcionalmente ampliando o recorte.

Roda em ``EXP-008/envs/ppocr``. Opções: ``model`` (``small`` embutido no wheel, ou caminho de um
``.onnx``
baixado, com SHA-256 conferido), ``ocr_version``, ``model_type``, ``lang_type`` e ``scale`` (fator
de
ampliação bicúbica do recorte antes da leitura). Sem rede.
"""

from __future__ import annotations

import hashlib
import logging
from importlib import metadata
from pathlib import Path
from typing import Any

import cv2
import numpy as np


def scaled(image: np.ndarray, scale: float) -> np.ndarray:
    if scale == 1:
        return image
    return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


class PPOCRLineReader:
    def load(self, context: dict[str, Any]) -> None:
        import rapidocr
        from rapidocr import LangRec, ModelType, OCRVersion, RapidOCR

        logging.getLogger("RapidOCR").setLevel(logging.ERROR)
        options = context["options"]
        path = Path(options["model_path"]) if options.get("model_path") else None
        if path is None:
            path = Path(rapidocr.__file__).parent / "models" / "PP-OCRv6_rec_small.onnx"
        if hashlib.sha256(path.read_bytes()).hexdigest() != options["model_sha256"]:
            raise ValueError(f"SHA-256 do modelo não confere: {path.name}")
        params: dict[str, Any] = {}
        if options.get("model_path"):
            params = {
                "Rec.model_path": str(path),
                "Rec.ocr_version": OCRVersion(options["ocr_version"]),
                "Rec.model_type": ModelType(options["model_type"]),
                "Rec.lang_type": LangRec(options["lang_type"]),
            }
        self._options = options
        self._scale = float(options.get("scale", 1))
        self._engine = RapidOCR(params=params)

    def predict(self, image_path: str) -> dict[str, Any]:
        image = scaled(cv2.imread(image_path, cv2.IMREAD_COLOR), self._scale)
        result = self._engine(image, use_det=False, use_cls=False, use_rec=True)
        texts = list(getattr(result, "txts", None) or [])
        scores = list(getattr(result, "scores", None) or [])
        text = str(texts[0]) if texts else ""
        score = float(scores[0]) if scores else 0.0
        return {"lines": [{"text": text, "score": score}], "blocks": []}

    def describe(self) -> dict[str, Any]:
        import onnxruntime

        return {
            "id": self._options.get("id"),
            "library": f"rapidocr {metadata.version('rapidocr')}",
            "onnxruntime": onnxruntime.__version__,
            "scale": self._scale,
        }
