"""Calibra o ponto de operação dos blocos detectados **só** no conjunto ``dev``.

Busca em grade sobre limiar de confiança, IoU da NMS e contenção, maximizando a acurácia de ordem
de blocos de ponta a ponta do ordenador ``anchored`` (já calibrado) no layout detectado do ``dev``.
Grava o resultado em ``calibration.json`` (chave ``block_filter``). O ``test`` nunca é lido aqui.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from order_eval import evaluate_manifest
from orderers import OrderParams
from postprocess import BlockFilter, filter_blocks

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "dataset" / "fixtures" / "exp-003" / "dev-manifest.json"
DETECTED = ROOT / "dataset" / "processed" / "exp-003" / "detected-dev.json"
CALIBRATION = Path(__file__).resolve().parents[1] / "calibration.json"
GRID = {
    "min_score": [0.3, 0.4, 0.5, 0.6, 0.7],
    "nms_iou": [0.3, 0.5, 0.7],
    "containment": [0.6, 0.8, 1.01],
}


def main() -> int:
    manifest = json.loads(DEV.read_text(encoding="utf-8"))
    raw = json.loads(DETECTED.read_text(encoding="utf-8"))["pages"]
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    orderer = OrderParams(**calibration["orderers"]["anchored"]["params"])

    best, best_score, tried = BlockFilter(), -1.0, []
    for values in itertools.product(*GRID.values()):
        params = BlockFilter(**dict(zip(GRID, values, strict=True)))
        detected = {
            pid: {
                "blocks": filter_blocks(item["blocks"], params),
                "lines": item["lines"]["rectified"],
            }
            for pid, item in raw.items()
        }
        overall = evaluate_manifest(manifest, orderer, detected, repeats=1)["overall"]
        tried.append({**params.to_dict(), "blocks_accuracy": overall["blocks_accuracy"],
                      "unmatched_predicted": overall["unmatched_predicted"],
                      "unmatched_truth": overall["unmatched_truth"]})  # fmt: skip
        if overall["blocks_accuracy"] > best_score:
            best, best_score = params, overall["blocks_accuracy"]

    calibration["block_filter"] = {
        "params": best.to_dict(),
        "dev_blocks_accuracy_end_to_end": best_score,
        "orderer": "anchored",
        "note": "Calibrado só no dev, sobre o layout detectado (linhas retificadas).",
        "grid": tried,
    }
    CALIBRATION.write_text(
        json.dumps(calibration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"melhor: {best.to_dict()} - acurácia de ponta a ponta no dev {best_score:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
