"""EXP-022, T003: roda o pipeline do EXP-019 nas fotos das páginas impressas.

Monta o manifesto a partir de ``dataset/raw/exp-022/fotos/`` (id = nome do arquivo, sem extensão;
a associação com a página do BRESSAY é feita na pontuação). Saída fora do Git:
``dataset/processed/exp-022/read-fotos-<leitor>.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image
from supervisor import Limits, run_candidate

from leitorum_di.procmem import available_system_memory_bytes

ROOT = Path(__file__).resolve().parents[3]
PHOTOS = ROOT / "dataset" / "raw" / "exp-022" / "fotos"
DATA = ROOT / "dataset" / "processed" / "exp-022"
PYTHON = ROOT / "experiments" / "EXP-008" / "envs" / "ppocr" / ".venv" / "Scripts" / "python.exe"
MODELS = {
    "PP-OCRv6_det_small.onnx": "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f",
    "PP-OCRv6_rec_small.onnx": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
}
# Leitor ajustado do EXP-014, exportado no EXP-017; só experimento.
FT_MODEL = ROOT / "models" / "exp-017" / "rec-ft-bressay.onnx"
FT_SHA256 = "d15ff16e74341bfceca507308ada731b68c4b7dd1237c9f8f0d8f0fc9ae0d372"
READERS = ("original", "ft")
SUFFIXES = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
TARGET = 80  # alvo de escala do EXP-013


def build_manifest() -> Path:
    pages = []
    for path in sorted(p for p in PHOTOS.iterdir() if p.suffix.lower() in SUFFIXES):
        with Image.open(path) as image:
            width, height = image.size
        pages.append(
            {
                "id": path.stem,
                "image": path.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "width": width,
                "height": height,
            }
        )
    DATA.mkdir(parents=True, exist_ok=True)
    manifest = DATA / "fotos-worker.json"
    manifest.write_text(json.dumps({"pages": pages}, ensure_ascii=False), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fotos de páginas impressas (EXP-022)")
    parser.add_argument("--reader", required=True, choices=READERS)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    calibration = json.loads(
        (ROOT / "experiments" / "EXP-008" / "calibration.json").read_text(encoding="utf-8")
    )
    candidate = {
        "id": f"pipeline-exp022-{args.reader}",
        "license_status": "NEEDS VALIDATION",
        "benchmark_allowed": True,
        "user_exception": "BRESSAY: exceção experimental do usuário (EXP-008 e seguintes)",
        "adapter": "pipeline:PagePipeline",
        "options": {
            "id": f"pipeline-exp022-{args.reader}",
            "target": TARGET,
            "models": MODELS,
            "merge": calibration["candidates"]["ppocr-det"]["best"]["params"],
        },
    }
    if args.reader == "ft":
        candidate["options"] |= {"rec_model": str(FT_MODEL), "rec_sha256": FT_SHA256}
    limits = Limits(latency_abort_ms=120_000.0, wall_timeout_s=3600.0)
    started = time.monotonic()
    while time.monotonic() - started < 900:
        free = available_system_memory_bytes()
        if free is None or free >= limits.min_free_system_bytes:
            break
        time.sleep(2.0)
    manifest = build_manifest()
    run = run_candidate(candidate, manifest, ROOT, python_exe=str(PYTHON), limits=limits)
    if run.status != "OK":
        tail = "\n".join(run.stderr_tail[-8:])
        raise SystemExit(f"fotos: {run.status} — {run.reason}\n{tail}")
    times = [p["elapsed_ms"] for p in run.predictions]
    output = {
        "set": "fotos",
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
    (DATA / f"read-fotos-{args.reader}.json").write_text(
        json.dumps(output, ensure_ascii=False), encoding="utf-8"
    )
    peak = (run.peak_rss_bytes or 0) / 2**20
    print(
        f"fotos ({args.reader}): {len(times)} páginas, "
        f"mediana {np.median(times):.0f} ms, pico {peak:.0f} MiB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
