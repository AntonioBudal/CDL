"""Gera e congela os conjuntos de páginas sintéticas do EXP-002 (dev, test, large).

Uso: ``python generate.py [--sets dev test large]`` — imagens em ``dataset/processed/exp-002/``
(fora do Git, regeneráveis) e manifestos em ``dataset/fixtures/exp-002/``.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import cv2
import numpy as np
import PIL
from pages.degrade import box_polygon, degrade, transform_polygon
from pages.render import PAGE_HEIGHT, PAGE_WIDTH, render_page
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = ROOT / "dataset" / "fixtures" / "exp-002" / "fonts"
IMAGES_DIR = ROOT / "dataset" / "processed" / "exp-002"
MANIFESTS_DIR = ROOT / "dataset" / "fixtures" / "exp-002"
SCHEMA = "leitorum-di-pages/1"

# conjunto → lista de (nível, quantidade, seed inicial, fator de escala)
SETS = {
    "dev": [("clean", 10, 10_000, 1.0), ("light", 10, 11_000, 1.0), ("strong", 10, 12_000, 1.0)],
    "test": [("clean", 60, 20_000, 1.0), ("light", 60, 21_000, 1.0), ("strong", 60, 22_000, 1.0)],
    "large": [("light", 10, 30_000, 2.3)],
}


def fonts() -> list[Path]:
    return sorted(FONTS_DIR.glob("*.ttf"))


def _scale_image(data: bytes, extension: str, factor: float) -> tuple[bytes, tuple[int, int]]:
    image = Image.open(io.BytesIO(data)).convert("RGB")
    size = (round(image.width * factor), round(image.height * factor))
    resized = cv2.resize(np.asarray(image), size, interpolation=cv2.INTER_CUBIC)
    buffer = io.BytesIO()
    if extension == ".jpg":
        Image.fromarray(resized).save(buffer, format="JPEG", quality=90)
    else:
        Image.fromarray(resized).save(buffer, format="PNG")
    return buffer.getvalue(), size


def _scale(values, factor: float):
    return [[round(x * factor), round(y * factor)] for x, y in values]


def build_page(page_id: str, level: str, seed: int, factor: float, images_dir: Path, root: Path):
    page, truth = render_page(seed, fonts())
    result = degrade(page, level, seed)
    transform = result.transform
    data, size = result.image_bytes, result.size
    if factor != 1.0:
        data, size = _scale_image(data, result.extension, factor)

    def geometry(polygon):
        bbox, poly = transform_polygon(polygon, transform)
        if factor != 1.0:
            bbox = [round(v * factor) for v in bbox]
            poly = _scale(poly, factor)
        return bbox, poly

    lines = []
    for line in truth.lines:
        bbox, poly = geometry(line.polygon)
        lines.append(
            {
                "id": line.id,
                "block_id": line.block_id,
                "text": line.text,
                "bbox": bbox,
                "polygon": poly,
            }
        )
    line_boxes = {line["id"]: line["bbox"] for line in lines}
    blocks = []
    for block in truth.blocks:
        if block.line_ids:
            # União das linhas já transformadas: mais justa que transformar o retângulo do bloco.
            members = [line_boxes[i] for i in block.line_ids]
            bbox = [
                min(b[0] for b in members),
                min(b[1] for b in members),
                max(b[2] for b in members),
                max(b[3] for b in members),
            ]
        else:
            bbox, _ = geometry(box_polygon(block.bbox))
        blocks.append(
            {"id": block.id, "type": block.type, "bbox": bbox, "line_ids": block.line_ids}
        )
    ignore = [geometry(box_polygon(region))[0] for region in truth.ignore]
    corners = [[0, 0], [PAGE_WIDTH, 0], [PAGE_WIDTH, PAGE_HEIGHT], [0, PAGE_HEIGHT]]
    if transform is not None:
        corners = [
            [round(float(x), 1), round(float(y), 1)] for x, y in transform.apply_points(corners)
        ]
    if factor != 1.0:
        corners = [[round(x * factor, 1), round(y * factor, 1)] for x, y in corners]

    path = images_dir / f"{page_id}{result.extension}"
    path.write_bytes(data)
    return {
        "id": page_id,
        "image": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": size[0],
        "height": size[1],
        "level": level,
        "seed": seed,
        "scale": factor,
        "font": truth.font,
        "page_corners": corners,
        "lines": lines,
        "blocks": blocks,
        "ignore": ignore,
        "degradation": result.params,
    }


def generate_set(
    name: str,
    images_dir: Path = IMAGES_DIR,
    manifests_dir: Path = MANIFESTS_DIR,
    root: Path = ROOT,
    plan=None,
) -> dict:
    target = images_dir / name
    target.mkdir(parents=True, exist_ok=True)
    pages = []
    for level, count, first_seed, factor in plan or SETS[name]:
        for index in range(count):
            page_id = f"{name}-{level}-{index + 1:03d}"
            pages.append(build_page(page_id, level, first_seed + index, factor, target, root))
    manifest = {
        "schema": SCHEMA,
        "dataset": f"exp-002-{name}",
        "origin": "synthetic",
        "note": "Páginas sintéticas com geometria conhecida; texto fictício. Não são fotos reais.",
        "renderer": {"pillow": PIL.__version__, "opencv": cv2.__version__, "numpy": np.__version__},
        "fonts": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in fonts()},
        "pages": pages,
    }
    manifests_dir.mkdir(parents=True, exist_ok=True)
    (manifests_dir / f"{name}-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera as páginas sintéticas do EXP-002")
    parser.add_argument("--sets", nargs="+", default=list(SETS), choices=list(SETS))
    args = parser.parse_args(argv)
    for name in args.sets:
        manifest = generate_set(name)
        lines = sum(len(p["lines"]) for p in manifest["pages"])
        print(f"{name}: {len(manifest['pages'])} páginas, {lines} linhas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
