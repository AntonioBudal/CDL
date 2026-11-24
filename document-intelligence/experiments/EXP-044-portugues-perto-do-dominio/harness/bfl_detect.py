"""EXP-044 — detecta e lê as linhas das páginas da BFL com o pipeline do produto (ADR-008), sem
alterar nada no motor. Roda no **ambiente do motor**. Retomável: páginas já lidas são puladas.

Uso: ``python bfl_detect.py [--limit N]``
Saída: ``D:/Leitorum-DI/trabalho/exp-044/bfl/deteccao/<página>.json`` (caixas, texto, confiança).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

MOTOR_DIR = Path("C:/Users/User/caderno/caderno-leitura-0.1/motor")
BFL = Path("D:/Leitorum-DI/trabalho/exp-044/bfl")
IMAGE_EXT = {".png", ".bmp", ".tif", ".tiff", ".jpg", ".jpeg"}


def page_images(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.suffix.lower() in IMAGE_EXT)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(MOTOR_DIR))
    from leitorum_motor import pipeline as pipeline_module

    pipeline = pipeline_module.PagePipeline(pipeline_module.load_config(MOTOR_DIR / "config.json"))
    out = BFL / "deteccao"
    out.mkdir(parents=True, exist_ok=True)
    images = page_images(BFL / "paginas")
    if args.limit:
        images = images[: args.limit]
    started, done = time.monotonic(), 0
    for path in images:
        target = out / f"{path.stem}.json"
        if target.is_file():
            continue
        result = pipeline.read(path)
        target.write_text(
            json.dumps(
                {
                    "page": path.stem,
                    "image": str(path),
                    "size": result["image"],
                    "page_scale": result["page_scale"],
                    "lines": result["lines"],
                },
                ensure_ascii=False,
            ),
            "utf-8",
        )
        done += 1
        if done % 25 == 0:
            minutes = (time.monotonic() - started) / 60
            print(f"{done} páginas ({minutes:.1f} min)", flush=True)
    print(f"fim: {done} páginas novas, {len(images)} no total", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
