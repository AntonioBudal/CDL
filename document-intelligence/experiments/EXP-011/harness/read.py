"""Lê um conjunto de linhas com o PP-OCRv6 small e recorte ampliado 2× (melhor leitor do EXP-010).

Conjuntos: ``val-lines`` (validação do BRESSAY, preparada aqui) e ``lines-bressay`` (todas as
linhas de teste, preparadas no EXP-009). Saída fora do Git: ``dataset/processed/exp-011/read-<conjunto>.json``.
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
OUT = ROOT / "dataset" / "processed" / "exp-011"
MANIFESTS = {
    "val-lines": OUT / "val-lines-worker.json",
    "lines-bressay": ROOT / "dataset" / "processed" / "exp-009" / "lines-bressay-worker.json",
}
PYTHON = ROOT / "experiments" / "EXP-008" / "envs" / "ppocr" / ".venv" / "Scripts" / "python.exe"
SMALL_SHA = "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Leitura de linhas (EXP-011)")
    parser.add_argument("--set", required=True, choices=sorted(MANIFESTS))
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    candidate = {
        "id": "ppocr-rec-small-x2",
        "license_status": "VERIFIED",
        "benchmark_allowed": True,
        "adapter": "adapters.ppocr_rec:PPOCRLineReader",
        "options": {
            "id": "ppocr-rec-small-x2",
            "model_path": None,
            "model_sha256": SMALL_SHA,
            "scale": 2,
        },
    }
    limits = Limits(latency_abort_ms=60_000.0, wall_timeout_s=5400.0)
    started = time.monotonic()
    while time.monotonic() - started < 900:
        free = available_system_memory_bytes()
        if free is None or free >= limits.min_free_system_bytes:
            break
        time.sleep(2.0)
    run = run_candidate(candidate, MANIFESTS[args.set], ROOT, python_exe=str(PYTHON), limits=limits)
    if run.status != "OK":
        raise SystemExit(f"{args.set}: {run.status} — {run.reason}")
    times = [p["elapsed_ms"] for p in run.predictions]
    OUT.mkdir(parents=True, exist_ok=True)
    output = {
        "set": args.set,
        "summary": {
            "items": len(times),
            "median_ms": float(np.median(times)),
            "peak_rss_bytes": run.peak_rss_bytes,
        },
        "items": {
            p["id"]: (p["result"]["lines"][0]["text"] if p["result"]["lines"] else "")
            for p in run.predictions
        },
    }
    (OUT / f"read-{args.set}.json").write_text(
        json.dumps(output, ensure_ascii=False), encoding="utf-8"
    )
    print(f"{args.set}: {len(times)} linhas, mediana {np.median(times):.0f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
