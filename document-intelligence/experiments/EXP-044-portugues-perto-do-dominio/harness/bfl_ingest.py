"""EXP-044 — alinha a carta da BFL às linhas detectadas (``bfl_detect.py``), filtra, recorta
e ingere as linhas aceitas no catálogo (fonte ``ufpr-bfl``, ``EXPERIMENT_ONLY``). Ambiente do
subprojeto.

Uso:
    python bfl_ingest.py --conferir   # alinha, grava estatísticas e 50 linhas p/ conferência
    python bfl_ingest.py              # ingere as aceitas
"""

from __future__ import annotations

import argparse
import io
import json
import random
import sys
from collections import Counter
from pathlib import Path

import align
from PIL import Image

from tools.catalogo import Catalog

BFL = Path("D:/Leitorum-DI/trabalho/exp-044/bfl")
SOURCE = "ufpr-bfl"
PAD = 6  # pixels de folga em volta da caixa detectada


def bucket(value: float) -> str:
    return f"{min(int(value * 10), 10) / 10:.1f}"


def aligned_pages(letter: str):
    for path in sorted((BFL / "deteccao").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        hyps = [ln["text"] for ln in doc["lines"]]
        parts = align.align_detail(letter, hyps) if hyps else []
        yield doc, hyps, parts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--conferir", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    letter = (BFL / "carta.txt").read_text(encoding="utf-8")  # fora do Git (dado da BFL)
    stats = Counter()
    cer_kept, cer_dropped = Counter(), Counter()
    accepted = []
    for doc, hyps, parts in aligned_pages(letter):
        stats["paginas"] += 1
        if not align.page_ok(len(hyps)):
            stats["paginas_fora"] += 1
            stats["linhas_pagina_fora"] += len(hyps)
            continue
        for number, (line, hyp, (ref, split)) in enumerate(
            zip(doc["lines"], hyps, parts, strict=True)
        ):
            stats["linhas"] += 1
            if split:  # palavra partida no fim/início da linha: o rótulo não bate com a imagem
                stats["palavra_partida"] += 1
                continue
            value = align.cer(hyp.lower(), ref.lower()) if ref else 1.0
            if align.accept(hyp, ref):
                cer_kept[bucket(value)] += 1
                accepted.append(
                    {
                        "page": doc["page"],
                        "image": doc["image"],
                        "line": number,
                        "bbox": line["bbox"],
                        "hyp": hyp,
                        "text": align.label(hyp, ref),
                        "cer": round(value, 3),
                    }
                )
            else:
                cer_dropped[bucket(value)] += 1
    stats["aceitas"] = len(accepted)
    writers = Counter(a["page"].split("_")[0] for a in accepted)
    summary = {
        "contagem": dict(stats),
        "pessoas_com_linhas": len(writers),
        "linhas_por_pessoa_min_med_max": [
            min(writers.values(), default=0),
            sorted(writers.values())[len(writers) // 2] if writers else 0,
            max(writers.values(), default=0),
        ],
        "cer_aceitas": dict(sorted(cer_kept.items())),
        "cer_descartadas": dict(sorted(cer_dropped.items())),
        "maiusculas": sum(1 for a in accepted if a["text"].isupper()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    (BFL / "alinhamento.json").write_text(json.dumps(summary, indent=1), "utf-8")
    if args.conferir:
        sample = random.Random("exp-044-bfl-conferencia").sample(accepted, min(50, len(accepted)))
        folder = BFL / "conferencia"
        folder.mkdir(exist_ok=True)
        for k, item in enumerate(sample):
            with Image.open(item["image"]) as image:
                x0, y0, x1, y1 = item["bbox"]
                image.crop((max(0, x0 - PAD), max(0, y0 - PAD), x1 + PAD, y1 + PAD)).save(
                    folder / f"{k:02d}.png"
                )
        (folder / "rotulos.json").write_text(
            json.dumps(
                [{"n": k, "text": s["text"], "page": s["page"]} for k, s in enumerate(sample)],
                ensure_ascii=False,
                indent=1,
            ),
            "utf-8",
        )
        return 0
    cat = Catalog()
    added = 0
    page_path, image = None, None
    try:
        for k, item in enumerate(accepted, 1):
            if item["image"] != page_path:  # as aceitas vêm agrupadas por página
                page_path = item["image"]
                with Image.open(page_path) as opened:
                    image = opened.copy()
            x0, y0, x1, y1 = item["bbox"]
            crop = image.crop((max(0, x0 - PAD), max(0, y0 - PAD), x1 + PAD, y1 + PAD))
            out = io.BytesIO()
            crop.save(out, "PNG")
            result = cat.ingest_line(
                SOURCE,
                f"{item['page']}#{item['line']}",
                image=out.getvalue(),
                text=item["text"],
                url=f"https://www.inf.ufpr.br/lesoliveira/download/BFL_Database.zip#{item['page']}",
                script="manuscript",
                split="train",
                language="pt",
                writer=item["page"].split("_")[0],
                acquired_via="exp-044",
                extra={"alinhamento_cer": item["cer"]},
            )
            added += result.created
            if k % 500 == 0:
                cat.flush()
                print(f"{k}/{len(accepted)} linhas", flush=True)
    finally:
        cat.flush()
        cat.close()
    print(f"ingeridas: {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
