"""Benchmark de ordem de leitura do EXP-003: todos os ordenadores calibrados sobre um layout.

Sem ``--detected``, usa o layout verdadeiro do manifesto. Com ``--detected <arquivo>``, usa o layout
produzido por ``detect.py`` (linhas e blocos preditos) e reporta a decomposição da perda.

Os ordenadores rodam neste processo: tempo por página pela mediana de 3 execuções e pico de
alocação por ``tracemalloc``. Uso (a partir de ``document-intelligence/``):
``uv run --project experiments/EXP-002/envs/harness python experiments/EXP-003/harness/run.py
--out evaluation/benchmarks/<arquivo>.json``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from order_eval import evaluate_manifest, predict_sequences, true_layout
from orderers import OrderParams
from to_ldf import to_ldf, validation_errors

from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds

SCHEMA = "leitorum-di-reading-order-benchmark/1"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "dataset" / "fixtures" / "exp-003" / "test-manifest.json"
CALIBRATION = EXPERIMENT / "calibration.json"

H1_TRUE_LAYOUT = 0.95
H2_DETECTED_LAYOUT = 0.85
H4_MAX_MS = 50.0


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


def ldf_check(
    manifest: dict[str, Any], params: OrderParams, detected: dict | None
) -> dict[str, int]:
    """Converte cada página ordenada para o LDF e valida contra o JSON Schema."""
    invalid = gaps = documents = 0
    for page in manifest["pages"]:
        if detected is not None and page["id"] not in detected:
            continue
        if detected is None:
            blocks, lines = true_layout(page)
        else:
            blocks, lines = detected[page["id"]]["blocks"], detected[page["id"]]["lines"]
        order, _ = predict_sequences(blocks, lines, params)
        prediction = {
            "lines": [{"bbox": ln["bbox"], "polygon": ln.get("polygon")} for ln in lines],
            "blocks": [{"type": b["type"], "bbox": b["bbox"]} for b in blocks],
        }
        document, page_gaps = to_ldf(page, prediction, params.method, order=order)
        documents += 1
        gaps += len(page_gaps)
        invalid += bool(validation_errors(document))
    return {"documents": documents, "invalid": invalid, "graphic_box_outside_reading_order": gaps}


def strip_pages(result: dict[str, Any]) -> dict[str, Any]:
    """Tira do relatório as listas por página, deixando só o que a análise usa."""
    pages = [
        {k: p[k] for k in ("id", "family", "level", "blocks_full", "blocks_matched", "lines_full",
                           "displaced_types", "unmatched_predicted", "unmatched_truth")}
        for p in result["per_page"]
    ]  # fmt: skip
    return {**{k: v for k, v in result.items() if k != "per_page"}, "per_page": pages}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark de ordem de leitura (EXP-003)")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--detected", default=None, help="layout detectado (saída de detect.py)")
    parser.add_argument(
        "--layout-key", default="rectified", help="variante de linhas do layout detectado"
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    detected = None
    source = "true"
    if args.detected:
        raw = json.loads(Path(args.detected).read_text(encoding="utf-8"))
        detected = {
            pid: {"blocks": item["blocks"], "lines": item["lines"][args.layout_key]}
            for pid, item in raw["pages"].items()
        }
        source = f"detected ({args.layout_key})"

    seed_record = freeze_seeds(DEFAULT_SEED)
    orderers = {}
    for name, item in calibration["orderers"].items():
        params = OrderParams(**item["params"])
        tracemalloc.start()
        result = evaluate_manifest(manifest, params, detected, repeats=3)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        overall = result["overall"]
        threshold = H1_TRUE_LAYOUT if detected is None else H2_DETECTED_LAYOUT
        orderers[name] = {
            "params": params.to_dict(),
            "python_peak_alloc_bytes": peak,
            "ldf": ldf_check(manifest, params, detected),
            "verdicts": {
                "accuracy_target": threshold,
                "meets_accuracy": overall["blocks_accuracy"] >= threshold,
                "meets_accuracy_in_every_family": all(
                    v["blocks_accuracy"] >= threshold for v in result["by_family"].values()
                ),
                "h4_cost": overall["order_ms_median"] <= H4_MAX_MS,
            },
            **strip_pages(result),
        }

    report = {
        "schema": SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-003",
        "git": git_state(),
        "environment": environment_snapshot(),
        "seed": seed_record,
        "layout_source": source,
        "dataset": {
            "id": manifest.get("dataset"),
            "manifest": Path(args.manifest).name,
            "manifest_sha256": hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest(),
            "pages": len(manifest["pages"]),
            "blocks": sum(len(p["blocks"]) for p in manifest["pages"]),
        },
        "orderers": orderers,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    sys.stdout.reconfigure(encoding="utf-8")
    for name, item in orderers.items():
        o = item["overall"]
        families = {k: round(v["blocks_accuracy"], 3) for k, v in item["by_family"].items()}
        print(
            f"{name}: blocos {o['blocks_accuracy']:.4f} "
            f"(casados {o['blocks_accuracy_matched']:.4f}) "
            f"linhas {o['lines_accuracy']:.4f} | {families} | {o['order_ms_median']:.2f} ms"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
