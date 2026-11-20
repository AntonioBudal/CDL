"""Prepara as páginas para a ferramenta de anotação. Roda no **ambiente do motor do produto**
(Pillow e OpenCV), só lendo o motor, a partir de ``document-intelligence/``::

    ..\\caderno-leitura-0.1\\motor\\.venv\\Scripts\\python.exe -m tools.anotar.prepare

Para cada foto em ``dataset/raw/exp-027/fotos/`` (qualquer nome):

1. calcula o SHA-256 e procura o ``pNN`` com esse hash em ``splits/pages-sha256.json`` do EXP-027
   (foto não registrada é ignorada: a ferramenta só anota páginas comprovadamente as mesmas);
2. grava a imagem de trabalho ``processed/anotacao/imagens/pNN.jpg``: orientada pelo EXIF, sem
   EXIF, reduzida só se o lado maior passar de 6000 px;
3. roda ``leitorum_motor read`` nessa imagem (caixas e texto iniciais, mesmos parâmetros do
   produto) e grava ``processed/anotacao/motor/pNN.json``;
4. atualiza o índice ``processed/anotacao/pages.json``.

Retomável: pula as páginas prontas, a não ser com ``--force``. Nada sai do computador; a saída
no terminal traz só contagens e ``pNN``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from .paths import MOTOR_CONFIG, MOTOR_DIR, MOTOR_PYTHON, Paths, default_paths

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
MAX_SIDE = 6000
JPEG_QUALITY = 95


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def work_image(source: Path, target: Path) -> dict:
    """Imagem de trabalho orientada; devolve largura, altura e fator em relação à foto orientada."""
    from PIL import Image, ImageOps

    try:  # HEIC, quando o plugin existir no ambiente
        from pillow_heif import register_heif_opener

        register_heif_opener()
    except ImportError:
        pass
    with Image.open(source) as image:
        oriented = ImageOps.exif_transpose(image).convert("RGB")
    width, height = oriented.size
    scale = min(1.0, MAX_SIDE / max(width, height))
    if scale < 1.0:
        oriented = oriented.resize(
            (round(width * scale), round(height * scale)), Image.Resampling.LANCZOS
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp.jpg")
    oriented.save(temporary, "JPEG", quality=JPEG_QUALITY)
    temporary.replace(target)
    return {"width": oriented.size[0], "height": oriented.size[1], "scale": round(scale, 6)}


def run_motor(image: Path, out: Path) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
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
        timeout=900,
        check=False,
    )
    error = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else ""
    return {
        "motor_ok": completed.returncode == 0 and out.is_file(),
        "motor_error": "" if completed.returncode == 0 else error.split(":")[0][:80],
        "motor_s": round(time.perf_counter() - started, 1),
    }


def prepare(paths: Paths, *, force: bool = False, motor: bool = True, only: set | None = None):
    registered = json.loads(paths.registered.read_text(encoding="utf-8"))["pages"]
    by_hash = {entry["sha256"]: pid for pid, entry in registered.items()}
    index_doc = (
        json.loads(paths.index.read_text(encoding="utf-8")) if paths.index.is_file() else {}
    )
    index = index_doc.get("pages", {})
    photos = (
        sorted(p for p in paths.photos.iterdir() if p.suffix.lower() in SUPPORTED)
        if paths.photos.is_dir()
        else []
    )
    report = {"photos": len(photos), "registered": 0, "unregistered": 0, "prepared": 0,
              "motor_failed": [], "duplicates": 0}
    seen: set[str] = set()
    for photo in photos:
        digest = sha256(photo)
        pid = by_hash.get(digest)
        if pid is None:
            report["unregistered"] += 1
            continue
        if pid in seen:
            report["duplicates"] += 1
            continue
        seen.add(pid)
        report["registered"] += 1
        if only and pid not in only:
            continue
        image = paths.images / f"{pid}.jpg"
        motor_out = paths.motor / f"{pid}.json"
        entry = index.get(pid, {})
        done = (
            entry.get("sha256") == digest
            and image.is_file()
            and (motor_out.is_file() or not motor)
        )
        if done and not force:
            continue
        info = work_image(photo, image)
        entry = {"sha256": digest, "work_sha256": sha256(image), **info, "motor_ok": False}
        if motor:
            entry.update(run_motor(image, motor_out))
            if not entry["motor_ok"]:
                report["motor_failed"].append(pid)
        entry["prepared_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        index[pid] = entry
        paths.index.parent.mkdir(parents=True, exist_ok=True)
        paths.index.write_text(
            json.dumps({"schema": "anotar-index/1", "pages": dict(sorted(index.items()))},
                       indent=2),
            encoding="utf-8",
        )
        report["prepared"] += 1
        print(f"{pid}: pronta" + ("" if entry["motor_ok"] or not motor else " (motor falhou)"),
              flush=True)
    report["missing"] = sorted(set(registered) - seen)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preparar páginas para a ferramenta de anotação")
    parser.add_argument("--force", action="store_true", help="refazer as páginas já prontas")
    parser.add_argument("--no-motor", action="store_true", help="só a imagem, sem caixas iniciais")
    parser.add_argument("--only", default="", help="pNN separados por vírgula")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    paths = default_paths()
    if not paths.registered.is_file():
        print(f"falta o registro de hashes: {paths.registered}")
        return 2
    only = {item.strip() for item in args.only.split(",") if item.strip()} or None
    report = prepare(paths, force=args.force, motor=not args.no_motor, only=only)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["registered"] and not report["motor_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
