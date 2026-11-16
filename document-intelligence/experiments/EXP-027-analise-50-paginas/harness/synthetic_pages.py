"""Páginas fictícias para testar a cadeia do EXP-027 sem dados reais (fonte manuscrita das fixtures
do EXP-002, frases inventadas). Uso: ``python synthetic_pages.py <pasta_destino> [--pages 2]``.
Grava JPG com EXIF mínimo e a referência esperada ao lado (``pNN.expected.txt``)."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from paths import DI_ROOT
from PIL import Image, ImageDraw, ImageFont

FONT = DI_ROOT / "dataset" / "fixtures" / "exp-002" / "fonts" / "Caveat-Regular.ttf"
SENTENCES = [
    "Livro de Teste, capítulo um: a leitura atenta",
    "Resumo: o autor defende a releitura lenta",
    "Conceito: atenção é a moeda da leitura",
    "A fórmula $x^2 + y^2 = r^2$ aparece na margem",
    "Pergunta: como aplicar isso no estudo diário?",
    "Referência: página 42 da edição fictícia",
    "Observação: reler o parágrafo três amanhã",
    "Exemplo: o círculo de raio $r = 2$",
]


def render(path: Path, seed: int) -> list[str]:
    rng = random.Random(seed)
    lines = rng.sample(SENTENCES, k=6)
    image = Image.new("RGB", (1600, 2200), (246, 243, 235))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(FONT), 64)
    y = 180
    for text in lines:
        visible = text.replace("$", "")
        draw.text((140 + rng.randint(-10, 10), y), visible, font=font, fill=(30, 30, 60))
        y += 150 + rng.randint(-10, 10)
    image = image.rotate(rng.uniform(-1.5, 1.5), resample=Image.BICUBIC, fillcolor=(246, 243, 235))
    image.save(path, "JPEG", quality=90)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    parser.add_argument("--pages", type=int, default=2)
    args = parser.parse_args(argv)
    destination = Path(args.destination)
    destination.mkdir(parents=True, exist_ok=True)
    for index in range(1, args.pages + 1):
        lines = render(destination / f"IMG_{index:04d}.jpg", seed=index)
        (destination / f"p{index:02d}.expected.txt").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    print(f"{args.pages} páginas fictícias em {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
