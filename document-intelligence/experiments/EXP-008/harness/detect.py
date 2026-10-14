"""Roda um candidato de detecção de linhas sobre um conjunto do EXP-008.

Saída, fora do Git: ``dataset/processed/exp-008/det-<candidato>-<conjunto>.json`` com as linhas por
página, o tempo de cada página e o resumo de custo medido pelo supervisor.

``--reuse-exp007`` (só para ``docufcn-norhand`` nos conjuntos de teste) copia as detecções já feitas
no EXP-007, em vez de rodar o modelo de novo: mesmo modelo, mesmos pesos, mesmas imagens.

Uso: ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-008/harness/detect.py --candidate <id> --set <conjunto>``
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from common import (
    EXP007_DATA,
    EXP007_DETECTED,
    EXPERIMENT,
    ROOT,
    SETS,
    detection_path,
    sha256_file,
    write_json,
)
from supervisor import Limits, run_candidate

from leitorum_di.procmem import available_system_memory_bytes


def _python(environment: str | None) -> str:
    if environment is None:
        return sys.executable
    scripts = "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    path = ROOT / environment / ".venv" / scripts
    if not path.is_file():
        raise SystemExit(f"Ambiente não instalado: {path}")
    return str(path)


def load_candidate(candidate_id: str) -> tuple[dict[str, Any], str, Path | None]:
    registry = json.loads((EXPERIMENT / "candidates.json").read_text(encoding="utf-8"))
    candidate = next(c for c in registry["candidates"] if c["id"] == candidate_id)
    options = {"id": candidate_id, "seed": 1234, **candidate.get("options", {})}
    weights_dir = None
    if candidate.get("weights", {}).get("local_dir"):
        weights_dir = ROOT / candidate["weights"]["local_dir"]
        options["weights_dir"] = str(weights_dir)
    candidate["options"] = options
    return candidate, _python(candidate.get("environment_path")), weights_dir


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[max(1, int(np.ceil(fraction * len(ordered)))) - 1]


def reuse_exp007(name: str) -> dict[str, Any]:
    source = json.loads((EXP007_DATA / EXP007_DETECTED[name]).read_text(encoding="utf-8"))
    if source["manifest_sha256"] != sha256_file(SETS[name]):
        raise SystemExit("detecção do EXP-007 não corresponde ao manifesto")
    summary = dict(source["stages"]["docufcn-norhand-line (original)"])
    summary.pop("describe", None)
    summary["reused_from"] = f"EXP-007 ({EXP007_DETECTED[name]})"
    return {
        "summary": summary,
        "pages": {pid: item["lines"]["original"] for pid, item in source["pages"].items()},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detecção de linhas (EXP-008)")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--set", required=True, choices=sorted(SETS))
    parser.add_argument("--reuse-exp007", action="store_true")
    parser.add_argument("--wait-free-s", type=float, default=900.0)
    parser.add_argument("--min-free-mib", type=int, default=1024)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    manifest_path = SETS[args.set]
    if args.reuse_exp007:
        if args.candidate != "docufcn-norhand" or args.set not in EXP007_DETECTED:
            raise SystemExit("--reuse-exp007 só vale para docufcn-norhand nos conjuntos de teste")
        result = reuse_exp007(args.set)
    else:
        candidate, python_exe, weights_dir = load_candidate(args.candidate)
        limits = Limits(min_free_system_bytes=args.min_free_mib * 1024 * 1024)
        started = time.monotonic()
        while time.monotonic() - started < args.wait_free_s:
            free = available_system_memory_bytes()
            if free is None or free >= limits.min_free_system_bytes:
                break
            time.sleep(2.0)
        run = run_candidate(
            candidate,
            manifest_path,
            ROOT,
            python_exe=python_exe,
            limits=limits,
            weights_dir=weights_dir,
        )
        if run.status != "OK":
            tail = "\n".join(run.stderr_tail[-8:])
            raise SystemExit(f"{args.candidate}/{args.set}: {run.status} — {run.reason}\n{tail}")
        times = [p["elapsed_ms"] for p in run.predictions]
        result = {
            "summary": {
                "pages": len(times),
                "failed_pages": [p["id"] for p in run.predictions if "error" in p["result"]],
                "median_ms": float(np.median(times)),
                "p95_ms": float(_percentile(times, 0.95)),
                "max_ms": float(max(times)),
                "peak_rss_bytes": run.peak_rss_bytes,
                "load_ms": run.load_ms,
                "wall_s": run.wall_s,
                "describe": run.describe,
            },
            "pages": {p["id"]: p["result"]["lines"] for p in run.predictions},
        }

    summary = result["summary"]
    write_json(
        detection_path(args.candidate, args.set),
        {
            "schema": "leitorum-di-line-detections/1",
            "candidate": args.candidate,
            "set": args.set,
            "manifest_sha256": sha256_file(manifest_path),
            **result,
        },
    )
    print(
        f"{args.candidate}/{args.set}: {summary['pages']} páginas, "
        f"{len(summary['failed_pages'])} com falha, mediana {summary['median_ms']:.0f} ms, "
        f"pico {(summary['peak_rss_bytes'] or 0) / 2**20:.0f} MiB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
