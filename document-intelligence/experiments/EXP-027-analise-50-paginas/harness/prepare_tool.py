"""T003a — prepara a ferramenta local de transcrição: cópia reduzida de cada página, recortes das
linhas lidas pelo motor e medidas automáticas de qualidade da foto (desfoque, brilho, contraste).
Roda no ambiente do motor (OpenCV). Tudo fora do Git, em ``processed/exp-027/transcrever``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from paths import MANIFEST, MOTOR_OUT, PHOTOS, PROCESSED, TOOL

MAX_SIDE = 1800  # px da cópia para o navegador
CONVERTED = PROCESSED / "fotos-png"


def load(path: Path, pid: str) -> np.ndarray:
    if path.suffix.lower() in {".heic", ".heif"}:
        path = CONVERTED / f"{pid}.png"
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(pid)
    return image


def quality(image: np.ndarray) -> dict:
    """Medidas simples numa versão a 1000 px de largura: variância do Laplaciano (desfoque),
    brilho médio, desvio (contraste) e assimetria esquerda/direita do brilho (sombra)."""
    h, w = image.shape[:2]
    scale = 1000 / w
    small = cv2.resize(image, (1000, max(1, round(h * scale))), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    left, right = gray[:, : gray.shape[1] // 2], gray[:, gray.shape[1] // 2 :]
    top, bottom = gray[: gray.shape[0] // 2], gray[gray.shape[0] // 2 :]
    return {
        "laplacian_var": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 1),
        "brightness_mean": round(float(gray.mean()), 1),
        "brightness_std": round(float(gray.std()), 1),
        "shade_lr": round(abs(float(left.mean()) - float(right.mean())), 1),
        "shade_tb": round(abs(float(top.mean()) - float(bottom.mean())), 1),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preparar a ferramenta de transcrição")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    (TOOL / "pages").mkdir(parents=True, exist_ok=True)
    (TOOL / "crops").mkdir(parents=True, exist_ok=True)
    quality_path = PROCESSED / "quality.json"
    measures = (
        json.loads(quality_path.read_text(encoding="utf-8")) if quality_path.is_file() else {}
    )
    for pid, page in manifest["pages"].items():
        target = TOOL / "pages" / f"{pid}.jpg"
        motor_file = MOTOR_OUT / f"{pid}.json"
        if target.is_file() and pid in measures and not args.force:
            continue
        image = load(PHOTOS / page["file"], pid)
        h, w = image.shape[:2]
        factor = min(1.0, MAX_SIDE / max(h, w))
        reduced = (
            cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.INTER_AREA)
            if factor < 1
            else image
        )
        cv2.imwrite(str(target), reduced, [cv2.IMWRITE_JPEG_QUALITY, 85])
        measures[pid] = {**quality(image), "display_factor": round(factor, 4)}
        if motor_file.is_file():
            crops_dir = TOOL / "crops" / pid
            crops_dir.mkdir(exist_ok=True)
            lines = json.loads(motor_file.read_text(encoding="utf-8"))["lines"]
            for index, line in enumerate(lines):
                x0, y0, x1, y1 = line["bbox"]
                pad = max(2, (y1 - y0) // 6)
                crop = image[
                    max(0, y0 - pad) : min(h, y1 + pad), max(0, x0 - pad) : min(w, x1 + pad)
                ]
                if crop.size:
                    ch, cw = crop.shape[:2]
                    if ch > 96:
                        crop = cv2.resize(
                            crop, (round(cw * 96 / ch), 96), interpolation=cv2.INTER_AREA
                        )
                    cv2.imwrite(
                        str(crops_dir / f"{index:03d}.jpg"), crop, [cv2.IMWRITE_JPEG_QUALITY, 85]
                    )
            measures[pid]["motor_lines"] = len(lines)
        quality_path.write_text(json.dumps(measures, indent=2), encoding="utf-8")
        print(pid, flush=True)
    print(json.dumps({"pages": len(measures)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
