"""EXP-043 — amostra de linhas sintéticas: texto em domínio público (Machado de Assis, *Dom
Casmurro*, pela API do Wikisource em português) desenhado com as fontes manuscritas OFL do
projeto, com variação de tamanho, inclinação, tinta e fundo. Mede velocidade de geração e
tamanho; a fonte é ilimitada e, no treino, é gerada na hora (não ocupa disco).

Uso: ``python sample_synthetic.py [--lines 200] [--fonts <pasta>]``
"""

from __future__ import annotations

import argparse
import html
import io
import json
import os
import random
import re
import sys
import time
import urllib.parse
from pathlib import Path

import common

WIKISOURCE = "https://pt.wikisource.org/w/api.php"
WORK = "Dom_Casmurro"
FONTS = Path(
    os.environ.get("EXP043_FONTS")
    or "C:/Users/User/caderno/document-intelligence/dataset/fixtures/exp-002/fonts"
)


def chapter_text(number: str) -> tuple[str, str]:
    params = {
        "action": "parse",
        "page": f"{WORK}/{number}",
        "prop": "text",
        "format": "json",
        "formatversion": 2,
    }
    url = f"{WIKISOURCE}?{urllib.parse.urlencode(params)}"
    data = common.fetch_json(url)
    text = re.sub(r"<[^>]+>", " ", data["parse"]["text"])
    text = html.unescape(re.sub(r"\s+", " ", text))
    text = re.sub(r"\[\s*editar\s*\]|←.*?→", " ", text)
    return " ".join(text.split()), url


def lines_from(text: str, rng: random.Random, count: int) -> list[str]:
    words = text.split()
    out = []
    while len(out) < count and len(words) > 12:
        start = rng.randrange(0, len(words) - 12)
        out.append(" ".join(words[start : start + rng.randint(4, 10)]))
    return out


def render(text: str, font_path: Path, rng: random.Random) -> bytes:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    size = rng.randint(34, 56)
    font = ImageFont.truetype(str(font_path), size)
    left, top, right, bottom = font.getbbox(text)
    width, height = right - left + 40, bottom - top + 30
    paper = rng.randint(225, 250)
    image = Image.new("L", (width, height), paper)
    draw = ImageDraw.Draw(image)
    ink = rng.randint(10, 80)
    draw.text((20 - left, 15 - top), text, font=font, fill=ink)
    image = image.rotate(
        rng.uniform(-2.5, 2.5), resample=Image.Resampling.BICUBIC, expand=True, fillcolor=paper
    )
    if rng.random() < 0.5:
        image = image.filter(ImageFilter.GaussianBlur(rng.uniform(0.3, 0.9)))
    out = io.BytesIO()
    image.save(out, "PNG")
    return out.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=200)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    rng = random.Random("exp-043-sintetico")
    fonts = sorted(p for p in FONTS.glob("*.ttf"))
    texts, urls = [], []
    for number in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII"):
        try:
            text, url = chapter_text(number)
        except Exception:  # noqa: BLE001 — capítulo ausente: segue
            continue
        texts.append(text)
        urls.append(url)
    corpus = " ".join(texts)
    sentences = lines_from(corpus, rng, args.lines)
    started = time.perf_counter()
    stats = {
        "lines": 0,
        "bytes_original": 0,
        "bytes_ours": 0,
        "bytes_ours_lossy": 0,
        "chars": 0,
        "pt_accents": 0,
    }
    for text in sentences:
        font = rng.choice(fonts)
        data = render(text, font, rng)
        path = common.store("sintetico", data, ".png")
        measures = common.line_measures(data, text)
        common.record(
            "sintetico",
            {
                "source": "sintético (Dom Casmurro, Wikisource pt) + fontes OFL",
                "source_url": urls[0] if urls else None,
                "file": path.name,
                "sha256": path.stem,
                "license": "texto em domínio público; fonte OFL-1.1",
                "status": "APPROVED",
                "language": "por",
                "era": "texto de 1899; letra simulada",
                "transcription": "line",
                "font": font.name,
                "text": text,
                **measures,
            },
        )
        stats["lines"] += 1
        for key in ("bytes_original", "bytes_ours", "bytes_ours_lossy", "chars", "pt_accents"):
            stats[key] += measures[key]
    stats["seconds_per_line"] = round((time.perf_counter() - started) / max(1, stats["lines"]), 4)
    stats["corpus_chars"] = len(corpus)
    stats["chapters"] = len(texts)
    stats["fonts"] = [f.name for f in fonts]
    (common.ROOT / "resumo-sintetico.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), "utf-8"
    )
    print(
        json.dumps(
            {k: stats[k] for k in ("lines", "seconds_per_line", "chapters")}, ensure_ascii=False
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
