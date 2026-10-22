"""Lê um conjunto de linhas com o reconhecedor PyTorch (original ou ajustado) e grava as predições.

Uso (ambiente ``envs/ft``): ``python experiments/EXP-014/harness/predict.py --set val --limit 600``
``[--checkpoint models/exp-014/best.pt] --out dataset/processed/exp-014/pred-<nome>.json``.
As predições ficam fora do Git; as métricas são calculadas no ambiente do harness (``score.py``).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import torch
from model import batch, decode, load, preprocess

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-014"


def predict(
    model, characters, items: list[dict], batch_size: int = 1, extra: int = 640
) -> dict[str, str]:
    model.eval()
    order = sorted(
        range(len(items)),
        key=lambda i: cv2.imread(str(ROOT / items[i]["image"])).shape[1],
    )
    out = {}
    with torch.no_grad():
        for start in range(0, len(order), batch_size):
            chunk = [items[i] for i in order[start : start + batch_size]]
            images = [
                preprocess(cv2.imread(str(ROOT / it["image"]), cv2.IMREAD_COLOR), extra)
                for it in chunk
            ]
            texts = decode(model(batch(images)), characters)
            out.update({it["id"]: text for it, text in zip(chunk, texts, strict=True)})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Predição do reconhecedor (EXP-014)")
    parser.add_argument("--set", required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--extra", type=int, default=640)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    torch.set_num_threads(4)
    model, characters = load()
    if args.checkpoint:
        model.load_state_dict(torch.load(ROOT / args.checkpoint, map_location="cpu"))
    items = json.loads((DATA / f"{args.set}.json").read_text(encoding="utf-8"))
    if args.limit:
        items = items[: args.limit]
    started = time.perf_counter()
    predictions = predict(model, characters, items, args.batch, args.extra)
    elapsed = time.perf_counter() - started
    Path(ROOT / args.out).write_text(
        json.dumps({"set": args.set, "checkpoint": args.checkpoint, "items": predictions,
                    "ms_per_line": elapsed * 1000 / max(1, len(items))}, ensure_ascii=False),
        encoding="utf-8",
    )  # fmt: skip
    print(
        f"{args.set}: {len(items)} linhas, {elapsed * 1000 / max(1, len(items)):.0f} ms por linha"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
