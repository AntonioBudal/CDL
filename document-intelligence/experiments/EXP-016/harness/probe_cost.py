"""Sonda do EXP-016: onde vai o tempo por página (só tempos; nenhum texto é gravado ou mostrado).

Roda no ambiente ``EXP-008/envs/ppocr`` sobre as primeiras páginas do conjunto de **calibração** do
BRESSAY (EXP-013), com o alvo de 80 px: tempo das duas detecções, do recorte e da leitura, com e sem
lote e com e sem margem.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crop import box_points, crop_line  # noqa: E402
from merge import merge_lines  # noqa: E402
from pipeline import PagePipeline, median_height, prepare_line, scale_factor  # noqa: E402
from probe_batch import MODELS  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]


def main(pages: int = 20) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    calibration = json.loads((ROOT / "experiments/EXP-008/calibration.json").read_text("utf-8"))
    merge = calibration["candidates"]["ppocr-det"]["best"]["params"]
    pipeline = PagePipeline()
    pipeline.load({"options": {"models": MODELS, "merge": merge, "target": 80}})
    manifest = json.loads(
        (ROOT / "dataset/processed/exp-013/cal-bressay-worker.json").read_text("utf-8")
    )
    rows = []
    for page in manifest["pages"][:pages]:
        timing = {}
        t = time.perf_counter()
        original = cv2.imread(str(ROOT / page["image"]), cv2.IMREAD_COLOR)
        lines = pipeline._detect(original)
        timing["det1"] = time.perf_counter() - t
        scale = scale_factor(median_height(lines), 80)
        image = original
        t = time.perf_counter()
        if scale > 1:
            image = cv2.resize(original, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            lines = pipeline._detect(image)
        timing["det2"] = time.perf_counter() - t
        t = time.perf_counter()
        crops = [
            prepare_line(crop_line(image, ln.get("polygon") or box_points(ln["bbox"])))[0]
            for ln in merge_lines(lines, pipeline._merge)
        ]
        timing["crop"] = time.perf_counter() - t
        for name, batch, extra in (("read", 1, 640), ("read_b8", 8, 640), ("read_m0", 1, 0)):
            pipeline._extra = extra
            t = time.perf_counter()
            pipeline._read_many(crops, batch=batch)
            timing[name] = time.perf_counter() - t
        pipeline._extra = 640
        timing["scale"], timing["lines"] = scale, len(crops)
        rows.append(timing)
    keys = ("det1", "det2", "crop", "read", "read_b8", "read_m0")
    print(json.dumps({
        "pages": len(rows),
        "median_s": {k: round(statistics.median(r[k] for r in rows), 3) for k in keys},
        "median_lines": statistics.median(r["lines"] for r in rows),
        "scales": sorted({r["scale"] for r in rows}),
    }))  # fmt: skip
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
