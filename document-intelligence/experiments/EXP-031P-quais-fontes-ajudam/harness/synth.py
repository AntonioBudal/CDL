"""EXP-031P — linhas sintéticas em português com aumentos fortes (o EXP-043 mostrou que, sem eles, o
leitor já lê o sintético com 8,7 % de erro: fácil demais para ensinar algo).

Texto: obras em domínio público da Wikisource em português (cache local com a lista de páginas
usadas). Fontes: as manuscritas OFL do projeto. Aumentos: tamanho, traço mais grosso, inclinação,
cisalhamento, ondulação da linha de base, pauta, fundo com ruído e gradiente, desfoque, perda de
resolução e compressão JPEG. Determinístico pela semente.

Uso: ``python synth.py --lines 8000 --out D:/Leitorum-DI/trabalho/exp-031p/sintetico``
"""

from __future__ import annotations

import argparse
import html
import io
import json
import math
import random
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

UA = "LeitorumDI-sampler/0.1 (non-commercial research; local handwriting recognition)"
WIKISOURCE = "https://pt.wikisource.org/w/api.php"


# Obras em domínio público (autores mortos há mais de 70 anos), capítulos na Wikisource em
# português.
def roman(n: int) -> str:
    out = ""
    numerals = ((50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))
    for value, numeral in numerals:
        while n >= value:
            out += numeral
            n -= value
    return out


# 60 capítulos de Dom Casmurro (1899): texto variado o bastante para 8 mil linhas.
PAGES = [f"Dom_Casmurro/{roman(n)}" for n in range(1, 61)]
FONTS = Path("C:/Users/User/caderno/document-intelligence/dataset/fixtures/exp-002/fonts")


def fetch_corpus(cache: Path) -> tuple[str, list[str]]:
    if cache.is_file():
        data = json.loads(cache.read_text(encoding="utf-8"))
        return data["text"], data["pages"]
    texts, used = [], []
    for page in PAGES:
        params = {
            "action": "parse",
            "page": page,
            "prop": "text",
            "format": "json",
            "formatversion": 2,
        }
        url = f"{WIKISOURCE}?{urllib.parse.urlencode(params)}"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA})
            data = json.load(urllib.request.urlopen(request, timeout=60))
        except Exception:  # noqa: BLE001 — página ausente: segue
            continue
        if "parse" not in data:
            continue
        text = re.sub(r"<[^>]+>", " ", data["parse"]["text"])
        text = html.unescape(re.sub(r"\s+", " ", text))
        texts.append(" ".join(text.split()))
        used.append(url)
    corpus = " ".join(texts)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"text": corpus, "pages": used}, ensure_ascii=False), "utf-8")
    return corpus, used


def sentences(corpus: str, count: int, rng: random.Random) -> list[str]:
    words = corpus.split()
    out = []
    while len(out) < count:
        start = rng.randrange(0, max(1, len(words) - 12))
        out.append(" ".join(words[start : start + rng.randint(3, 10)]))
    return out


def wave(image: Image.Image, rng: random.Random, paper: int) -> Image.Image:
    """Ondula a linha de base: desloca cada faixa vertical por uma senoide."""
    amplitude = rng.uniform(0, 4)
    period = rng.uniform(80, 300)
    phase = rng.uniform(0, 2 * math.pi)
    out = Image.new("L", image.size, paper)
    step = 4
    for x in range(0, image.width, step):
        dy = round(amplitude * math.sin(2 * math.pi * x / period + phase))
        out.paste(image.crop((x, 0, x + step, image.height)), (x, dy))
    return out


def render(text: str, font_path: Path, rng: random.Random) -> Image.Image:
    font = ImageFont.truetype(str(font_path), rng.randint(28, 64))
    left, top, right, bottom = font.getbbox(text)
    pad = 24
    width, height = right - left + 2 * pad, bottom - top + 2 * pad
    paper = rng.randint(185, 250)
    image = Image.new("L", (width, height), paper)
    draw = ImageDraw.Draw(image)
    if rng.random() < 0.5:  # pauta
        y = pad + (bottom - top) + rng.randint(-4, 6)
        draw.line([(0, y), (width, y)], fill=paper - rng.randint(30, 70), width=rng.randint(1, 2))
    ink = rng.randint(0, 110)
    stroke = rng.choice([0, 0, 0, 1, 1, 2])
    draw.text(
        (pad - left, pad - top), text, font=font, fill=ink, stroke_width=stroke, stroke_fill=ink
    )
    shear = rng.uniform(-0.35, 0.35)
    image = image.transform(
        image.size,
        Image.Transform.AFFINE,
        (1, shear, -shear * height / 2, 0, 1, 0),
        resample=Image.Resampling.BICUBIC,
        fillcolor=paper,
    )
    image = wave(image, rng, paper)
    image = image.rotate(
        rng.uniform(-4, 4), resample=Image.Resampling.BICUBIC, expand=True, fillcolor=paper
    )
    # ruído determinístico (``Image.effect_noise`` usa o gerador global e quebraria a semente)
    noise = Image.frombytes("L", image.size, rng.randbytes(image.width * image.height))
    image = Image.blend(image, noise, rng.uniform(0.0, 0.15))
    if rng.random() < 0.6:
        image = image.filter(ImageFilter.GaussianBlur(rng.uniform(0.3, 1.4)))
    if rng.random() < 0.5:  # perda de resolução
        factor = rng.uniform(0.35, 0.8)
        small = image.resize(
            (max(8, int(image.width * factor)), max(8, int(image.height * factor)))
        )
        image = small.resize(image.size)
    if rng.random() < 0.6:  # compressão JPEG
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=rng.randint(25, 85))
        image = Image.open(io.BytesIO(buffer.getvalue())).convert("L")
    return image


def generate(lines: int, out: Path, seed: str, corpus: str) -> list[dict]:
    rng = random.Random(seed)
    fonts = sorted(FONTS.glob("*.ttf"))
    out.mkdir(parents=True, exist_ok=True)
    items = []
    for index, text in enumerate(sentences(corpus, lines, rng)):
        font = fonts[index % len(fonts)] if index < len(fonts) else rng.choice(fonts)
        image = render(text, font, rng)
        path = out / f"s{index:05d}.png"
        image.save(path, "PNG")
        items.append(
            {"id": f"sintetico:{index:05d}", "image": str(path), "text": text, "font": font.name}
        )
    return items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=8000)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", default="exp-031p-sintetico")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(args.out)
    corpus, pages = fetch_corpus(out.parent / "corpus-dominio-publico.json")
    items = generate(args.lines, out, args.seed, corpus)
    (out.parent / "sintetico.json").write_text(
        json.dumps(
            {
                "seed": args.seed,
                "pages": pages,
                "fonts": sorted({i["font"] for i in items}),
                "items": items,
            },
            ensure_ascii=False,
        ),
        "utf-8",
    )
    print(json.dumps({"lines": len(items), "corpus_chars": len(corpus), "pages": len(pages)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
