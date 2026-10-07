"""Análise dos erros de ordem de leitura do EXP-003 a partir dos relatórios do benchmark.

Para cada ordenador e fonte de layout: acurácia por família e nível, tipos de bloco fora de ordem
(separando os laterais — nota de margem e caixa de destaque — dos do fluxo principal) e a
decomposição da perda de ponta a ponta. Produz só agregados.

Uso: ``python analyze.py --true <relatório> --detected <relatório> [--detected-original <relatório>]
--out <json>``
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA = "leitorum-di-reading-order-analysis/1"


def _displaced(orderer: dict[str, Any]) -> dict[str, dict[str, int]]:
    by_family: dict[str, Counter[str]] = {}
    for page in orderer["per_page"]:
        by_family.setdefault(page["family"], Counter()).update(page["displaced_types"])
    return {family: dict(counter.most_common()) for family, counter in sorted(by_family.items())}


def _pages_with_errors(orderer: dict[str, Any]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for page in orderer["per_page"]:
        if page["blocks_full"][0] > 0:
            counter[f"{page['family']}/{page['level']}"] += 1
    return dict(sorted(counter.items()))


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for name, orderer in report["orderers"].items():
        overall = orderer["overall"]
        out[name] = {
            "blocks_accuracy": overall["blocks_accuracy"],
            "blocks_accuracy_matched": overall["blocks_accuracy_matched"],
            "lines_accuracy": overall["lines_accuracy"],
            "lines_accuracy_matched": overall["lines_accuracy_matched"],
            "perfect_pages": overall["perfect_pages"],
            "tau_blocks_mean": overall["tau_blocks_mean"],
            "unmatched_predicted": overall["unmatched_predicted"],
            "unmatched_truth": overall["unmatched_truth"],
            "truth_blocks": overall["truth_blocks"],
            "order_ms_median": overall["order_ms_median"],
            "order_ms_max": overall["order_ms_max"],
            "by_family": {k: v["blocks_accuracy"] for k, v in orderer["by_family"].items()},
            "by_level": {k: v["blocks_accuracy"] for k, v in orderer["by_level"].items()},
            "lines_by_level": {k: v["lines_accuracy"] for k, v in orderer["by_level"].items()},
            "displaced_types_by_family": _displaced(orderer),
            "pages_with_errors": _pages_with_errors(orderer),
            "verdicts": orderer["verdicts"],
            "ldf": orderer["ldf"],
        }
    return out


def decomposition(true: dict[str, Any], detected: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Perda de ponta a ponta separada em ordenação e detecção (faltas e sobras de blocos)."""
    out = {}
    for name in true:
        a = true[name]["blocks_accuracy"]
        b = detected[name]["blocks_accuracy"]
        c = detected[name]["blocks_accuracy_matched"]
        out[name] = {
            "true_layout": a,
            "detected_layout": b,
            "detected_layout_matched_only": c,
            "loss_total": a - b,
            "loss_from_ordering": a - c,
            "loss_from_detection": c - b,
        }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Análise de ordem de leitura (EXP-003)")
    parser.add_argument("--true", required=True)
    parser.add_argument("--detected", required=True)
    parser.add_argument("--detected-original", default=None)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    def load(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    true, detected = summarize(load(args.true)), summarize(load(args.detected))
    result = {
        "schema": SCHEMA,
        "true_layout": true,
        "detected_layout": detected,
        "decomposition": decomposition(true, detected),
    }
    if args.detected_original:
        result["detected_layout_lines_without_rectification"] = summarize(
            load(args.detected_original)
        )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Análise gravada em {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
