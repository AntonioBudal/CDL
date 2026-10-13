"""Análise do EXP-007: comparação sintético × real e natureza dos erros de linha.

Lê o relatório de ``run.py`` e, para classificar os erros, os manifestos e layouts detectados (fora
do Git). Grava só números e identificadores de arquivo.

Cada linha verdadeira não casada (IoU < 0,5 com toda predição) é classificada pela caixa:

* ``missed``: nenhuma predição cobre metade dela;
* ``merged``: a predição que a cobre também cobre metade de outra linha verdadeira;
* ``split``: duas ou mais predições estão, cada uma, mais da metade dentro dela;
* ``misaligned``: há predição sobre ela, mas com sobreposição insuficiente.

Também calcula:

* o teto de uma fusão de fragmentos (``oracle_merge``): as predições que estão mais da metade dentro
  de uma mesma linha verdadeira são unidas antes de casar. Usa a verdade de chão para unir, então é
  um limite superior do que uma fusão horizontal recuperaria, não um resultado do pipeline;
* o efeito da retificação por faixa de área do quadrilátero encontrado;
* quantos parágrafos verdadeiros ficaram dentro de um bloco detectado maior.

Uso: ``... python experiments/EXP-007/harness/analyze.py --benchmark <relatório> --out <arquivo>``
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from postprocess import BlockFilter, filter_blocks

from leitorum_di.metrics.detection import detection_counts, match_detections, precision_recall_f1

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
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


def merge_fragments(truths: list[list[float]], predictions: list[list[float]]):
    """Une as predições que estão mais da metade dentro de uma mesma linha verdadeira."""
    groups: dict[int, list[list[float]]] = {}
    rest = []
    for prediction in predictions:
        area = _area(prediction) or 1.0
        shares = [_intersection(truth, prediction) / area for truth in truths]
        best = max(range(len(truths)), key=shares.__getitem__, default=None)
        if best is None or shares[best] < 0.5:
            rest.append(prediction)
        else:
            groups.setdefault(best, []).append(prediction)
    merged = [
        [min(b[0] for b in g), min(b[1] for b in g), max(b[2] for b in g), max(b[3] for b in g)]
        for _, g in sorted(groups.items())
    ]
    return merged + rest


def _load(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = json.loads((DATA / f"{name}-manifest.json").read_text(encoding="utf-8"))
    detected = json.loads((DATA / f"detected-{name}.json").read_text(encoding="utf-8"))
    return manifest, detected


def _ignored(box, regions) -> bool:
    area = _area(box)
    return area == 0 or any(_intersection(box, region) / area >= 0.5 for region in regions)


def _kept_lines(page: dict[str, Any], lines: list[dict[str, Any]]) -> list[list[float]]:
    return [ln["bbox"] for ln in lines if not _ignored(ln["bbox"], page.get("ignore", []))]


def line_errors(name: str, key: str) -> dict[str, Any]:
    manifest, detected = _load(name)
    kinds: Counter = Counter()
    truth_total = 0
    worst = []
    oracle = {"tp": 0, "fp": 0, "fn": 0, "iou_sum": 0.0}
    fragments = []
    for page in manifest["pages"]:
        truths = [line["bbox"] for line in page["lines"]]
        predictions = _kept_lines(page, detected["pages"][page["id"]]["lines"][key])
        page_kinds = classify_unmatched(truths, predictions)
        kinds.update(page_kinds)
        truth_total += len(truths)
        worst.append((sum(page_kinds.values()) / max(1, len(truths)), page["id"]))
        counts = detection_counts(truths, merge_fragments(truths, predictions), 0.5)
        for field in oracle:
            oracle[field] += counts[field]
        if truths:
            fragments.append(len(predictions) / len(truths))
    unmatched = sum(kinds.values())
    fragments.sort()
    return {
        "oracle_merge": precision_recall_f1(oracle),
        "predictions_per_truth_line_median": fragments[len(fragments) // 2] if fragments else None,
        "truth_lines": truth_total,
        "unmatched_truth_lines": unmatched,
        "by_kind": dict(kinds),
        "share_by_kind": {k: v / unmatched for k, v in kinds.items()} if unmatched else {},
        "pages_with_all_lines_unmatched": sum(1 for share, _ in worst if share >= 1.0),
        "worst_pages": [pid for _, pid in sorted(worst, reverse=True)[:10]],
    }


def _quad_area(quad) -> float:
    total = sum(
        quad[i][0] * quad[(i + 1) % 4][1] - quad[(i + 1) % 4][0] * quad[i][1] for i in range(4)
    )
    return abs(total / 2)


BUCKETS = {"quad >= 90% da foto": (0.9, 9.9), "60% a 90%": (0.6, 0.9), "< 60%": (0.0, 0.6)}


def rectification_effect() -> dict[str, Any]:
    """F1 de linhas com e sem retificação, por fração da foto ocupada pelo quadrilátero."""
    manifest, detected = _load("gnhk")
    share = {
        page["id"]: _quad_area(detected["pages"][page["id"]]["rectification"]["quad"])
        / (page["width"] * page["height"])
        for page in manifest["pages"]
    }
    out: dict[str, Any] = {}
    for label, (low, high) in BUCKETS.items():
        totals = {k: {"tp": 0, "fp": 0, "fn": 0, "iou_sum": 0.0} for k in ("original", "rectified")}
        pages = [page for page in manifest["pages"] if low <= share[page["id"]] < high]
        for page in pages:
            truths = [line["bbox"] for line in page["lines"]]
            for key, total in totals.items():
                predictions = _kept_lines(page, detected["pages"][page["id"]]["lines"][key])
                counts = detection_counts(truths, predictions, 0.5)
                for field in total:
                    total[field] += counts[field]
        out[label] = {
            "photos": len(pages),
            "f1_original": precision_recall_f1(totals["original"])["f1"] if pages else None,
            "f1_rectified": precision_recall_f1(totals["rectified"])["f1"] if pages else None,
        }
    ordered = sorted(share.values())
    out["quad_share_median"] = ordered[len(ordered) // 2]
    return out


def block_absorption(name: str) -> dict[str, Any]:
    """Parágrafos verdadeiros que ficaram dentro de um bloco detectado maior."""
    manifest, detected = _load(name)
    registry = json.loads((EXPERIMENT / "candidates.json").read_text(encoding="utf-8"))
    block_filter = BlockFilter(**registry["block_filter"])
    absorbed = unmatched = truth_total = 0
    per_page: Counter = Counter()
    for page in manifest["pages"]:
        blocks = filter_blocks(detected["pages"][page["id"]]["blocks"], block_filter)
        kept = [block["bbox"] for block in blocks]
        truths = [block["bbox"] for block in page["blocks"]]
        per_page[min(len(kept), 5)] += 1
        matched = {ti for ti, _, _ in match_detections(truths, kept, 0.5)}
        truth_total += len(truths)
        for index, truth in enumerate(truths):
            if index in matched:
                continue
            unmatched += 1
            area = _area(truth) or 1.0
            if any(
                _intersection(truth, box) / area >= 0.9 and _area(box) >= 1.5 * area for box in kept
            ):
                absorbed += 1
    return {
        "truth_blocks": truth_total,
        "unmatched_truth_blocks": unmatched,
        "absorbed_in_larger_block": absorbed,
        "pages_by_detected_blocks": {
            ("5+" if k == 5 else str(k)): v for k, v in sorted(per_page.items())
        },
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
        "rectification_effect": rectification_effect(),
        "block_absorption": {n: block_absorption(n) for n in ("bressay-x3", "bressay-native")},
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
        merged = {k: round(v, 3) for k, v in item["oracle_merge"].items() if k != "mean_iou"}
        per_line = round(item["predictions_per_truth_line_median"], 2)
        print("  teto com fusão:", merged, "| predições por linha:", per_line)
    print("retificação:", json.dumps(analysis["rectification_effect"], ensure_ascii=False))
    print("blocos:", json.dumps(analysis["block_absorption"], ensure_ascii=False))
    regions = analysis["gnhk_by_region"]["original"]
    print("regiões:", {k: round(v["f1"], 3) for k, v in regions.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
