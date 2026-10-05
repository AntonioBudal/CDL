"""Mede um retificador isoladamente e gera o manifesto das páginas retificadas.

Para cada página do conjunto (por padrão, só as degradadas do ``test``): erro dos cantos da folha
contra a verdade de chão, tempo por página e pico de memória. As imagens retificadas ficam em
``dataset/processed/exp-002/rectified/<retificador>/`` e o manifesto retificado (com a homografia
de cada página) em ``dataset/processed/exp-002/rectified/`` — ambos fora do Git.

Uso: ``python rectify_run.py --rectifier contour|docufcn-page --out <relatório.json>``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from evaluate import latency_stats
from rectify import corner_error
from run import ROOT, candidate_python, git_state, load_candidate, wait_for_free_memory
from supervisor import Limits, run_candidate

from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds

SCHEMA = "leitorum-di-rectification-benchmark/1"
RECTIFIED_DIR = ROOT / "dataset" / "processed" / "exp-002" / "rectified"
RECTIFIERS = {
    "contour": {
        "id": "rectify-contour",
        "kind": "reference",  # sem modelo: não passa pelo portão de licença
        "adapter": "adapters.rectifiers:ContourRectifier",
        "license_status": "VERIFIED (OpenCV, Apache-2.0; sem pesos)",
    },
    "docufcn-page": None,  # vem de candidates.json
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark de retificação (EXP-002)")
    parser.add_argument("--rectifier", required=True, choices=list(RECTIFIERS))
    parser.add_argument(
        "--manifest", default=str(ROOT / "dataset/fixtures/exp-002/test-manifest.json")
    )
    parser.add_argument("--levels", nargs="+", default=["light", "strong"])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--out", required=True)
    parser.add_argument("--wait-free-s", type=float, default=180.0)
    args = parser.parse_args(argv)

    source = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    pages = [p for p in source["pages"] if p["level"] in args.levels]
    name = args.rectifier
    subset_stem = f"{Path(args.manifest).stem}-{'-'.join(args.levels)}"
    output_dir = RECTIFIED_DIR / name / subset_stem
    output_dir.mkdir(parents=True, exist_ok=True)
    subset_path = RECTIFIED_DIR / f"{subset_stem}-source.json"
    subset_path.write_text(
        json.dumps({**source, "pages": pages}, ensure_ascii=False), encoding="utf-8"
    )

    weights_dir = None
    if RECTIFIERS[name] is not None:
        candidate = dict(RECTIFIERS[name])
    else:
        candidate = load_candidate(name)
        candidate["adapter"] = "adapters.rectifiers:DocUFCNPageRectifier"
        weights_dir = ROOT / candidate["weights"]["local_dir"]
    candidate["options"] = {
        "id": candidate["id"],
        "output_dir": str(output_dir),
        "seed": DEFAULT_SEED,
        "weights_dir": str(weights_dir) if weights_dir else None,
    }

    limits = Limits()
    seed_record = freeze_seeds(DEFAULT_SEED)
    truth = {p["id"]: p for p in pages}
    runs, last_ok = [], None
    for _ in range(args.repeats):
        waited = wait_for_free_memory(limits.min_free_system_bytes, args.wait_free_s)
        result = run_candidate(
            candidate,
            subset_path,
            ROOT,
            python_exe=candidate_python(candidate),
            limits=limits,
            weights_dir=weights_dir,
        )
        errors, found = {}, 0
        for prediction in result.predictions:
            info = prediction["result"]["rectification"]
            found += info["found"]
            errors[prediction["id"]] = corner_error(
                info["quad"], truth[prediction["id"]]["page_corners"]
            )
        by_level = {}
        for level in args.levels:
            values = [e for pid, e in errors.items() if truth[pid]["level"] == level]
            if values:
                by_level[level] = {
                    "mean_px": statistics.fmean(values),
                    "median_px": statistics.median(values),
                    "max_px": max(values),
                }
        summary = {k: v for k, v in result.to_dict().items() if k != "predictions"}
        summary.update(
            waited_for_memory_s=waited,
            latency=latency_stats([p["elapsed_ms"] for p in result.predictions]),
            pages_found=found,
            corner_error_px=by_level,
            corner_error_mean_px=statistics.fmean(errors.values()) if errors else None,
        )
        runs.append(summary)
        if result.status == "OK":
            last_ok = result

    if last_ok is not None:
        rectified_pages = []
        for prediction in last_ok.predictions:
            info = prediction["result"]["rectification"]
            image = Path(info["output"])
            rectified_pages.append(
                {
                    "id": prediction["id"],
                    "image": image.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                    "width": info["size"][0],
                    "height": info["size"][1],
                    "level": truth[prediction["id"]]["level"],
                    "homography": info["homography"],
                    "found": info["found"],
                }
            )
        manifest = {
            "schema": "leitorum-di-rectified-pages/1",
            "rectifier": name,
            "source_manifest": Path(args.manifest).name,
            "levels": args.levels,
            "pages": rectified_pages,
        }
        (RECTIFIED_DIR / f"{name}-{subset_stem}-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
        )

    ok = [run for run in runs if run["status"] == "OK"]
    report = {
        "schema": SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-002",
        "git": git_state(),
        "environment": environment_snapshot(),
        "seed": seed_record,
        "limits": asdict(limits),
        "dataset": {
            "manifest": Path(args.manifest).name,
            "levels": args.levels,
            "pages": len(pages),
        },
        "rectifier": {k: v for k, v in candidate.items() if k != "options"},
        "summary": {
            "statuses": [run["status"] for run in runs],
            "median_ms": [run["latency"]["median_ms"] for run in ok],
            "peak_rss_bytes_max": max((run["peak_rss_bytes"] or 0 for run in ok), default=None),
            "corner_error_px": ok[0]["corner_error_px"] if ok else None,
            "pages_found": ok[0]["pages_found"] if ok else None,
        },
        "runs": runs,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
