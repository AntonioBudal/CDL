"""Confere o efeito da margem vertical automática do ``rapidocr`` (``Global.use_vertical_padding``).

Lê as linhas de um conjunto do EXP-014 com o reconhecedor do pacote, com a regra ligada (padrão) e
desligada, e grava as predições no formato do ``score.py``. Roda em ``EXP-008/envs/ppocr``; sem
rede.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

import cv2
from rapidocr import RapidOCR

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-014"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    logging.getLogger("RapidOCR").setLevel(logging.ERROR)
    name = sys.argv[1]
    items = json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
    for padding in (True, False):
        engine = RapidOCR(params={"Global.use_vertical_padding": padding})
        started = time.perf_counter()
        out = {}
        for item in items:
            image = cv2.imread(str(ROOT / item["image"]), cv2.IMREAD_COLOR)
            result = engine(image, use_det=False, use_cls=False, use_rec=True)
            texts = list(getattr(result, "txts", None) or [])
            out[item["id"]] = str(texts[0]) if texts else ""
        ms = (time.perf_counter() - started) * 1000 / len(items)
        path = DATA / f"pred-rapidocr-padding{int(padding)}-{name}.json"
        path.write_text(
            json.dumps({"set": name, "items": out, "ms_per_line": ms}, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"margem vertical {padding}: {ms:.0f} ms por linha -> {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
