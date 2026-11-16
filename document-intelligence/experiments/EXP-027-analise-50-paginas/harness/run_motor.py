"""T001b — reproduz a leitura do produto: roda ``leitorum_motor read`` (processo à parte, ambiente
do motor) em cada foto do manifesto e guarda ``motor/pNN.json`` (fora do Git). Retomável: pula as
páginas já lidas. Fotos HEIC são convertidas para PNG antes (o motor lê pelo OpenCV).

Uso: ``python run_motor.py [--only p01,p02] [--force]``
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from paths import MANIFEST, MOTOR_CONFIG, MOTOR_DIR, MOTOR_OUT, MOTOR_PYTHON, PHOTOS, PROCESSED

CONVERTED = PROCESSED / "fotos-png"


def ensure_readable(path: Path, pid: str) -> Path:
    """Devolve um caminho que o OpenCV abre: a própria foto, ou um PNG convertido (HEIC)."""
    if path.suffix.lower() not in {".heic", ".heif"}:
        return path
    CONVERTED.mkdir(parents=True, exist_ok=True)
    target = CONVERTED / f"{pid}.png"
    if not target.is_file():
        from PIL import Image, ImageOps

        with Image.open(path) as image:
            ImageOps.exif_transpose(image).convert("RGB").save(target)
    return target


def read_page(image: Path, out: Path) -> dict:
    started = time.perf_counter()
    completed = subprocess.run(
        [
            str(MOTOR_PYTHON),
            "-I",
            "-m",
            "leitorum_motor",
            "read",
            "--image",
            str(image),
            "--out",
            str(out),
            "--config",
            str(MOTOR_CONFIG),
        ],
        cwd=str(MOTOR_DIR),
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    return {
        "exit_code": completed.returncode,
        "stderr_type": completed.stderr.strip().splitlines()[-1]
        if completed.stderr.strip()
        else "",
        "wall_s": round(time.perf_counter() - started, 1),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Leitura das páginas pelo motor do produto")
    parser.add_argument("--only", default="")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    wanted = set(args.only.split(",")) if args.only else None
    MOTOR_OUT.mkdir(parents=True, exist_ok=True)
    log_path = MOTOR_OUT / "_runs.json"
    runs = json.loads(log_path.read_text(encoding="utf-8")) if log_path.is_file() else {}
    for pid, page in manifest["pages"].items():
        if wanted and pid not in wanted:
            continue
        out = MOTOR_OUT / f"{pid}.json"
        if out.is_file() and not args.force:
            continue
        image = ensure_readable(PHOTOS / page["file"], pid)
        result = read_page(image, out)
        result["at"] = datetime.now(UTC).isoformat()
        runs[pid] = result
        log_path.write_text(json.dumps(runs, indent=2), encoding="utf-8")
        status = (
            "ok"
            if result["exit_code"] == 0
            else f"erro {result['exit_code']} {result['stderr_type']}"
        )
        print(f"{pid}: {status} em {result['wall_s']} s", flush=True)
    done = sum(1 for pid in manifest["pages"] if (MOTOR_OUT / f"{pid}.json").is_file())
    print(json.dumps({"pages": len(manifest["pages"]), "read": done}))
    return 0 if done == len(manifest["pages"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
