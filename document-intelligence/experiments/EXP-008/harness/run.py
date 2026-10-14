"""Benchmark do EXP-008: detectores de linha em manuscrito real, brutos e com fusão calibrada.

Para cada candidato e cada conjunto de teste: precisão, revocação e F1 (IoU ≥ 0,5), cobertura de
área, classes de erro, teto de fusão ideal e custo. As saídas fundidas são gravadas em LDF 2.0 e
validadas. O relatório traz só números e identificadores de arquivo.

Uso (árvore limpa): ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-008/harness/run.py --out evaluation/benchmarks/<arquivo>.json``
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from common import (
    EXPERIMENT,
    SETS,
    TEST_SETS,
    add,
    classify_unmatched,
    empty_counts,
    git_state,
    kept_boxes,
    load_detection,
    load_manifest,
    oracle_merge,
    sha256_file,
)
from coverage import page_coverage, summarize
from merge import MergeParams, merge_lines

from leitorum_di.contracts.ldf import LDFValidationError, build_document, component, validate
from leitorum_di.metrics.detection import detection_counts, precision_recall_f1
from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds

SCHEMA = "leitorum-di-line-detection-benchmark/1"
# Referências do EXP-007 (aceito) e critérios da spec §1.
EXP007 = {
    "test-gnhk": {"f1": 0.345, "oracle": 0.535},
    "test-bressay": {"f1": 0.372, "oracle": 0.712},
}
H1 = {"test-gnhk": 0.43, "test-bressay": 0.57}
H2 = {"test-gnhk": 0.60, "test-bressay": 0.70}
H4_MAX_MS = 3000.0
H4_MAX_PEAK = 2 * 1024**3


def evaluate(manifest: dict[str, Any], pages: dict[str, list[dict]]) -> dict[str, Any]:
    totals, ceiling = empty_counts(), empty_counts()
    kinds: Counter = Counter()
    areas = []
    groups: dict[str, dict[str, float]] = {}
    predicted = 0
    for page in manifest["pages"]:
        truths = [line["bbox"] for line in page["lines"]]
        boxes = kept_boxes(page, pages.get(page["id"], []))
        predicted += len(boxes)
        counts = detection_counts(truths, boxes, 0.5)
        add(totals, counts)
        add(groups.setdefault(page["level"], empty_counts()), counts)
        add(ceiling, detection_counts(truths, oracle_merge(truths, boxes), 0.5))
        kinds.update(classify_unmatched(truths, boxes))
        areas.append(page_coverage(page, boxes))
    result = precision_recall_f1(totals)
    return {
        "precision": result["precision"],
        "recall": result["recall"],
        "f1": result["f1"],
        "mean_iou": result["mean_iou"],
        "predicted_lines": predicted,
        "truth_lines": sum(len(p["lines"]) for p in manifest["pages"]),
        "oracle_merge_f1": precision_recall_f1(ceiling)["f1"],
        "unmatched_by_kind": dict(kinds),
        "coverage": summarize(areas),
        "f1_by_group": {k: precision_recall_f1(v)["f1"] for k, v in sorted(groups.items())},
    }


def ldf_check(manifest, pages, candidate: dict[str, Any]) -> dict[str, Any]:
    """Grava cada página (só linhas) em LDF 2.0 e conta os documentos válidos."""
    layout = component(
        candidate["id"],
        candidate["code"]["package"],
        license=candidate["code"]["license"],
        license_status=candidate["license_status"],
    )
    counts = {"documents": 0, "valid": 0, "not_representable": 0, "lines": 0}
    reasons: Counter = Counter()
    for page in manifest["pages"]:
        counts["documents"] += 1
        try:
            document = build_document(
                image={
                    "filename": Path(page["image"]).name,
                    "width": page["width"],
                    "height": page["height"],
                    "sha256": page["sha256"],
                },
                lines=[
                    {"bbox": ln["bbox"], "polygon": ln.get("polygon"), "score": ln.get("score")}
                    for ln in pages.get(page["id"], [])
                ],
                regions=[],
                stages={"layout": {"component": layout}},
                created_at="2026-10-13T00:00:00Z",
            )
        except LDFValidationError as error:
            counts["not_representable"] += 1
            reasons["+".join(sorted({issue.code for issue in error.issues}))] += 1
            continue
        except ValueError:
            counts["not_representable"] += 1
            reasons["ValueError"] += 1
            continue
        counts["valid"] += not validate(document)
        counts["lines"] += len(document["recognition"]["lines"])
    return {**counts, "reasons": dict(reasons)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark de detecção de linhas (EXP-008)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    registry = json.loads((EXPERIMENT / "candidates.json").read_text(encoding="utf-8"))
    calibration = json.loads((EXPERIMENT / "calibration.json").read_text(encoding="utf-8"))
    manifests = {name: load_manifest(name) for name in TEST_SETS}
    seed_record = freeze_seeds(DEFAULT_SEED)

    candidates: dict[str, Any] = {}
    for candidate in registry["candidates"]:
        cid = candidate["id"]
        params = MergeParams(**calibration["candidates"][cid]["best"]["params"])
        item: dict[str, Any] = {
            "license_status": candidate["license_status"],
            "merge_params": params.to_dict(),
            "sets": {},
        }
        for name in TEST_SETS:
            detection = load_detection(cid, name)
            merged = {pid: merge_lines(lines, params) for pid, lines in detection["pages"].items()}
            cost = {k: v for k, v in detection["summary"].items() if k != "describe"}
            item["sets"][name] = {
                "raw": evaluate(manifests[name], detection["pages"]),
                "merged": evaluate(manifests[name], merged),
                "cost": cost,
                "ldf2": ldf_check(manifests[name], merged, candidate),
            }
        for variant in ("raw", "merged"):
            item[f"mean_f1_{variant}"] = sum(
                item["sets"][name][variant]["f1"] for name in TEST_SETS
            ) / len(TEST_SETS)
        candidates[cid] = item

    def best_of(cid: str, name: str) -> float:
        return max(candidates[cid]["sets"][name][v]["f1"] for v in ("raw", "merged"))

    ranking = sorted(candidates, key=lambda cid: -candidates[cid]["mean_f1_merged"])
    best = ranking[0]
    models = [cid for cid in candidates if cid != "classic"]
    norhand = candidates["docufcn-norhand"]["sets"]
    area_rank = {
        name: sorted(
            candidates,
            key=lambda cid, name=name: (
                -(candidates[cid]["sets"][name]["merged"]["coverage"]["area_f1"] or 0)
            ),
        )
        for name in TEST_SETS
    }
    f1_rank = {
        name: sorted(
            candidates, key=lambda cid, name=name: -candidates[cid]["sets"][name]["merged"]["f1"]
        )
        for name in TEST_SETS
    }
    best_cost = candidates[best]["sets"]
    verdicts = {
        "h1_merge_recovers_the_ceiling": {
            "f1_merged": {name: norhand[name]["merged"]["f1"] for name in TEST_SETS},
            "target": H1,
            "met": all(norhand[name]["merged"]["f1"] >= H1[name] for name in TEST_SETS),
        },
        "h2_some_candidate_is_good_enough": {
            "best_f1": {
                name: {cid: best_of(cid, name) for cid in candidates} for name in TEST_SETS
            },
            "target": H2,
            "met_by": [
                cid
                for cid in candidates
                if all(best_of(cid, name) >= H2[name] for name in TEST_SETS)
            ],
        },
        "h3_classic_below_models": {
            "classic": {name: best_of("classic", name) for name in TEST_SETS},
            "best_model": {name: max(best_of(cid, name) for cid in models) for name in TEST_SETS},
            "met": all(
                best_of("classic", name) < max(best_of(cid, name) for cid in models)
                for name in TEST_SETS
            ),
        },
        "h4_cost_of_best": {
            "candidate": best,
            "median_ms": {name: best_cost[name]["cost"]["median_ms"] for name in TEST_SETS},
            "peak_rss_bytes": {
                name: best_cost[name]["cost"]["peak_rss_bytes"] for name in TEST_SETS
            },
            "met": all(
                best_cost[name]["cost"]["median_ms"] <= H4_MAX_MS
                and (best_cost[name]["cost"]["peak_rss_bytes"] or 0) <= H4_MAX_PEAK
                for name in TEST_SETS
            ),
        },
        "h5_same_verdict_by_coverage": {
            "ranking_by_f1": f1_rank,
            "ranking_by_area_f1": area_rank,
            "met": all(f1_rank[name][0] == area_rank[name][0] for name in TEST_SETS),
        },
    }
    verdicts["h2_some_candidate_is_good_enough"]["met"] = bool(
        verdicts["h2_some_candidate_is_good_enough"]["met_by"]
    )

    report = {
        "schema": SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-008",
        "git": git_state(),
        "environment": environment_snapshot(),
        "seed": seed_record,
        "license_status": {
            "gnhk": "VERIFIED (CC-BY-4.0, conforme declarado)",
            "bressay": "NEEDS VALIDATION (exceção experimental do usuário; não embasa produto)",
        },
        "datasets": {
            name: {
                "manifest_sha256": sha256_file(SETS[name]),
                "pages": len(manifests[name]["pages"]),
                "truth_lines": sum(len(p["lines"]) for p in manifests[name]["pages"]),
            }
            for name in TEST_SETS
        },
        "exp007_reference": EXP007,
        "calibration_sets": calibration["sets"],
        "ranking_by_mean_f1_merged": ranking,
        "candidates": candidates,
        "verdicts": verdicts,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    for cid in ranking:
        for name in TEST_SETS:
            data = candidates[cid]["sets"][name]
            raw, merged = data["raw"], data["merged"]
            print(
                f"{cid:20s} {name:13s} bruto {raw['f1']:.3f} fundido {merged['f1']:.3f} "
                f"(P {merged['precision']:.3f} R {merged['recall']:.3f}) "
                f"teto {raw['oracle_merge_f1']:.3f} área {merged['coverage']['area_f1']:.3f} "
                f"{data['cost']['median_ms']:.0f} ms"
            )
    for name, verdict in verdicts.items():
        print(name, "→", verdict["met"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
