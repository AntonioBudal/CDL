"""Gerador de linhas sintéticas (frase → imagem) e do manifesto de linhas do EXP-001.

Uso: ``python synth.py`` — lê ``dataset/fixtures/exp-001/sentences.json``, grava as imagens em
``dataset/processed/exp-001/synthetic/`` (fora do Git) e o manifesto em
``dataset/fixtures/exp-001/synthetic-manifest.json``.

A camada sintética valida o harness e mede custo; não vale como métrica de HTR real.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

import PIL
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "dataset" / "fixtures" / "exp-001"
DEFAULT_FONT = FIXTURES / "fonts" / "Caveat-Regular.ttf"
DEFAULT_SENTENCES = FIXTURES / "sentences.json"
DEFAULT_MANIFEST = FIXTURES / "synthetic-manifest.json"
DEFAULT_IMAGES = ROOT / "dataset" / "processed" / "exp-001" / "synthetic"
SCHEMA = "leitorum-di-lines/1"
FONT_SIZE = 48
PADDING = 12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def missing_glyphs(text: str, font_path: Path) -> list[str]:
    """Caracteres de ``text`` (exceto espaço) sem glifo na fonte."""
    cmap = TTFont(str(font_path)).getBestCmap()
    return sorted({ch for ch in text if ch != " " and ord(ch) not in cmap})


def render_line(text: str, font: ImageFont.FreeTypeFont) -> Image.Image:
    """Renderiza uma linha em tons de cinza: tinta preta sobre fundo branco."""
    left, top, right, bottom = font.getbbox(text)
    ascent, descent = font.getmetrics()
    width = (right - left) + 2 * PADDING
    height = max(ascent + descent, bottom - top) + 2 * PADDING
    image = Image.new("L", (width, height), color=255)
    ImageDraw.Draw(image).text((PADDING - left, PADDING), text, font=font, fill=0)
    return image


def generate(
    sentences_path: Path = DEFAULT_SENTENCES,
    font_path: Path = DEFAULT_FONT,
    images_dir: Path = DEFAULT_IMAGES,
    manifest_path: Path = DEFAULT_MANIFEST,
    root: Path = ROOT,
) -> dict[str, object]:
    """Gera uma imagem por frase e grava o manifesto; devolve o manifesto."""
    sentences = json.loads(Path(sentences_path).read_text(encoding="utf-8"))["sentences"]
    all_text = "".join(item["text"] for item in sentences)
    missing = missing_glyphs(all_text, font_path)
    if missing:
        raise ValueError(f"A fonte não tem glifo para: {missing}")

    font = ImageFont.truetype(str(font_path), FONT_SIZE)
    images_dir = Path(images_dir)
    images_dir.mkdir(parents=True, exist_ok=True)

    lines = []
    for item in sentences:
        text = unicodedata.normalize("NFC", item["text"])
        image = render_line(text, font)
        image_path = images_dir / f"{item['id']}.png"
        image.save(image_path, format="PNG")
        lines.append(
            {
                "id": item["id"],
                "image": image_path.relative_to(root).as_posix(),
                "sha256": sha256_file(image_path),
                "text": text,
                "width": image.width,
                "height": image.height,
                "origin": "synthetic",
            }
        )

    manifest = {
        "schema": SCHEMA,
        "dataset": "exp-001-synthetic",
        "origin": "synthetic",
        "note": "Linhas sintéticas: validam o harness e o custo; não são métrica de HTR real.",
        "sentences_sha256": sha256_file(Path(sentences_path)),
        "font": {
            "file": Path(font_path).name,
            "sha256": sha256_file(Path(font_path)),
            "size": FONT_SIZE,
            "license": "OFL-1.1",
        },
        "renderer": {"pillow": PIL.__version__, "padding": PADDING, "mode": "L"},
        "lines": lines,
    }
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera as linhas sintéticas do EXP-001")
    parser.add_argument("--sentences", default=str(DEFAULT_SENTENCES))
    parser.add_argument("--font", default=str(DEFAULT_FONT))
    parser.add_argument("--images", default=str(DEFAULT_IMAGES))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    args = parser.parse_args(argv)
    manifest = generate(
        Path(args.sentences), Path(args.font), Path(args.images), Path(args.manifest)
    )
    print(f"{len(manifest['lines'])} linhas geradas; manifesto em {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
