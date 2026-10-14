"""Prepara os conjuntos de calibração do EXP-008 (nunca usados no teste).

* ``cal-gnhk``: 150 fotos sorteadas, com semente fixa, da divisão oficial de **treino** do GNHK;
* ``cal-bressay``: as páginas da divisão oficial de **validação** do BRESSAY, ampliadas 3×.

Mesmo tratamento do EXP-007: orientação aplicada, lado maior limitado a 2.048 px, anotação escalada;
imagens de trabalho sem metadados. Saídas fora do Git em ``dataset/processed/exp-008/``; no Git, só
``subsets.json`` (nomes e SHA-256).

Uso: ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-008/harness/prepare.py``
"""

from __future__ import annotations

import json
import random
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from bressay import page_truth, scale_truth
from common import DATA, EXPERIMENT, ROOT, sha256_file, write_json
from gnhk import lines_from_words

GNHK_ZIP = ROOT / "dataset" / "raw" / "exp-007" / "gnhk" / "train_data.zip"
GNHK_SHA256 = "a8a841f504761a7df91c5104cff1d85d534dd5834af99c2d68baecb7c6cddda2"
BRESSAY_ZIP = ROOT / "dataset" / "raw" / "exp-001" / "bressay.zip"
SEED = 1234
GNHK_SAMPLE = 150
MAX_SIDE = 2048
UPSCALE = 3


def _page(page_id, image: Path, level: str, shape, lines, ignore) -> dict:
    return {
        "id": page_id,
        "image": image.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(image),
        "width": int(shape[1]),
        "height": int(shape[0]),
        "level": level,
        "family": "calibration",
        "lines": lines,
        "blocks": [],
        "ignore": ignore,
    }


def prepare_gnhk() -> tuple[dict, list[dict]]:
    if sha256_file(GNHK_ZIP) != GNHK_SHA256:
        raise SystemExit("GNHK: SHA-256 do zip de treino não confere")
    archive = zipfile.ZipFile(GNHK_ZIP)
    names = sorted(n for n in archive.namelist() if n.lower().endswith(".jpg"))
    chosen = sorted(random.Random(SEED).sample(names, GNHK_SAMPLE))
    target = DATA / "cal-gnhk"
    target.mkdir(parents=True, exist_ok=True)
    pages, sources = [], []
    for name in chosen:
        raw = archive.read(name)
        page_id = Path(name).stem
        image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        scale = min(1.0, MAX_SIDE / max(image.shape[:2]))
        if scale < 1.0:
            size = (round(image.shape[1] * scale), round(image.shape[0] * scale))
            image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
        lines, ignore = lines_from_words(json.loads(archive.read(name[:-4] + ".json")), scale)
        path = target / f"{page_id}.jpg"
        cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        sources.append({"id": page_id, "member": name})
        if lines:
            region = page_id.split("_")[1] if page_id.count("_") >= 2 else "outros"
            pages.append(_page(page_id, path, region, image.shape, lines, ignore))
    return {"dataset": "exp-008-cal-gnhk", "pages": pages}, sources


def prepare_bressay() -> tuple[dict, list[dict]]:
    archive = zipfile.ZipFile(BRESSAY_ZIP)
    wanted = sorted(item.decode() for item in archive.read("bressay/sets/validation.txt").split())
    crops: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for name in archive.namelist():
        for kind in ("paragraphs", "lines"):
            prefix = f"bressay/data/{kind}/"
            if name.startswith(prefix) and name.endswith(".png"):
                crops[name[len(prefix) :].split("/")[0]][kind].append(name)

    def gray(name: str) -> np.ndarray:
        return cv2.imdecode(np.frombuffer(archive.read(name), np.uint8), cv2.IMREAD_GRAYSCALE)

    target = DATA / "cal-bressay"
    target.mkdir(parents=True, exist_ok=True)
    pages, sources = [], []
    for page_id in wanted:
        member = f"bressay/data/pages/{page_id}/{page_id}.png"
        color = cv2.imdecode(np.frombuffer(archive.read(member), np.uint8), cv2.IMREAD_COLOR)
        truth = page_truth(
            cv2.cvtColor(color, cv2.COLOR_BGR2GRAY),
            {Path(n).stem: gray(n) for n in crops[page_id]["paragraphs"]},
            {Path(n).stem: gray(n) for n in crops[page_id]["lines"]},
        )
        sources.append({"id": page_id, "member": member, "usable": not truth["missing"]})
        if truth["missing"] or not truth["lines"]:
            continue
        big = cv2.resize(color, None, fx=UPSCALE, fy=UPSCALE, interpolation=cv2.INTER_CUBIC)
        path = target / f"{page_id}.png"
        cv2.imwrite(str(path), big)
        lines = [
            {k: line[k] for k in ("id", "bbox", "polygon")}
            for line in scale_truth(truth, UPSCALE)["lines"]
        ]
        pages.append(_page(page_id, path, "x3", big.shape, lines, []))
    return {"dataset": "exp-008-cal-bressay", "pages": pages}, sources


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    gnhk, gnhk_sources = prepare_gnhk()
    bressay, bressay_sources = prepare_bressay()
    write_json(DATA / "cal-gnhk-manifest.json", gnhk)
    write_json(DATA / "cal-bressay-manifest.json", bressay)
    write_json(
        EXPERIMENT / "subsets.json",
        {
            "schema": "leitorum-di-subsets/1",
            "note": "Conjuntos de CALIBRAÇÃO. Só nomes de arquivo; o conteúdo não é versionado. "
            "O teste é o do EXP-007 (experiments/EXP-007/subsets.json).",
            "gnhk": {
                "archive": "train_data.zip",
                "archive_sha256": GNHK_SHA256,
                "split": f"treino oficial, amostra de {GNHK_SAMPLE} com semente {SEED}",
                "files": gnhk_sources,
            },
            "bressay": {
                "archive": "bressay.zip (DOI 10.5281/zenodo.11637681)",
                "split": "bressay/sets/validation.txt",
                "files": bressay_sources,
            },
        },
        indent=1,
    )
    for name, manifest in (("cal-gnhk", gnhk), ("cal-bressay", bressay)):
        pages = manifest["pages"]
        print(name, "páginas:", len(pages), "linhas:", sum(len(p["lines"]) for p in pages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
