"""EXP-022, T001: sorteia 15 páginas de teste do BRESSAY e monta um PDF A4 para imprimir.

Cada página é ampliada 4× (Lanczos) e centralizada numa folha A4 a 300 dpi, sem rótulo. Saída
fora do Git: ``dataset/processed/exp-022/imprimir.pdf`` e ``paginas.json`` (ids na ordem do PDF).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "dataset" / "processed" / "exp-017"
OUT = ROOT / "dataset" / "processed" / "exp-022"
PAGES = 15
SEED = "exp-022"
UPSCALE = 4
DPI = 300
A4 = (2480, 3508)  # 210 × 297 mm a 300 dpi
MARGIN = 150  # 12,7 mm


def pick(ids: list[str], count: int, seed: str) -> list[str]:
    """Sorteio estável: mesma lista ordenada, mesma semente, mesmas páginas."""
    return random.Random(seed).sample(sorted(ids), count)


def sheet(image: Image.Image) -> Image.Image:
    """Página ampliada e centralizada numa folha A4 branca, sem passar das margens."""
    big = image.resize((image.width * UPSCALE, image.height * UPSCALE), Image.Resampling.LANCZOS)
    room = (A4[0] - 2 * MARGIN, A4[1] - 2 * MARGIN)
    if big.width > room[0] or big.height > room[1]:
        big.thumbnail(room, Image.Resampling.LANCZOS)
    page = Image.new("RGB", A4, "white")
    page.paste(big, ((A4[0] - big.width) // 2, MARGIN))
    return page


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    pages = json.loads((SOURCE / "test-bressay-worker.json").read_text(encoding="utf-8"))["pages"]
    by_id = {page["id"]: page for page in pages}
    chosen = pick(list(by_id), PAGES, SEED)
    sheets = [sheet(Image.open(ROOT / by_id[i]["image"]).convert("RGB")) for i in chosen]
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = OUT / "imprimir.pdf"
    sheets[0].save(pdf, save_all=True, append_images=sheets[1:], resolution=DPI)
    (OUT / "paginas.json").write_text(
        json.dumps({"seed": SEED, "pages": chosen}, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"{len(chosen)} páginas → {pdf.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
