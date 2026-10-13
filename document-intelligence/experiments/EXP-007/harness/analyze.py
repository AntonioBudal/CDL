"""Análise do EXP-007: comparação sintético × real e natureza dos erros de linha.

Lê o relatório de ``run.py`` e, para classificar os erros, os manifestos e layouts detectados (fora
do Git). Grava só números e identificadores de arquivo.

Cada linha verdadeira não casada (IoU < 0,5 com toda predição) é classificada pela caixa:

* ``missed``: nenhuma predição cobre metade dela;
* ``merged``: a predição que a cobre também cobre metade de outra linha verdadeira;
* ``split``: duas ou mais predições estão, cada uma, mais da metade dentro dela;
* ``misaligned``: há predição sobre ela, mas com sobreposição insuficiente.

Uso: ``... python experiments/EXP-007/harness/analyze.py --benchmark <relatório> --out <arquivo>``
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from leitorum_di.metrics.detection import match_detections

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-007"
SETS = {
    "gnhk": ("original", "rectified"),
    "bressay-x3": ("original",),
    "bressay-native": ("original",),
}


def _intersection(a, b) -> float:
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def _area(box) -> float:
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def classify_unmatched(truths: list[list[float]], predictions: list[list[float]]) -> Counter:
    """Classifica as linhas verdadeiras não casadas de uma página."""
    matched = {ti for ti, _, _ in match_detections(truths, predictions, 0.5)}
    kinds: Counter = Counter()
    for index, truth in enumerate(truths):
        if index in matched:
            continue
        area = _area(truth) or 1.0
        covering = [p for p in predictions if _intersection(truth, p) / area >= 0.5]
        inside = [p for p in predictions if _intersection(truth, p) / (_area(p) or 1.0) >= 0.5]
        merged = any(
            _intersection(other, p) / (_area(other) or 1.0) >= 0.5
            for p in covering
            for k, other in enumerate(truths)
            if k != index
        )
        if merged:
            kinds["merged"] += 1
        elif len(inside) >= 2:
            kinds["split"] += 1
        elif covering or inside:
            kinds["misaligned"] += 1
        else:
            kinds["missed"] += 1
    return kinds


def line_errors(name: str, key: str) -> dict[str, Any]:
    manifest = json.loads((DATA / f"{name}-manifest.json").read_text(encoding="utf-8"))
    detected = json.loads((DATA / f"detected-{name}.json").read_text(encoding="utf-8"))
    kinds: Counter = Counter()
    truth_total = 0
    worst = []
    for page in manifest["pages"]:
        truths = [line["bbox"] for line in page["lines"]]
        predictions = [line["bbox"] for line in detected["pages"][page["id"]]["lines"][key]]
        page_kinds = classify_unmatched(truths, predictions)
        kinds.update(page_kinds)
        truth_total += len(truths)
        worst.append((sum(page_kinds.values()) / max(1, len(truths)), page["id"]))
    unmatched = sum(kinds.values())
    return {
        "truth_lines": truth_total,
        "unmatched_truth_lines": unmatched,
        "by_kind": dict(kinds),
        "share_by_kind": {k: v / unmatched for k, v in kinds.items()} if unmatched else {},
        "pages_with_all_lines_unmatched": sum(1 for share, _ in worst if share >= 1.0),
        "worst_pages": [pid for _, pid in sorted(worst, reverse=True)[:10]],
    }


def comparison(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Tabela sintético × real, uma linha por métrica."""
    ref = report["synthetic_reference"]
    data = report["datasets"]
    gnhk, big, native = data["gnhk"], data["bressay-x3"], data["bressay-native"]

    def f1(item, key="lines_original"):
        return item[key]["bbox"]["0.5"]["f1"]

    def order(item, layout):
        return item["order"]["anchored"][layout]["blocks_accuracy"]

    return [
        {
            "metric": "F1 de linhas, sem retificação",
            "synthetic": ref["lines_f1_strong"],
            "synthetic_condition": "degradação forte",
            "gnhk": f1(gnhk),
            "bressay_x3": f1(big),
            "bressay_native": f1(native),
        },
        {
            "metric": "F1 de linhas, com retificação",
            "synthetic": ref["lines_f1_strong_rectified"],
            "synthetic_condition": "degradação forte",
            "gnhk": f1(gnhk, "lines_rectified"),
        },
        {
            "metric": "F1 de linhas, página limpa",
            "synthetic": ref["lines_f1_clean"],
            "synthetic_condition": "sem degradação",
            "bressay_x3": f1(big),
            "bressay_native": f1(native),
        },
        {
            "metric": "blocos (sintético: mAP50 com classe; real: AP50 sem classe)",
            "synthetic": ref["blocks_map50"],
            "bressay_x3": big["blocks"]["class_agnostic_ap50"],
            "bressay_native": native["blocks"]["class_agnostic_ap50"],
        },
        {
            "metric": "F1 de blocos no ponto de operação",
            "bressay_x3": big["blocks"]["at_operating_point"]["0.5"]["f1"],
            "bressay_native": native["blocks"]["at_operating_point"]["0.5"]["f1"],
        },
        {
            "metric": "ordem de blocos, layout verdadeiro",
            "synthetic": ref["order_true_layout"],
            "bressay_x3": order(big, "true_layout"),
            "bressay_native": order(native, "true_layout"),
        },
        {
            "metric": "ordem de blocos, layout detectado",
            "synthetic": ref["order_detected_layout"],
            "bressay_x3": order(big, "detected_layout"),
            "bressay_native": order(native, "detected_layout"),
        },
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Análise do EXP-007")
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    report = json.loads(Path(args.benchmark).read_text(encoding="utf-8"))
    analysis = {
        "schema": "leitorum-di-real-images-analysis/1",
        "experiment": "EXP-007",
        "benchmark": Path(args.benchmark).name,
        "benchmark_commit": report["git"]["commit"],
        "comparison": comparison(report),
        "line_errors": {
            f"{name}/{key}": line_errors(name, key) for name, keys in SETS.items() for key in keys
        },
        "gnhk_by_region": {
            "original": report["datasets"]["gnhk"]["lines_original"]["by_group"],
            "rectified": report["datasets"]["gnhk"]["lines_rectified"]["by_group"],
            "rectification_found": report["datasets"]["gnhk"]["rectification"]["found_by_group"],
        },
        "verdicts": {name: verdict["met"] for name, verdict in report["verdicts"].items()},
    }
    out = Path(args.out)
    out.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    for row in analysis["comparison"]:
        values = {k: round(v, 3) for k, v in row.items() if isinstance(v, float)}
        print(row["metric"], values)
    for name, item in analysis["line_errors"].items():
        print(name, item["unmatched_truth_lines"], "de", item["truth_lines"], item["by_kind"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
