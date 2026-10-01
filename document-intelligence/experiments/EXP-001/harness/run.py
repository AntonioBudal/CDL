"""CLI do benchmark do EXP-001: executa um candidato N vezes e grava o relatório JSON.

Uso (a partir de ``document-intelligence/``):
``uv run --project experiments/EXP-001/envs/harness python experiments/EXP-001/harness/run.py
--candidate echo-reference``
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from evaluate import evaluate, latency_stats, verdicts
from supervisor import Limits, RunResult, run_candidate, sha256_file

from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds

SCHEMA = "leitorum-di-htr-benchmark/1"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "dataset" / "fixtures" / "exp-001" / "synthetic-manifest.json"
CANDIDATES_FILE = EXPERIMENT / "candidates.json"

# Reconhecedores internos do harness (não são modelos; não passam pelo portão de licença).
BUILTIN = {
    "echo-reference": {
        "id": "echo-reference",
        "kind": "reference",
        "adapter": "adapters.echo:EchoRecognizer",
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
    """Interpretador do ambiente isolado do candidato (ou o atual, para reconhecedores internos)."""
    environment = candidate.get("environment")
    if not environment:
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

    status = git("status", "--porcelain", "--", ".")
    return {"commit": git("rev-parse", "HEAD"), "dirty": None if status is None else bool(status)}


def summarize_run(result: RunResult, manifest: dict[str, Any]) -> dict[str, Any]:
    metrics = evaluate(manifest, result.predictions)
    latency = latency_stats(result.predictions)
    summary = result.to_dict()
    summary["metrics"] = metrics
    summary["latency"] = latency
    summary["partial"] = result.status != "OK"
    summary["verdicts"] = verdicts(metrics, latency, result.peak_rss_bytes)
    return summary


def build_report(
    candidate: dict[str, Any],
    manifest_path: Path,
    repeats: int,
    limits: Limits,
    seed: int = DEFAULT_SEED,
    python_exe: str | None = None,
    weights_dir: Path | None = None,
) -> dict[str, Any]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    seed_record = freeze_seeds(seed)
    runs = []
    for _ in range(repeats):
        result = run_candidate(
            candidate,
            manifest_path,
            ROOT,
            python_exe=python_exe,
            limits=limits,
            seed=seed,
            weights_dir=weights_dir,
        )
        runs.append(summarize_run(result, manifest))

    ok = [run for run in runs if run["status"] == "OK"]
    medians = [run["latency"]["median_ms"] for run in ok if run["latency"]["median_ms"] is not None]
    peaks = [run["peak_rss_bytes"] for run in ok if run["peak_rss_bytes"] is not None]
    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-001",
        "git": git_state(),
        "environment": environment_snapshot(),
        "seed": seed_record,
        "limits": asdict(limits),
        "dataset": {
            "id": manifest.get("dataset"),
            "origin": manifest.get("origin"),
            "manifest": Path(manifest_path).name,
            "manifest_sha256": sha256_file(Path(manifest_path)),
            "lines": len(manifest["lines"]),
        },
        "candidate": {k: v for k, v in candidate.items() if k != "options"},
        "license_status": candidate.get("license_status", ""),
        "repeats": repeats,
        "summary": {
            "statuses": [run["status"] for run in runs],
            "cer_micro": ok[0]["metrics"]["cer_micro"] if ok else None,
            "wer_micro": ok[0]["metrics"]["wer_micro"] if ok else None,
            "median_ms_of_medians": statistics.median(medians) if medians else None,
            "median_ms_min": min(medians) if medians else None,
            "median_ms_max": max(medians) if medians else None,
            "peak_rss_bytes_max": max(peaks) if peaks else None,
        },
        "runs": runs,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark de reconhecimento de linha (EXP-001)")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", default=None)
    parser.add_argument(
        "--min-free-mib",
        type=int,
        default=1024,
        help="RAM livre mínima do sistema para iniciar (padrão do plano: 1024). "
        "O valor usado fica registrado em 'limits' no relatório.",
    )
    args = parser.parse_args(argv)

    candidate = load_candidate(args.candidate)
    report = build_report(
        candidate,
        Path(args.manifest),
        args.repeats,
        Limits(min_free_system_bytes=args.min_free_mib * 1024 * 1024),
        seed=args.seed,
        python_exe=candidate_python(candidate),
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
