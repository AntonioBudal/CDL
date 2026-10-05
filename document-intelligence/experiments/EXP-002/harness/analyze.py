"""Análise de falhas do EXP-002: F1 de linhas por propriedade da página e modos de falha.

Lê as predições completas de uma execução (``dataset/processed/exp-002/reports/``) e o manifesto e
produz só agregados:

* F1 (caixa, IoU ≥ 0,5) por nível, por faixa de rotação da folha e por faixa de curvatura;
* modos de falha das linhas verdadeiras não casadas: ``perdida`` (nenhuma predição a cobre),
  ``fundida`` (uma predição cobre esta e outra linha), ``fragmentada`` (várias predições a cobrem),
  ``deslocada`` (uma predição a cobre só em parte);
* falsos positivos: ``fora_da_folha`` ou ``na_folha``.

Sombra e desfoque não são separados por página (o gerador não registra se a sombra foi sorteada);
ficam embutidos no nível.

Uso: ``python analyze.py --predictions <arquivo> --manifest <manifesto> --out <json>``
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from evaluate import _empty_counts, _ignored

from leitorum_di.metrics.base import calculate_iou
from leitorum_di.metrics.detection import match_detections, precision_recall_f1

SCHEMA = "leitorum-di-layout-failure-analysis/1"
ROTATION_BINS = [(0.0, 1.0), (1.0, 3.0), (3.0, 6.0), (6.0, 90.0)]
CURVATURE_BINS = [(0.0, 0.004), (0.004, 0.012), (0.012, 1.0)]


def page_rotation(page: dict[str, Any]) -> float:
    """Inclinação (graus, em módulo) da borda superior da folha."""
    (x0, y0), (x1, y1) = page["page_corners"][0], page["page_corners"][1]
    return abs(math.degrees(math.atan2(y1 - y0, x1 - x0)))


def page_curvature(page: dict[str, Any]) -> float:
    return float((page.get("degradation") or {}).get("transform", {}).get("curvature", 0.0))


def _bin_label(value: float, bins, unit: str) -> str:
    last = len(bins) - 1
    for index, (low, high) in enumerate(bins):
        if index == last:
            return f"≥{low:g}{unit}"
        if low <= value < high:
            return f"{low:g}–{high:g}{unit}"
    return ""


def _coverage(truth, prediction) -> float:
    """Fração da caixa verdadeira coberta pela predição."""
    ix = max(0, min(truth[2], prediction[2]) - max(truth[0], prediction[0]))
    iy = max(0, min(truth[3], prediction[3]) - max(truth[1], prediction[1]))
    area = max(1, (truth[2] - truth[0]) * (truth[3] - truth[1]))
    return ix * iy / area


def analyze(manifest: dict[str, Any], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, dict[str, float]]] = {"level": {}, "rotation": {}, "curvature": {}}
    failures: Counter[str] = Counter()
    false_positives: Counter[str] = Counter()
    by_level_failures: dict[str, Counter[str]] = {}

    for page in manifest["pages"]:
        result = predictions.get(page["id"], {"lines": []})
        truths = [line["bbox"] for line in page["lines"]]
        preds = [
            ln["bbox"]
            for ln in result.get("lines", [])
            if not _ignored(ln["bbox"], page.get("ignore", []))
        ]
        matches = match_detections(truths, preds, 0.5)
        counts = {
            "tp": len(matches),
            "fp": len(preds) - len(matches),
            "fn": len(truths) - len(matches),
            "iou_sum": sum(m[2] for m in matches),
        }
        labels = {
            "level": page["level"],
            "rotation": _bin_label(page_rotation(page), ROTATION_BINS, "°"),
            "curvature": _bin_label(page_curvature(page), CURVATURE_BINS, ""),
        }
        for key, label in labels.items():
            total = groups[key].setdefault(label, _empty_counts())
            for name in total:
                total[name] += counts[name]

        matched_truth = {m[0] for m in matches}
        matched_pred = {m[1] for m in matches}
        level_failures = by_level_failures.setdefault(page["level"], Counter())
        for index, truth in enumerate(truths):
            if index in matched_truth:
                continue
            covering = [p for p in preds if _coverage(truth, p) >= 0.2]
            if not covering:
                mode = "perdida"
            elif len(covering) >= 2:
                mode = "fragmentada"
            else:
                others = sum(
                    1
                    for j, other in enumerate(truths)
                    if j != index and _coverage(other, covering[0]) >= 0.5
                )
                mode = "fundida" if others else "deslocada"
            failures[mode] += 1
            level_failures[mode] += 1

        corners = np.array(page["page_corners"], dtype=np.float32)
        for index, prediction in enumerate(preds):
            if index in matched_pred:
                continue
            if any(calculate_iou(prediction, truth) >= 0.1 for truth in truths):
                continue  # já contado como modo de falha de uma linha verdadeira
            center = ((prediction[0] + prediction[2]) / 2, (prediction[1] + prediction[3]) / 2)
            inside = cv2.pointPolygonTest(corners, center, False) >= 0
            false_positives["na_folha" if inside else "fora_da_folha"] += 1

    return {
        "pages": len(manifest["pages"]),
        "f1_by": {
            key: {label: precision_recall_f1(counts) for label, counts in sorted(values.items())}
            for key, values in groups.items()
        },
        "unmatched_truth_modes": dict(failures),
        "unmatched_truth_modes_by_level": {
            k: dict(v) for k, v in sorted(by_level_failures.items())
        },
        "isolated_false_positives": dict(false_positives),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Análise de falhas de layout (EXP-002)")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    runs = json.loads(Path(args.predictions).read_text(encoding="utf-8"))
    run = next(run for run in runs if run)
    predictions = {item["id"]: item["result"] for item in run}
    ids = set(predictions)
    manifest = {**manifest, "pages": [page for page in manifest["pages"] if page["id"] in ids]}
    result = {
        "schema": SCHEMA,
        "candidate": args.candidate,
        "manifest": Path(args.manifest).name,
        **analyze(manifest, predictions),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Análise gravada em {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
