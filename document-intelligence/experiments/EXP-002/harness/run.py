"""CLI do benchmark de layout do EXP-002: executa um detector N vezes e grava os relatórios.

O relatório público (``--out``) traz métricas, latência, memória e validação LDF; as predições
completas vão para ``--predictions-out`` (por padrão em ``dataset/processed/exp-002/reports/``, fora
do Git, por tamanho).

Uso (a partir de ``document-intelligence/``):
``uv run --project experiments/EXP-002/envs/harness python experiments/EXP-002/harness/run.py
--candidate reference --manifest dataset/fixtures/exp-002/test-manifest.json``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evaluate import evaluate_pages, latency_stats, verdicts
from supervisor import Limits, RunResult, run_candidate
from to_ldf import to_ldf, validation_errors

from leitorum_di.procmem import available_system_memory_bytes
from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds

SCHEMA = "leitorum-di-layout-benchmark/1"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "dataset" / "fixtures" / "exp-002" / "test-manifest.json"
PREDICTIONS_DIR = ROOT / "dataset" / "processed" / "exp-002" / "reports"
CANDIDATES_FILE = EXPERIMENT / "candidates.json"

BUILTIN = {
    "reference": {
        "id": "reference",
        "kind": "reference",
        "adapter": "adapters.reference:ReferenceDetector",
        "license_status": "N/A (sem modelo)",
    }
}


def load_candidate(candidate_id: str) -> dict[str, Any]:
    if candidate_id in BUILTIN:
        return dict(BUILTIN[candidate_id])
    registry = json.loads(CANDIDATES_FILE.read_text(encoding="utf-8"))
    for candidate in registry["candidates"]:
        if candidate["id"] == candidate_id:
            return candidate
    raise SystemExit(f"Candidato desconhecido: {candidate_id}")


def candidate_python(candidate: dict[str, Any]) -> str:
    environment = candidate.get("environment")
    if not environment or environment == "envs/harness":
        return sys.executable
    scripts = "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    python = EXPERIMENT / environment / ".venv" / scripts
    if not python.is_file():
        raise SystemExit(f"Ambiente não instalado: {python}")
    return str(python)


def git_state() -> dict[str, object]:
    def git(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return out.stdout.strip()

    # Os próprios relatórios em evaluation/ não contam como alteração de código.
    status = git("status", "--porcelain", "--", ".", ":(exclude)evaluation")
    return {"commit": git("rev-parse", "HEAD"), "dirty": None if status is None else bool(status)}


def wait_for_free_memory(min_bytes: int, timeout_s: float) -> float:
    """Espera a RAM livre atingir o mínimo exigido, sem relaxá-lo; devolve a espera em s."""
    started = time.monotonic()
    while time.monotonic() - started < timeout_s:
        free = available_system_memory_bytes()
        if free is None or free >= min_bytes:
            break
        time.sleep(2.0)
    return time.monotonic() - started


def ldf_check(manifest: dict[str, Any], result: RunResult, detector: str) -> dict[str, Any]:
    pages = {page["id"]: page for page in manifest["pages"]}
    invalid, gaps, examples = 0, 0, []
    for prediction in result.predictions:
        document, page_gaps = to_ldf(
            pages[prediction["id"]], prediction["result"], detector, prediction["elapsed_ms"]
        )
        errors = validation_errors(document)
        gaps += len(page_gaps)
        if errors:
            invalid += 1
            examples.extend(errors[:2])
    return {
        "documents": len(result.predictions),
        "invalid": invalid,
        "graphic_box_gaps": gaps,
        "error_examples": examples[:5],
    }


def summarize_run(result: RunResult, manifest: dict[str, Any]) -> dict[str, Any]:
    predictions = {p["id"]: p["result"] for p in result.predictions}
    metrics = evaluate_pages(manifest, predictions)
    latency = latency_stats([p["elapsed_ms"] for p in result.predictions])
    summary = {k: v for k, v in result.to_dict().items() if k != "predictions"}
    summary.update(
        metrics=metrics,
        latency=latency,
        partial=result.status != "OK",
        verdicts=verdicts(metrics, latency, result.peak_rss_bytes),
        ldf=ldf_check(manifest, result, result.candidate_id),
    )
    return summary


def build_report(
    candidate: dict[str, Any],
    manifest_path: Path,
    repeats: int,
    limits: Limits,
    seed: int = DEFAULT_SEED,
    python_exe: str | None = None,
    weights_dir: Path | None = None,
    wait_free_s: float = 0.0,
) -> tuple[dict[str, Any], list[list[dict[str, Any]]]]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    seed_record = freeze_seeds(seed)
    runs, raw = [], []
    for _ in range(repeats):
        waited = wait_for_free_memory(limits.min_free_system_bytes, wait_free_s)
        result = run_candidate(
            candidate,
            manifest_path,
            ROOT,
            python_exe=python_exe,
            limits=limits,
            seed=seed,
            weights_dir=weights_dir,
        )
        runs.append({**summarize_run(result, manifest), "waited_for_memory_s": waited})
        raw.append(result.predictions)

    ok = [run for run in runs if run["status"] == "OK"]
    medians = [run["latency"]["median_ms"] for run in ok if run["latency"]["median_ms"] is not None]
    peaks = [run["peak_rss_bytes"] for run in ok if run["peak_rss_bytes"] is not None]
    first = ok[0]["metrics"] if ok else None
    report = {
        "schema": SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-002",
        "git": git_state(),
        "environment": environment_snapshot(),
        "seed": seed_record,
        "limits": asdict(limits),
        "dataset": {
            "id": manifest.get("dataset"),
            "manifest": Path(manifest_path).name,
            "manifest_sha256": hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest(),
            "pages": len(manifest["pages"]),
            "lines": sum(len(p["lines"]) for p in manifest["pages"]),
        },
        "candidate": {k: v for k, v in candidate.items() if k != "options"},
        "license_status": candidate.get("license_status", ""),
        "repeats": repeats,
        "summary": {
            "statuses": [run["status"] for run in runs],
            "lines_f1_bbox50": first["lines"]["bbox"]["0.5"]["f1"] if first else None,
            "lines_f1_by_level": {k: v["f1"] for k, v in first["lines_by_level"].items()}
            if first
            else None,
            "blocks_map50": first["blocks"]["map50"] if first and first["blocks"] else None,
            "median_ms_of_medians": statistics.median(medians) if medians else None,
            "peak_rss_bytes_max": max(peaks) if peaks else None,
        },
        "runs": runs,
    }
    return report, raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark de layout (EXP-002)")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", default=None)
    parser.add_argument("--predictions-out", default=None)
    parser.add_argument("--min-free-mib", type=int, default=1024)
    parser.add_argument("--wait-free-s", type=float, default=180.0)
    args = parser.parse_args(argv)

    candidate = load_candidate(args.candidate)
    weights_dir = None
    local_dir = (candidate.get("weights") or {}).get("local_dir")
    if local_dir:
        weights_dir = ROOT / local_dir
    candidate.setdefault("options", {}).update(
        {
            "id": candidate["id"],
            "seed": args.seed,
            "weights_dir": str(weights_dir) if weights_dir else None,
        }
    )
    report, raw = build_report(
        candidate,
        Path(args.manifest),
        args.repeats,
        Limits(min_free_system_bytes=args.min_free_mib * 1024 * 1024),
        seed=args.seed,
        python_exe=candidate_python(candidate),
        weights_dir=weights_dir,
        wait_free_s=args.wait_free_s,
    )
    stem = f"{candidate['id']}-{Path(args.manifest).stem}"
    predictions_out = Path(args.predictions_out or PREDICTIONS_DIR / f"{stem}-predictions.json")
    predictions_out.parent.mkdir(parents=True, exist_ok=True)
    predictions_out.write_text(
        json.dumps(raw, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        print(f"Relatório gravado em {out}")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
