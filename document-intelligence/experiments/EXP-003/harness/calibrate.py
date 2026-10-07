"""Calibra os ordenadores **só** no conjunto ``dev`` do EXP-003, sobre o layout verdadeiro.

Para cada método (com e sem endireitamento) faz uma busca em grade pequena e guarda os parâmetros
de maior acurácia de ordem de blocos. Grava ``experiments/EXP-003/calibration.json``. O conjunto
``test`` nunca é lido aqui.
"""

from __future__ import annotations

import itertools
import json
import time
from dataclasses import replace
from pathlib import Path

from order_eval import evaluate_manifest
from orderers import OrderParams

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "dataset" / "fixtures" / "exp-003" / "dev-manifest.json"
OUT = Path(__file__).resolve().parents[1] / "calibration.json"

GRIDS = {
    "naive": {"tie": [0.0, 0.25, 0.5, 1.0]},
    "xycut": {"min_gap": [0.05, 0.15, 0.3, 0.6], "shrink": [0.0, 0.1, 0.25]},
    "anchored": {"lateral_offset": [0.04, 0.08, 0.12, 0.2], "side_overlap": [0.15, 0.3, 0.5]},
}


def calibrate(manifest: dict) -> dict[str, dict]:
    results = {}
    for method, grid in GRIDS.items():
        for deskew in (False, True):
            base = OrderParams(method=method, deskew=deskew)
            best, best_score, tried = base, -1.0, []
            for values in itertools.product(*grid.values()):
                params = replace(base, **dict(zip(grid, values, strict=True)))
                score = evaluate_manifest(manifest, params, repeats=1)["overall"]["blocks_accuracy"]
                tried.append({**dict(zip(grid, values, strict=True)), "blocks_accuracy": score})
                if score > best_score:
                    best, best_score = params, score
            name = method + ("+deskew" if deskew else "")
            results[name] = {
                "params": best.to_dict(),
                "dev_blocks_accuracy": best_score,
                "grid": tried,
            }
    return results


def main() -> int:
    started = time.monotonic()
    manifest = json.loads(DEV.read_text(encoding="utf-8"))
    result = {
        "dataset": "exp-003-dev",
        "note": "Calibração só no dev, sobre o layout verdadeiro.",
        "orderers": calibrate(manifest),
        "elapsed_s": round(time.monotonic() - started, 1),
    }
    OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    for name, item in result["orderers"].items():
        print(f"{name}: {item['dev_blocks_accuracy']:.4f} {item['params']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
