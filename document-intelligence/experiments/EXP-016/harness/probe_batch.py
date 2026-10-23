"""Sonda do EXP-016: leitura em lote contra individual, no modelo real, com linhas fictícias.

Roda no ambiente ``EXP-008/envs/ppocr``. Gera 40 linhas sintéticas ("Livro de Teste",
"Capítulo N"…) em larguras variadas, lê uma a uma e em lotes de 8, e conta textos idênticos
e o tempo de cada modo.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import PagePipeline  # noqa: E402

MODELS = {  # os mesmos de read.py (que depende do pacote principal, ausente neste ambiente)
    "PP-OCRv6_det_small.onnx": "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f",
    "PP-OCRv6_rec_small.onnx": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
}
PHRASES = [
    "Livro de Teste",
    "Capítulo {n}",
    "nota de margem {n}",
    "uma linha mais longa de teste {n}",
]


def synthetic_lines(count: int = 40) -> list[np.ndarray]:
    lines = []
    for n in range(count):
        text = PHRASES[n % len(PHRASES)].format(n=n)
        scale = 0.8 + 0.1 * (n % 5)
        (w, h), base = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)
        image = np.full((h + base + 16, w + 16, 3), 255, np.uint8)
        cv2.putText(image, text, (8, h + 8), cv2.FONT_HERSHEY_SIMPLEX, scale, (20, 20, 20), 2)
        lines.append(image)
    return lines


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    pipeline = PagePipeline()
    pipeline.load({"options": {"models": MODELS, "merge": {}, "batch": 8}})
    lines = synthetic_lines()
    started = time.perf_counter()
    single = [pipeline._read(line) for line in lines]
    single_s = time.perf_counter() - started
    started = time.perf_counter()
    batched = pipeline._read_many(lines)
    batched_s = time.perf_counter() - started
    same = sum(a[0] == b[0] for a, b in zip(single, batched, strict=True))
    gap = max(abs(a[1] - b[1]) for a, b in zip(single, batched, strict=True))
    summary = {"lines": len(lines), "same_text": same, "max_confidence_gap": gap}
    summary |= {"single_s": round(single_s, 3), "batched_s": round(batched_s, 3)}
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
