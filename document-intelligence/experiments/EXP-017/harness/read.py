"""Roda o pipeline com escala automática (EXP-017) sobre um conjunto, com um alvo de altura.

Saída fora do Git: ``dataset/processed/exp-017/read-<conjunto>-t<alvo>.json`` (alvo 0 = sem escala).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from supervisor import Limits, run_candidate

from leitorum_di.procmem import available_system_memory_bytes

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-017"
PYTHON = ROOT / "experiments" / "EXP-008" / "envs" / "ppocr" / ".venv" / "Scripts" / "python.exe"
MODELS = {
    "PP-OCRv6_det_small.onnx": "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f",
    "PP-OCRv6_rec_small.onnx": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
}
# Leitor ajustado do EXP-014, exportado no T001 (export.json); só experimento.
FT_MODEL = ROOT / "models" / "exp-017" / "rec-ft-bressay.onnx"
FT_SHA256 = "d15ff16e74341bfceca507308ada731b68c4b7dd1237c9f8f0d8f0fc9ae0d372"
VARIANTS = ("cal-bressay", "cal-gnhk", "test-bressay", "test-gnhk")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline com escala automática (EXP-017)")
    parser.add_argument("--set", required=True, choices=VARIANTS)
    parser.add_argument("--target", type=int, default=0)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    calibration = json.loads(
        (ROOT / "experiments" / "EXP-008" / "calibration.json").read_text(encoding="utf-8")
    )
    candidate = {
        "id": "pipeline-exp017",
        "license_status": "NEEDS VALIDATION",
        "benchmark_allowed": True,
        "user_exception": "BRESSAY: exceção experimental do usuário (EXP-008 e seguintes)",
        "adapter": "pipeline:PagePipeline",
        "options": {
            "id": "pipeline-exp017",
            "target": args.target or None,
            "models": MODELS,
            "rec_model": str(FT_MODEL),
            "rec_sha256": FT_SHA256,
            "merge": calibration["candidates"]["ppocr-det"]["best"]["params"],
        },
    }
    limits = Limits(latency_abort_ms=60_000.0, wall_timeout_s=5400.0)
    started = time.monotonic()
    while time.monotonic() - started < 900:
        free = available_system_memory_bytes()
        if free is None or free >= limits.min_free_system_bytes:
            break
        time.sleep(2.0)
    manifest = DATA / f"{args.set}-worker.json"
    run = run_candidate(candidate, manifest, ROOT, python_exe=str(PYTHON), limits=limits)
    if run.status != "OK":
        tail = "\n".join(run.stderr_tail[-8:])
        raise SystemExit(f"{args.set}: {run.status} — {run.reason}\n{tail}")
    times = [p["elapsed_ms"] for p in run.predictions]
    output = {
        "set": args.set,
        "summary": {
            "pages": len(times),
            "failed": [p["id"] for p in run.predictions if "error" in p["result"]],
            "median_ms": float(np.median(times)),
            "p95_ms": float(np.percentile(times, 95)),
            "peak_rss_bytes": run.peak_rss_bytes,
            "load_ms": run.load_ms,
        },
        "items": {p["id"]: p["result"]["lines"] for p in run.predictions},
        "scales": {p["id"]: p["result"].get("page_scale", 1) for p in run.predictions},
    }
    (DATA / f"read-{args.set}-t{args.target}.json").write_text(
        json.dumps(output, ensure_ascii=False), encoding="utf-8"
    )
    peak = (run.peak_rss_bytes or 0) / 2**20
    print(
        f"{args.set}: {len(times)} páginas, mediana {np.median(times):.0f} ms, pico {peak:.0f} MiB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
