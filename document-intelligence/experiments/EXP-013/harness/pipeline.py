"""Pipeline do EXP-013: o do EXP-012 com escala automática da página.

Primeiro passo: detecção na imagem recebida e altura mediana das linhas; se ``options['target']``
for dado, a página é ampliada pelo fator inteiro mais próximo de ``target / altura`` (1 a 4) e a
detecção é refeita. As coordenadas devolvidas estão sempre na imagem recebida.

Roda no ambiente ``EXP-008/envs/ppocr`` como adaptador do supervisor. Etapas:

1. detecção de linhas PP-OCRv6 small (modelo embutido no wheel, SHA-256 conferido);
2. fusão de fragmentos com os parâmetros calibrados no EXP-008;
3. recorte desentortado de cada linha; ampliação 2× quando a altura for menor que ``MIN_HEIGHT`` px
   (regra do EXP-010);
4. leitura PP-OCRv6 small.

A correção lexical e a montagem do LDF ficam no ambiente do harness (``run.py``), porque dependem de
dados e do pacote principal. Sem rede.
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

MIN_HEIGHT = 32
MAX_SCALE = 4


def median_height(lines: list[dict[str, Any]]) -> float | None:
    """Altura mediana (px) das linhas detectadas, ou ``None`` se não houver linha."""
    heights = sorted(ln["bbox"][3] - ln["bbox"][1] for ln in lines)
    return float(heights[len(heights) // 2]) if heights else None


def scale_factor(height: float | None, target: float | None) -> int:
    """Fator inteiro de ampliação da página para as linhas chegarem perto de ``target`` px."""
    if not target or not height or height <= 0:
        return 1
    return int(max(1, min(MAX_SCALE, round(target / height))))


def to_original(line: dict[str, Any], scale: int) -> dict[str, Any]:
    """Leva caixa e contorno de volta às coordenadas da imagem recebida."""
    if scale == 1:
        return dict(line)
    return {
        **line,
        "bbox": [round(v / scale) for v in line["bbox"]],
        "polygon": [[round(x / scale, 1), round(y / scale, 1)] for x, y in line["polygon"]]
        if line.get("polygon")
        else None,
    }


def prepare_line(image: np.ndarray, min_height: int = MIN_HEIGHT) -> tuple[np.ndarray, int]:
    """Amplia 2× o recorte baixo demais; devolve o recorte e o fator usado."""
    if image.shape[0] < min_height:
        return cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC), 2
    return image, 1


class PagePipeline:
    def load(self, context: dict[str, Any]) -> None:
        import rapidocr
        from rapidocr import RapidOCR

        logging.getLogger("RapidOCR").setLevel(logging.ERROR)
        options = context["options"]
        models = Path(rapidocr.__file__).parent / "models"
        for name, expected in options["models"].items():
            if hashlib.sha256((models / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f"SHA-256 do modelo não confere: {name}")
        self._options = options
        self._merge = MergeParams(**options["merge"])
        self._engine = RapidOCR()

    def _detect(self, image: np.ndarray) -> list[dict[str, Any]]:
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
        return lines

    def predict(self, image_path: str) -> dict[str, Any]:
        original = cv2.imread(image_path, cv2.IMREAD_COLOR)
        lines = self._detect(original)
        height = median_height(lines)
        scale = scale_factor(height, self._options.get("target"))
        image = original
        if scale > 1:
            image = cv2.resize(original, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            lines = self._detect(image)
        out = []
        for line in merge_lines(lines, self._merge):
            crop, factor = prepare_line(
                crop_line(image, line.get("polygon") or box_points(line["bbox"]))
            )
            result = self._engine(crop, use_det=False, use_cls=False, use_rec=True)
            texts = list(getattr(result, "txts", None) or [])
            confidences = list(getattr(result, "scores", None) or [])
            out.append(
                {
                    **to_original(line, scale),
                    "text": str(texts[0]) if texts else "",
                    "rec_score": float(confidences[0]) if confidences else 0.0,
                    "upscaled": factor,
                }
            )
        return {"lines": out, "blocks": [], "page_scale": scale, "median_line_height": height}

    def describe(self) -> dict[str, Any]:
        return {
            "id": self._options.get("id"),
            "library": f"rapidocr {metadata.version('rapidocr')}",
            "min_height": MIN_HEIGHT,
            "target": self._options.get("target"),
            "merge": self._merge.to_dict(),
        }
