"""Roda o pipeline do EXP-019 com o leitor treinado com degradações de foto (EXP-021).

O SHA-256 do modelo vem de ``experiments/EXP-021/export.json``. Saída fora do Git:
``dataset/processed/exp-021/read-<conjunto>-aug.json``.
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
DATA = ROOT / "dataset" / "processed" / "exp-021"
PYTHON = ROOT / "experiments" / "EXP-008" / "envs" / "ppocr" / ".venv" / "Scripts" / "python.exe"
MODELS = {
    "PP-OCRv6_det_small.onnx": "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f",
    "PP-OCRv6_rec_small.onnx": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
}
# Leitor do EXP-021 (BRESSAY + degradações de foto), exportado no T002; só experimento.
AUG_MODEL = ROOT / "models" / "exp-021" / "rec-aug-bressay.onnx"
EXPORT = ROOT / "experiments" / "EXP-021" / "export.json"
VARIANTS = ("test-bressay-clean", "test-bressay-light", "test-bressay-strong")
READERS = ("aug",)
TARGET = 80  # alvo de escala do EXP-013


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Leitor treinado com degradações (EXP-021)")
    parser.add_argument("--set", required=True, choices=VARIANTS)
    parser.add_argument("--reader", default="aug", choices=READERS)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    calibration = json.loads(
        (ROOT / "experiments" / "EXP-008" / "calibration.json").read_text(encoding="utf-8")
    )
    candidate = {
        "id": f"pipeline-exp021-{args.reader}",
        "license_status": "NEEDS VALIDATION",
        "benchmark_allowed": True,
        "user_exception": "BRESSAY: exceção experimental do usuário (EXP-008 e seguintes)",
        "adapter": "pipeline:PagePipeline",
        "options": {
            "id": f"pipeline-exp021-{args.reader}",
            "target": TARGET,
            "models": MODELS,
            "merge": calibration["candidates"]["ppocr-det"]["best"]["params"],
        },
    }
    sha256 = json.loads(EXPORT.read_text(encoding="utf-8"))["onnx_sha256"]
    candidate["options"] |= {"rec_model": str(AUG_MODEL), "rec_sha256": sha256}
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
        "reader": args.reader,
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
    (DATA / f"read-{args.set}-{args.reader}.json").write_text(
        json.dumps(output, ensure_ascii=False), encoding="utf-8"
    )
    peak = (run.peak_rss_bytes or 0) / 2**20
    print(
        f"{args.set} ({args.reader}): {len(times)} páginas, "
        f"mediana {np.median(times):.0f} ms, pico {peak:.0f} MiB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
