"""Benchmark do EXP-007: pipeline dos ADR-002/003 em imagens reais (GNHK e BRESSAY).

Lê os manifestos com a verdade de chão e os layouts detectados por ``detect.py`` (ambos fora do Git)
e grava um relatório só com números e identificadores de arquivo.

* GNHK: F1 de linhas com e sem retificação, taxa de sucesso da retificação, custo.
* BRESSAY (ampliado 3× e nativo): F1 de linhas; blocos sem olhar a classe (AP50 e F1 no ponto de
  operação do EXP-003); ordem de leitura com parágrafos verdadeiros e detectados.
* Todas as saídas convertidas para LDF 2.0 e validadas.

Uso (a partir de ``document-intelligence/``, com a árvore limpa):
``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-007/harness/run.py --out evaluation/benchmarks/<arquivo>.json``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evaluate import _bbox_iou, evaluate_pages
from order_eval import evaluate_manifest, predict_sequences
from orderers import OrderParams
from postprocess import BlockFilter, filter_blocks
from to_ldf2 import convert_all, layout_component, order_component

from leitorum_di.metrics.detection import detection_counts, precision_recall_f1
from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds

SCHEMA = "leitorum-di-real-images-benchmark/1"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed" / "exp-007"

# Referências sintéticas (EXP-002 e EXP-003, aceitos) e critérios da spec §1.
SYNTHETIC = {
    "lines_f1_clean": 0.928,
    "lines_f1_strong": 0.784,
    "lines_f1_strong_rectified": 0.845,
    "blocks_map50": 0.781,
    "order_true_layout": 0.983,
    "order_detected_layout": 0.773,
    "page_ms": {"rectify": 178.0, "docufcn": 2600.0, "heron": 1800.0},
}
H1_MARGIN = 0.10
H2_FOUND_RATE = 0.70
H3_MARGIN = 0.05
H4_BLOCK_F1 = 0.70
H5_ORDER_TRUE = 0.90
H5_ORDER_DETECTED = 0.75
H6_TIME_FACTOR = 1.5
H6_MAX_PEAK_BYTES = 2 * 1024**3


def git_state() -> dict[str, object]:
    def git(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return out.stdout.strip()

    status = git("status", "--porcelain", "--", ".", ":(exclude)evaluation")
    return {"commit": git("rev-parse", "HEAD"), "dirty": None if status is None else bool(status)}


def load(name: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    manifest_path = DATA / f"{name}-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    detected = json.loads((DATA / f"detected-{name}.json").read_text(encoding="utf-8"))
    if detected.get("fake"):
        raise SystemExit(f"{name}: o layout detectado é de ensaio (--fake)")
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if detected["manifest_sha256"] != digest:
        raise SystemExit(f"{name}: o layout detectado não corresponde ao manifesto atual")
    return manifest, detected, manifest_path


def line_metrics(manifest: dict[str, Any], detected: dict[str, Any], key: str) -> dict[str, Any]:
    predictions = {
        pid: {"lines": item["lines"][key], "blocks": []} for pid, item in detected["pages"].items()
    }
    result = evaluate_pages(manifest, predictions)
    f1 = sorted(page["f1"] for page in result["per_page"] if page["f1"] is not None)
    return {
        "bbox": result["lines"]["bbox"],
        "polygon": result["lines"]["polygon"],
        "by_group": result["lines_by_level"],
        "missing_pages": result["missing"],
        "page_f1_median": f1[len(f1) // 2] if f1 else None,
        "pages_with_f1_below_0_5": sum(1 for value in f1 if value < 0.5),
        "predicted_lines": sum(len(p["lines"]) for p in predictions.values()),
        "truth_lines": sum(len(p["lines"]) for p in manifest["pages"]),
    }


def subset(manifest: dict[str, Any], ids: set[str]) -> dict[str, Any]:
    return {**manifest, "pages": [p for p in manifest["pages"] if p["id"] in ids]}


def as_paragraphs(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ignora a classe: todo bloco previsto conta como parágrafo."""
    return [{**block, "type": "paragraph"} for block in blocks]


def block_metrics(
    manifest: dict[str, Any], detected: dict[str, Any], block_filter: BlockFilter
) -> dict[str, Any]:
    raw = {
        pid: {"lines": [], "blocks": as_paragraphs(item["blocks"])}
        for pid, item in detected["pages"].items()
    }
    ap50 = evaluate_pages(manifest, raw)["blocks"]["ap50"]["paragraph"]
    totals = {t: {"tp": 0, "fp": 0, "fn": 0, "iou_sum": 0.0} for t in (0.5, 0.75)}
    predicted = 0
    for page in manifest["pages"]:
        kept = filter_blocks(raw[page["id"]]["blocks"], block_filter)
        predicted += len(kept)
        for threshold, total in totals.items():
            counts = detection_counts(page["blocks"], kept, threshold, _bbox_iou)
            for key in total:
                total[key] += counts[key]
    return {
        "class_agnostic_ap50": ap50,
        "operating_point": block_filter.to_dict(),
        "at_operating_point": {str(t): precision_recall_f1(c) for t, c in totals.items()},
        "predicted_blocks": predicted,
        "raw_predicted_blocks": sum(len(p["blocks"]) for p in raw.values()),
        "truth_blocks": sum(len(p["blocks"]) for p in manifest["pages"]),
    }


def order_metrics(
    manifest: dict[str, Any],
    detected: dict[str, Any],
    block_filter: BlockFilter,
    orderers: dict[str, OrderParams],
) -> dict[str, Any]:
    layout = {
        pid: {
            "blocks": filter_blocks(as_paragraphs(item["blocks"]), block_filter),
            "lines": item["lines"]["original"],
        }
        for pid, item in detected["pages"].items()
    }
    keys = (
        "blocks_accuracy",
        "blocks_accuracy_matched",
        "lines_accuracy",
        "perfect_pages",
        "tau_blocks_mean",
        "unmatched_predicted",
        "unmatched_truth",
        "truth_blocks",
        "order_ms_median",
        "order_ms_max",
    )
    out: dict[str, Any] = {}
    for name, params in orderers.items():
        true = evaluate_manifest(manifest, params, None, repeats=3)["overall"]
        found = evaluate_manifest(manifest, params, layout, repeats=3)["overall"]
        out[name] = {
            "params": params.to_dict(),
            "true_layout": {k: true[k] for k in keys},
            "detected_layout": {k: found[k] for k in keys},
        }
    multi = [p for p in manifest["pages"] if len(p["blocks"]) > 1]
    out["pages_with_more_than_one_block"] = len(multi)
    return out


def ldf_items(
    manifest: dict[str, Any],
    detected: dict[str, Any],
    block_filter: BlockFilter,
    params: OrderParams,
    line_key: str,
) -> list[dict[str, Any]]:
    items = []
    for page in manifest["pages"]:
        found = detected["pages"][page["id"]]
        blocks = filter_blocks(found["blocks"], block_filter)
        lines = found["lines"][line_key]
        order, _ = predict_sequences(
            [{"type": b["type"], "bbox": b["bbox"]} for b in blocks],
            [{"bbox": ln["bbox"], "polygon": ln.get("polygon")} for ln in lines],
            params,
        )
        items.append(
            {
                "page": page,
                "lines": lines,
                "blocks": blocks,
                "order": order,
                "rectification": found.get("rectification"),
            }
        )
    return items


def stage_costs(detected: dict[str, Any]) -> dict[str, Any]:
    return {
        name: {k: v for k, v in summary.items() if k != "describe"}
        for name, summary in detected["stages"].items()
    }


def page_ms(costs: dict[str, Any], names: list[str]) -> float:
    return sum(costs[name]["median_ms"] for name in names)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark em imagens reais (EXP-007)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    registry = json.loads((EXPERIMENT / "candidates.json").read_text(encoding="utf-8"))
    block_filter = BlockFilter(**registry["block_filter"])
    orderers = {name: OrderParams(**params) for name, params in registry["orderers"].items()}
    layout, orderer = layout_component(registry), order_component("anchored")
    seed_record = freeze_seeds(DEFAULT_SEED)
    datasets: dict[str, Any] = {}

    # --- GNHK: fotos de celular ---
    manifest, detected, path = load("gnhk")
    rect = {pid: item.get("rectification", {}) for pid, item in detected["pages"].items()}
    found_ids = {pid for pid, info in rect.items() if info.get("found")}
    gnhk_costs = stage_costs(detected)
    original = line_metrics(manifest, detected, "original")
    rectified = line_metrics(manifest, detected, "rectified")
    on_found = subset(manifest, found_ids)
    gnhk = {
        "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "pages": len(manifest["pages"]),
        "lines_original": original,
        "lines_rectified": rectified,
        "rectification": {
            "found": len(found_ids),
            "found_rate": len(found_ids) / len(manifest["pages"]),
            "failed": sum(1 for info in rect.values() if info.get("failed")),
            "found_by_group": {
                group: sum(
                    1 for p in manifest["pages"] if p["level"] == group and p["id"] in found_ids
                )
                for group in sorted({p["level"] for p in manifest["pages"]})
            },
            "f1_original_where_found": line_metrics(on_found, detected, "original")["bbox"]["0.5"]
            if found_ids
            else None,
            "f1_rectified_where_found": line_metrics(on_found, detected, "rectified")["bbox"]["0.5"]
            if found_ids
            else None,
        },
        "ldf2": convert_all(
            ldf_items(manifest, detected, block_filter, orderers["anchored"], "rectified"),
            layout,
            orderer,
        ),
        "costs": gnhk_costs,
    }
    datasets["gnhk"] = gnhk

    # --- BRESSAY: caligrafia em português, duas escalas ---
    for name in ("bressay-x3", "bressay-native"):
        manifest, detected, path = load(name)
        datasets[name] = {
            "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "pages": len(manifest["pages"]),
            "lines_original": line_metrics(manifest, detected, "original"),
            "blocks": block_metrics(manifest, detected, block_filter),
            "order": order_metrics(manifest, detected, block_filter, orderers),
            "ldf2": convert_all(
                ldf_items(manifest, detected, block_filter, orderers["anchored"], "original"),
                layout,
                orderer,
            ),
            "costs": stage_costs(detected),
        }

    main_set = datasets["bressay-x3"]
    f1_original = original["bbox"]["0.5"]["f1"]
    f1_rectified = rectified["bbox"]["0.5"]["f1"]
    where = gnhk["rectification"]
    order = main_set["order"]["anchored"]
    block_f1 = main_set["blocks"]["at_operating_point"]["0.5"]["f1"]
    synthetic_ms = sum(SYNTHETIC["page_ms"].values())
    gnhk_ms = page_ms(gnhk_costs, ["rectify-contour", "docufcn-norhand-line (retificado)", "heron"])
    bressay_ms = page_ms(main_set["costs"], ["docufcn-norhand-line (original)", "heron"])
    peaks = [
        stage["peak_rss_bytes"] or 0
        for item in datasets.values()
        for stage in item["costs"].values()
    ]
    verdicts = {
        "h1_lines_real_photos": {
            "f1_without_rectification": f1_original,
            "target_without": SYNTHETIC["lines_f1_strong"] - H1_MARGIN,
            "f1_with_rectification": f1_rectified,
            "target_with": SYNTHETIC["lines_f1_strong_rectified"] - H1_MARGIN,
            "met": f1_rectified >= SYNTHETIC["lines_f1_strong_rectified"] - H1_MARGIN,
            "met_without_rectification": f1_original >= SYNTHETIC["lines_f1_strong"] - H1_MARGIN,
        },
        "h2_rectification": {
            "found_rate": where["found_rate"],
            "target": H2_FOUND_RATE,
            "does_not_hurt": None
            if not found_ids
            else where["f1_rectified_where_found"]["f1"] >= where["f1_original_where_found"]["f1"],
            "met": where["found_rate"] >= H2_FOUND_RATE
            and bool(found_ids)
            and where["f1_rectified_where_found"]["f1"] >= where["f1_original_where_found"]["f1"],
        },
        "h3_lines_portuguese": {
            "f1_x3": main_set["lines_original"]["bbox"]["0.5"]["f1"],
            "f1_native": datasets["bressay-native"]["lines_original"]["bbox"]["0.5"]["f1"],
            "target": SYNTHETIC["lines_f1_clean"] - H3_MARGIN,
            "met": main_set["lines_original"]["bbox"]["0.5"]["f1"]
            >= SYNTHETIC["lines_f1_clean"] - H3_MARGIN,
        },
        "h4_blocks": {"f1_x3": block_f1, "target": H4_BLOCK_F1, "met": block_f1 >= H4_BLOCK_F1},
        "h5_order": {
            "true_layout": order["true_layout"]["blocks_accuracy"],
            "target_true": H5_ORDER_TRUE,
            "detected_layout": order["detected_layout"]["blocks_accuracy"],
            "target_detected": H5_ORDER_DETECTED,
            "met": order["true_layout"]["blocks_accuracy"] >= H5_ORDER_TRUE
            and order["detected_layout"]["blocks_accuracy"] >= H5_ORDER_DETECTED,
        },
        "h6_cost": {
            "synthetic_page_ms": synthetic_ms,
            "gnhk_page_ms": gnhk_ms,
            "bressay_x3_page_ms": bressay_ms,
            "max_peak_rss_bytes": max(peaks),
            "met": gnhk_ms <= H6_TIME_FACTOR * synthetic_ms
            and bressay_ms <= H6_TIME_FACTOR * synthetic_ms
            and max(peaks) <= H6_MAX_PEAK_BYTES,
        },
    }

    report = {
        "schema": SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-007",
        "git": git_state(),
        "environment": environment_snapshot(),
        "seed": seed_record,
        "license_status": {
            "gnhk": "VERIFIED (CC-BY-4.0, conforme declarado)",
            "bressay": "NEEDS VALIDATION (exceção experimental do usuário; não embasa produto)",
        },
        "pipeline": {
            "candidates": [c["id"] for c in registry["candidates"]],
            "block_filter": block_filter.to_dict(),
            "orderers": {name: params.to_dict() for name, params in orderers.items()},
        },
        "synthetic_reference": SYNTHETIC,
        "datasets": datasets,
        "verdicts": verdicts,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    for name, verdict in verdicts.items():
        print(name, json.dumps(verdict, ensure_ascii=False))
    for name, item in datasets.items():
        print(name, "LDF 2.0:", json.dumps(item["ldf2"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
