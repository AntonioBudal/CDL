"""Roda um leitor do PP-OCR sobre um conjunto do EXP-009, pelo supervisor.

Conjuntos: ``lines-exp001``, ``lines-gnhk``, ``lines-bressay`` (leitor de linha) e ``pages-bressay``
(leitor de página: detecção + fusão + leitura). Saída fora do Git:
``dataset/processed/exp-009/read-<conjunto>.json``.

Uso: ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-009/harness/read.py --set <conjunto> [--limit N]``
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from supervisor import Limits, run_candidate

from leitorum_di.procmem import available_system_memory_bytes

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed" / "exp-009"
PYTHON = ROOT / "experiments" / "EXP-008" / "envs" / "ppocr" / ".venv" / "Scripts" / "python.exe"
MODELS = {
    "PP-OCRv6_det_small.onnx": "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f",
    "PP-OCRv6_rec_small.onnx": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
}
SETS = ("lines-exp001", "lines-gnhk", "lines-bressay", "pages-bressay")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Leitura com o PP-OCR (EXP-009)")
    parser.add_argument("--set", required=True, choices=SETS)
    parser.add_argument("--limit", type=int, default=None, help="ensaio com os N primeiros itens")
    parser.add_argument("--wait-free-s", type=float, default=900.0)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    worker_manifest = DATA / f"{args.set}-worker.json"
    if args.limit:
        content = json.loads(worker_manifest.read_text(encoding="utf-8"))
        content["pages"] = content["pages"][: args.limit]
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(content, handle)
        handle.close()
        worker_manifest = Path(handle.name)

    calibration = json.loads(
        (ROOT / "experiments" / "EXP-008" / "calibration.json").read_text(encoding="utf-8")
    )
    page = args.set.startswith("pages")
    candidate = {
        "id": "ppocr-page" if page else "ppocr-line",
        "license_status": "VERIFIED",
        "benchmark_allowed": True,
        "adapter": "adapters.ppocr_rec:" + ("PPOCRPageReader" if page else "PPOCRLineReader"),
        "options": {
            "models": MODELS,
            "merge": calibration["candidates"]["ppocr-det"]["best"]["params"],
        },
    }
    limits = Limits(latency_abort_ms=60_000.0, wall_timeout_s=5400.0)
    started = time.monotonic()
    while time.monotonic() - started < args.wait_free_s:
        free = available_system_memory_bytes()
        if free is None or free >= limits.min_free_system_bytes:
            break
        time.sleep(2.0)
    run = run_candidate(candidate, worker_manifest, ROOT, python_exe=str(PYTHON), limits=limits)
    if run.status != "OK":
        raise SystemExit(
            f"{args.set}: {run.status} — {run.reason}\n" + "\n".join(run.stderr_tail[-8:])
        )
    times = [p["elapsed_ms"] for p in run.predictions]
    output = {
        "set": args.set,
        "limit": args.limit,
        "summary": {
            "items": len(times),
            "failed": [p["id"] for p in run.predictions if "error" in p["result"]],
            "median_ms": float(np.median(times)),
            "p95_ms": float(np.percentile(times, 95)),
            "peak_rss_bytes": run.peak_rss_bytes,
            "load_ms": run.load_ms,
            "wall_s": run.wall_s,
            "describe": run.describe,
        },
        "items": {p["id"]: p["result"]["lines"] for p in run.predictions},
    }
    suffix = f"-sample{args.limit}" if args.limit else ""
    out = DATA / f"read-{args.set}{suffix}.json"
    out.write_text(json.dumps(output, ensure_ascii=False), encoding="utf-8")
    summary = output["summary"]
    peak = (summary["peak_rss_bytes"] or 0) / 2**20
    print(
        f"{args.set}: {summary['items']} itens, {len(summary['failed'])} com falha, "
        f"mediana {summary['median_ms']:.0f} ms, pico {peak:.0f} MiB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
