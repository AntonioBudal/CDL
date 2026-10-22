"""Efeito da margem vazia à direita na leitura (ONNX Runtime, uma linha por vez).

A linha é redimensionada para 48 px de altura e completada com zeros (cinza médio, após a
normalização) até
``largura + extra`` (arredondado para múltiplo de 32) ou até uma largura fixa. Grava predições no
formato do
``score.py`` para o conjunto pedido.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import onnx
import onnxruntime as ort
from model import ONNX_MODEL

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-014"


def prepare(image: np.ndarray, extra: int = 0, fixed: int | None = None) -> np.ndarray:
    h, w = image.shape[:2]
    resized_w = math.ceil(48 * w / h)
    resized = cv2.resize(image, (resized_w, 48)).astype(np.float32)
    resized = (resized.transpose(2, 0, 1) / 255 - 0.5) / 0.5
    width = max(320, resized_w + extra)
    if fixed:
        width = max(width, fixed)
    width = math.ceil(width / 32) * 32
    out = np.zeros((1, 3, 48, width), dtype=np.float32)
    out[0, :, :, :resized_w] = resized
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    name = sys.argv[1]
    variants = list(sys.argv[2].split(","))
    session = ort.InferenceSession(str(ONNX_MODEL), providers=["CPUExecutionProvider"])
    meta = {p.key: p.value for p in onnx.load(str(ONNX_MODEL)).metadata_props}
    characters = ["blank", *meta["character"].splitlines(), " "]
    items = json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
    for variant in variants:
        kind, value = variant[0], int(variant[1:])
        out = {}
        for item in items:
            image = cv2.imread(str(ROOT / item["image"]), cv2.IMREAD_COLOR)
            tensor = prepare(image, extra=value) if kind == "e" else prepare(image, fixed=value)
            probs = session.run(None, {"x": tensor})[0][0]
            text, previous = [], None
            for token in probs.argmax(-1):
                if token != previous and token != 0:
                    text.append(characters[token])
                previous = token
            out[item["id"]] = "".join(text)
        path = DATA / f"pred-pad-{variant}-{name}.json"
        path.write_text(
            json.dumps({"set": name, "items": out}, ensure_ascii=False), encoding="utf-8"
        )
        print(variant, "->", path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
