"""Calibra o baseline clássico e as regras de blocos **só** no conjunto ``dev``.

* Baseline: busca em grade em duas etapas (binarização; depois dilatação e fusão), maximizando o F1
  de linhas (bbox, IoU ≥ 0,5) no ``dev``.
* Regras de blocos: busca em grade sobre as **linhas verdadeiras** do ``dev`` (independe do
  detector), maximizando o mAP@0,5.

Grava ``experiments/EXP-002/calibration.json``. O conjunto ``test`` nunca é lido aqui.
"""

from __future__ import annotations

import itertools
import json
import time
from dataclasses import replace
from pathlib import Path

import cv2
from blocks import BlockParams, assemble_blocks
from classic import ClassicParams, detect_lines, ink_mask
from evaluate import evaluate_pages

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "dataset" / "fixtures" / "exp-002" / "dev-manifest.json"
OUT = Path(__file__).resolve().parents[1] / "calibration.json"


def _line_f1(manifest, images, params: ClassicParams) -> float:
    predictions = {}
    for page in manifest["pages"]:
        lines, _, _ = detect_lines(images[page["id"]], params)
        predictions[page["id"]] = {"lines": lines, "blocks": []}
    return evaluate_pages(manifest, predictions)["lines"]["bbox"]["0.5"]["f1"]


def calibrate_classic(manifest, images) -> tuple[ClassicParams, list[dict]]:
    history = []
    best = ClassicParams()
    best_f1 = _line_f1(manifest, images, best)
    history.append({"params": best.to_dict(), "f1": best_f1})
    stages = [
        {"block_size": [41, 61], "offset": [18, 25, 30, 38]},
        {"dilate_width": [15, 21, 31], "merge_gap_factor": [1.5, 2.5, 4.0]},
    ]
    for grid in stages:
        stage_best = best
        for values in itertools.product(*grid.values()):
            candidate = replace(best, **dict(zip(grid, values, strict=True)))
            f1 = _line_f1(manifest, images, candidate)
            history.append({"params": candidate.to_dict(), "f1": f1})
            if f1 > best_f1:
                stage_best, best_f1 = candidate, f1
        best = stage_best
    return best, history


def calibrate_blocks(manifest, masks) -> tuple[BlockParams, float, int]:
    grid = {
        "paragraph_gap": [1.3, 1.55, 1.8],
        "title_height": [1.0, 1.08, 1.2],
        "title_gap": [1.4, 1.6, 2.0],
        "margin_gap": [0.2, 0.5, 1.0],
        "graphic_min_area": [4.0, 6.0, 10.0],
    }
    best, best_map, tried = BlockParams(), -1.0, 0
    for values in itertools.product(*grid.values()):
        params = BlockParams(**dict(zip(grid, values, strict=True)))
        predictions = {}
        for page in manifest["pages"]:
            lines = [{"bbox": ln["bbox"], "polygon": ln["polygon"]} for ln in page["lines"]]
            blocks = assemble_blocks(lines, masks[page["id"]], params)
            predictions[page["id"]] = {"lines": [], "blocks": blocks}
        score = evaluate_pages(manifest, predictions)["blocks"]["map50"] or 0.0
        tried += 1
        if score > best_map:
            best, best_map = params, score
    return best, best_map, tried


def main() -> int:
    started = time.monotonic()
    manifest = json.loads(DEV.read_text(encoding="utf-8"))
    images = {
        p["id"]: cv2.imread(str(ROOT / p["image"]), cv2.IMREAD_COLOR) for p in manifest["pages"]
    }
    classic, history = calibrate_classic(manifest, images)
    base = ClassicParams()
    masks = {
        pid: ink_mask(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), base) for pid, img in images.items()
    }
    blocks, block_map, tried = calibrate_blocks(manifest, masks)
    result = {
        "dataset": "exp-002-dev",
        "classic_params": classic.to_dict(),
        "classic_dev_f1": max(item["f1"] for item in history),
        "classic_history": history,
        "block_params": blocks.to_dict(),
        "block_dev_map50_on_true_lines": block_map,
        "block_combinations_tried": tried,
        "note": "Calibração só no dev; regras de blocos ajustadas nas linhas verdadeiras do dev.",
        "elapsed_s": round(time.monotonic() - started, 1),
    }
    OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "classic_history"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
