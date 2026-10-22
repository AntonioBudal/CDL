"""Isola a diferença entre a leitura pelo ``rapidocr`` (38,5 %) e pela conversão PyTorch (28,0 %).

Lê as 398 linhas do EXP-001 com o ONNX Runtime em três variantes de pré-processamento e grava as
predições no formato do ``score.py``:

* ``exact``: altura 48, largura ``ceil(48·w/h)`` (mínimo 320), como o ``TextRecognizer`` do pacote;
* ``mult32``: como ``exact``, completando a largura até múltiplo de 32 (o que a conversão PyTorch
  usa);
* ``package``: antes, o redimensionamento de entrada do pacote (lado menor ≥ 30 px, lados
  arredondados para
  múltiplos de 32), depois ``exact``.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
from model import ONNX_MODEL

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-014"


def normalize(image: np.ndarray, multiple: int | None) -> np.ndarray:
    h, w = image.shape[:2]
    target_w = max(320, math.ceil(48 * w / h))
    resized = cv2.resize(image, (math.ceil(48 * w / h), 48)).astype(np.float32)
    resized = (resized.transpose(2, 0, 1) / 255 - 0.5) / 0.5
    width = math.ceil(target_w / multiple) * multiple if multiple else target_w
    out = np.zeros((1, 3, 48, width), dtype=np.float32)
    out[0, :, :, : resized.shape[2]] = resized
    return out


def package_resize(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    if min(h, w) >= 30:
        return image
    ratio = 30 / min(h, w)
    new_h = int(round(int(h * ratio) / 32) * 32)
    new_w = int(round(int(w * ratio) / 32) * 32)
    return cv2.resize(image, (new_w, new_h))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    session = ort.InferenceSession(str(ONNX_MODEL), providers=["CPUExecutionProvider"])
    import onnx

    meta = {p.key: p.value for p in onnx.load(str(ONNX_MODEL)).metadata_props}
    characters = ["blank", *meta["character"].splitlines(), " "]
    items = json.loads((DATA / "test-exp001.json").read_text(encoding="utf-8"))
    variants = {
        "exact": lambda img: normalize(img, None),
        "mult32": lambda img: normalize(img, 32),
        "package": lambda img: normalize(package_resize(img), None),
    }
    for name, prep in variants.items():
        out = {}
        for item in items:
            image = cv2.imread(str(ROOT / item["image"]), cv2.IMREAD_COLOR)
            probs = session.run(None, {"x": prep(image)})[0][0]
            tokens, text, previous = probs.argmax(-1), [], None
            for token in tokens:
                if token != previous and token != 0:
                    text.append(characters[token])
                previous = token
            out[item["id"]] = "".join(text)
        path = DATA / f"pred-ort-{name}-test-exp001.json"
        path.write_text(
            json.dumps({"set": "test-exp001", "items": out}, ensure_ascii=False), encoding="utf-8"
        )
        print(name, "->", path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
