"""Roda um reconhecedor PP-OCR, numa escala, sobre um conjunto de linhas preparado no EXP-009.

Saída fora do Git: ``dataset/processed/exp-010/read-<modelo>-x<escala>-<conjunto>.json``.

Uso: ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-010/harness/read.py --model <small|medium|latin> --scale <1|2|3> --set <conjunto>``
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
EXP009 = ROOT / "dataset" / "processed" / "exp-009"
OUT = ROOT / "dataset" / "processed" / "exp-010"
PYTHON = ROOT / "experiments" / "EXP-008" / "envs" / "ppocr" / ".venv" / "Scripts" / "python.exe"
MODELS = {
    "small": {
        "model_path": None,
        "model_sha256": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
    },
    "medium": {
        "model_path": "models/exp-010/PP-OCRv6_rec_medium.onnx",
        "model_sha256": "eef444829dbbe18d7fea59a3f6eb75647518d2b3a9568d27c92e42940204894b",
        "ocr_version": "PP-OCRv6",
        "model_type": "medium",
        "lang_type": "ch",
    },
    "latin": {
        "model_path": "models/exp-010/latin_PP-OCRv5_rec_mobile.onnx",
        "model_sha256": "b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a",
        "ocr_version": "PP-OCRv5",
        "model_type": "mobile",
        "lang_type": "latin",
    },
}
SETS = ("lines-exp001", "lines-gnhk")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Leitura de linhas (EXP-010)")
    parser.add_argument("--model", required=True, choices=sorted(MODELS))
    parser.add_argument("--scale", type=int, default=1, choices=(1, 2, 3))
    parser.add_argument("--set", required=True, choices=SETS)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    options = dict(MODELS[args.model])
    if options["model_path"]:
        options["model_path"] = str(ROOT / options["model_path"])
    candidate = {
        "id": f"ppocr-rec-{args.model}",
        "license_status": "VERIFIED",
        "benchmark_allowed": True,
        "adapter": "adapters.ppocr_rec:PPOCRLineReader",
        "options": {**options, "id": f"ppocr-rec-{args.model}", "scale": args.scale},
    }
    limits = Limits(latency_abort_ms=60_000.0, wall_timeout_s=5400.0)
    started = time.monotonic()
    while time.monotonic() - started < 900:
        free = available_system_memory_bytes()
        if free is None or free >= limits.min_free_system_bytes:
            break
        time.sleep(2.0)
    manifest = EXP009 / f"{args.set}-worker.json"
    run = run_candidate(candidate, manifest, ROOT, python_exe=str(PYTHON), limits=limits)
    if run.status != "OK":
        tail = "\n".join(run.stderr_tail[-8:])
        raise SystemExit(f"{args.model}/{args.set}: {run.status} — {run.reason}\n{tail}")
    times = [p["elapsed_ms"] for p in run.predictions]
    OUT.mkdir(parents=True, exist_ok=True)
    output = {
        "model": args.model,
        "scale": args.scale,
        "set": args.set,
        "summary": {
            "items": len(times),
            "failed": [p["id"] for p in run.predictions if "error" in p["result"]],
            "median_ms": float(np.median(times)),
            "p95_ms": float(np.percentile(times, 95)),
            "peak_rss_bytes": run.peak_rss_bytes,
            "load_ms": run.load_ms,
        },
        "items": {
            p["id"]: p["result"]["lines"][0]["text"] if p["result"]["lines"] else ""
            for p in run.predictions
        },  # fmt: skip
    }
    out = OUT / f"read-{args.model}-x{args.scale}-{args.set}.json"
    out.write_text(json.dumps(output, ensure_ascii=False), encoding="utf-8")
    peak = (run.peak_rss_bytes or 0) / 2**20
    print(f"{args.model} x{args.scale} {args.set}: {len(times)} itens, "
          f"mediana {np.median(times):.0f} ms, pico {peak:.0f} MiB")  # fmt: skip
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
