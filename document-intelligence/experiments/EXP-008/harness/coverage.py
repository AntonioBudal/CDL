"""Medida por cobertura de área, complementar ao F1 por IoU com a linha inteira.

Para cada página, sobre as caixas rasterizadas numa grade reduzida:

* ``covered``: fração da área das linhas verdadeiras que está dentro de alguma detecção;
* ``spill``: fração da área detectada que cai fora de toda linha verdadeira e de toda região a
  ignorar.

Não depende de como a tinta foi repartida em caixas: uma linha partida em três fragmentos e uma
linha detectada inteira dão a mesma cobertura.
"""

from __future__ import annotations

from typing import Any

import numpy as np

GRID = 1024


def _mask(boxes, shape, scale: float) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    for x0, y0, x1, y1 in boxes:
        c0, r0 = int(np.floor(x0 * scale)), int(np.floor(y0 * scale))
        c1, r1 = int(np.ceil(x1 * scale)), int(np.ceil(y1 * scale))
        mask[max(0, r0) : max(0, r1), max(0, c0) : max(0, c1)] = True
    return mask


def page_coverage(page: dict[str, Any], predicted: list[list[float]]) -> dict[str, int]:
    """Contagens de área (em células da grade) de uma página."""
    scale = GRID / max(page["width"], page["height"])
    shape = (int(np.ceil(page["height"] * scale)) + 1, int(np.ceil(page["width"] * scale)) + 1)
    truth = _mask([line["bbox"] for line in page["lines"]], shape, scale)
    ignore = _mask(page.get("ignore", []), shape, scale)
    found = _mask(predicted, shape, scale)
    return {
        "truth": int(truth.sum()),
        "truth_covered": int((truth & found).sum()),
        "predicted": int(found.sum()),
        "predicted_outside": int((found & ~truth & ~ignore).sum()),
    }


def summarize(counts: list[dict[str, int]]) -> dict[str, float | None]:
    truth = sum(c["truth"] for c in counts)
    predicted = sum(c["predicted"] for c in counts)
    covered = sum(c["truth_covered"] for c in counts) / truth if truth else None
    spill = sum(c["predicted_outside"] for c in counts) / predicted if predicted else None
    score = None
    if covered is not None and spill is not None and covered + (1 - spill) > 0:
        score = 2 * covered * (1 - spill) / (covered + (1 - spill))
    return {"covered": covered, "spill": spill, "area_f1": score}
