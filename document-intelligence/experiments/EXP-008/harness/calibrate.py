"""Calibra a fusão de fragmentos de cada candidato, só nos conjuntos de calibração.

Busca em grade sobre ``v_overlap``, ``max_gap`` e ``max_angle``. O critério é a média do F1 de
linhas (IoU ≥ 0,5) nos dois conjuntos de calibração. Grava ``calibration.json`` com a grade
inteira, o
resultado sem fusão e os parâmetros escolhidos. Nenhum dado de teste é lido aqui.

Uso: ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-008/harness/calibrate.py``
"""

from __future__ import annotations

import itertools
import json
import sys
import time

from common import (
    CALIBRATION_SETS,
    EXPERIMENT,
    line_f1,
    load_detection,
    load_manifest,
    write_json,
)
from merge import MergeParams, merge_lines

GRID = {
    "v_overlap": (0.3, 0.5, 0.7),
    "max_gap": (0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0),
    "max_angle": (5.0, 10.0, 20.0),
}


def score(manifests, detections, params: MergeParams | None) -> dict[str, float]:
    result = {}
    for name in CALIBRATION_SETS:
        pages = detections[name]["pages"]
        if params is not None:
            pages = {pid: merge_lines(lines, params) for pid, lines in pages.items()}
        result[name] = line_f1(manifests[name], pages)["f1"]
    result["mean"] = sum(result[name] for name in CALIBRATION_SETS) / len(CALIBRATION_SETS)
    return result


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    registry = json.loads((EXPERIMENT / "candidates.json").read_text(encoding="utf-8"))
    manifests = {name: load_manifest(name) for name in CALIBRATION_SETS}
    started = time.monotonic()
    out = {
        "schema": "leitorum-di-merge-calibration/1",
        "note": "Calibração só nos conjuntos cal-gnhk e cal-bressay; o teste não é lido.",
        "criterion": "média do F1 de linhas (IoU >= 0,5) nos dois conjuntos de calibração",
        "grid": {key: list(values) for key, values in GRID.items()},
        "sets": {name: len(manifests[name]["pages"]) for name in CALIBRATION_SETS},
        "candidates": {},
    }
    for candidate in registry["candidates"]:
        cid = candidate["id"]
        detections = {name: load_detection(cid, name) for name in CALIBRATION_SETS}
        raw = score(manifests, detections, None)
        results = []
        for v_overlap, max_gap, max_angle in itertools.product(*GRID.values()):
            params = MergeParams(v_overlap, max_gap, max_angle)
            results.append({"params": params.to_dict(), **score(manifests, detections, params)})
        best = max(results, key=lambda item: item["mean"])
        out["candidates"][cid] = {"raw": raw, "best": best, "grid_results": results}
        print(
            f"{cid}: bruto {raw['mean']:.3f} → fundido {best['mean']:.3f} com {best['params']} "
            f"(gnhk {best['cal-gnhk']:.3f}, bressay {best['cal-bressay']:.3f})"
        )
    out["elapsed_s"] = round(time.monotonic() - started, 1)
    write_json(EXPERIMENT / "calibration.json", out, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
