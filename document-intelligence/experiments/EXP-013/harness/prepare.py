"""Conjuntos do EXP-013 (fora do Git, em ``dataset/processed/exp-013/``).

* ``cal-bressay``: as 154 páginas de VALIDAÇÃO do BRESSAY, na escala original, com o texto;
* ``cal-gnhk``: as 150 fotos de TREINO do GNHK sorteadas no EXP-008, com o texto anotado;
* ``test-bressay`` e ``test-gnhk``: os conjuntos de teste do EXP-012 (escala original).

Para cada um, ``<conjunto>-worker.json`` (imagens e hashes) e ``<conjunto>-refs.json`` (texto, só
para o avaliador). Nenhum texto é impresso.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "dataset" / "processed" / "exp-013"
EXP008 = ROOT / "dataset" / "processed" / "exp-008"
EXP012 = ROOT / "dataset" / "processed" / "exp-012"
BRESSAY_ZIP = ROOT / "dataset" / "raw" / "exp-001" / "bressay.zip"
GNHK_TRAIN = ROOT / "dataset" / "raw" / "exp-007" / "gnhk" / "train_data.zip"
CORNERS = ("x0", "x1", "x2", "x3")


def special(text: str) -> bool:
    return text.startswith("%") and text.endswith("%")


def gnhk_page_text(words: list[dict]) -> str:
    lines: dict[int, list[dict]] = {}
    for word in words:
        if not special(word.get("text", "")):
            lines.setdefault(int(word["line_idx"]), []).append(word)
    return "\n".join(
        " ".join(
            w["text"] for w in sorted(group, key=lambda w: sum(w["polygon"][k] for k in CORNERS))
        )
        for _, group in sorted(lines.items())
    )


def page_item(page_id: str, path: Path) -> dict:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    return {
        "id": page_id,
        "image": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
    }


def write(name: str, pages: list[dict], refs: dict) -> None:
    (OUT / f"{name}-worker.json").write_text(json.dumps({"pages": pages}), encoding="utf-8")
    (OUT / f"{name}-refs.json").write_text(
        json.dumps({"refs": refs}, ensure_ascii=False), encoding="utf-8"
    )
    print(name, len(pages), "páginas")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)

    bressay = zipfile.ZipFile(BRESSAY_ZIP)
    target = OUT / "cal-bressay"
    target.mkdir(exist_ok=True)
    pages, refs = [], {}
    for page_id in sorted(i.decode() for i in bressay.read("bressay/sets/validation.txt").split()):
        data = bressay.read(f"bressay/data/pages/{page_id}/{page_id}.png")
        color = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        path = target / f"{page_id}.png"
        cv2.imwrite(str(path), color)
        pages.append(page_item(page_id, path))
        refs[page_id] = bressay.read(f"bressay/data/pages/{page_id}/{page_id}.txt").decode("utf-8")
    write("cal-bressay", pages, refs)

    gnhk = zipfile.ZipFile(GNHK_TRAIN)
    manifest = json.loads((EXP008 / "cal-gnhk-manifest.json").read_text(encoding="utf-8"))
    pages = [page_item(p["id"], ROOT / p["image"]) for p in manifest["pages"]]
    refs = {p["id"]: gnhk_page_text(json.loads(gnhk.read(f"train/{p['id']}.json"))) for p in pages}
    write("cal-gnhk", pages, refs)

    for source, name in (("bressay-native", "test-bressay"), ("gnhk", "test-gnhk")):
        shutil.copyfile(EXP012 / f"{source}-worker.json", OUT / f"{name}-worker.json")
        shutil.copyfile(EXP012 / f"{source}-refs.json", OUT / f"{name}-refs.json")
        print(name, "copiado do EXP-012")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
