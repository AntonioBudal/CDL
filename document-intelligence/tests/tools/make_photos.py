"""Gera "fotos" fictícias de caderno (pauta + rabiscos sem texto real) para testar a ferramenta.
Roda num ambiente com Pillow (o do motor): ``python -m tests.tools.make_photos <pasta> [n]``.
A página 2 sai deitada com EXIF de orientação 6, para conferir a rotação da imagem de trabalho."""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path


def make(folder: Path, count: int = 3) -> list[Path]:
    from PIL import Image, ImageDraw

    folder.mkdir(parents=True, exist_ok=True)
    out = []
    for number in range(1, count + 1):
        rng = random.Random(number)
        width, height = 1500, 2000
        image = Image.new("RGB", (width, height), (246, 243, 232))
        draw = ImageDraw.Draw(image)
        for y in range(160, height - 80, 90):
            draw.line([(60, y), (width - 60, y)], fill=(170, 195, 220), width=2)
        for row in range(rng.randint(8, 14)):
            base = 150 + row * 90 - 18
            x = 120 + rng.randint(0, 80)
            end = rng.randint(700, width - 120)
            while x < end:
                word = rng.randint(60, 180)
                points = [
                    (x + t, base + 14 * math.sin((x + t) / rng.uniform(6, 11)) + rng.uniform(-3, 3))
                    for t in range(0, word, 3)
                ]
                draw.line(points, fill=(35, 40, 90), width=4)
                x += word + rng.randint(25, 45)
        name = folder / f"IMG_{2000 + number}.jpg"
        if number == 2:
            image = image.rotate(90, expand=True)  # deitada; EXIF 6 manda girar de volta
            exif = Image.Exif()
            exif[0x0112] = 6
            image.save(name, "JPEG", quality=90, exif=exif)
        else:
            image.save(name, "JPEG", quality=90)
        out.append(name)
    return out


if __name__ == "__main__":
    target = Path(sys.argv[1])
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    for path in make(target, total):
        print(path.name)
