"""Monta os conjuntos do EXP-009 (fora do Git, em ``dataset/processed/exp-009/``).

Para cada conjunto são gravados dois arquivos: ``<conjunto>-worker.json`` (só imagens e hashes; é o
que
o processo do modelo recebe) e ``<conjunto>-refs.json`` (as transcrições, lidas só pelo avaliador).
Nenhum texto é impresso.

Uso: ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-009/harness/prepare.py``
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import cv2
import numpy as np
from crop import crop_line

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "dataset" / "processed" / "exp-009"
EXP007 = ROOT / "dataset" / "processed" / "exp-007"
SUBSET = ROOT / "dataset" / "raw" / "exp-001" / "bressay-subset" / "manifest.json"
GNHK_ZIP = ROOT / "dataset" / "raw" / "exp-007" / "gnhk" / "test_data.zip"
BRESSAY_ZIP = ROOT / "dataset" / "raw" / "exp-001" / "bressay.zip"
MAX_SIDE = 2048
CORNERS = (("x0", "y0"), ("x1", "y1"), ("x2", "y2"), ("x3", "y3"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def item(key: str, path: Path) -> dict:
    return {"id": key, "image": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def write(name: str, items: list[dict], refs: dict, extra: dict | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    worker = {"dataset": f"exp-009-{name}", "pages": items}
    (OUT / f"{name}-worker.json").write_text(json.dumps(worker), encoding="utf-8")
    content = {"refs": refs, **(extra or {})}
    (OUT / f"{name}-refs.json").write_text(
        json.dumps(content, ensure_ascii=False), encoding="utf-8"
    )
    print(name, len(items), "itens")


def lines_exp001() -> None:
    manifest = json.loads(SUBSET.read_text(encoding="utf-8"))
    items, refs = [], {}
    for line in manifest["lines"]:
        path = ROOT / line["image"]
        if sha256(path) != line["sha256"]:
            raise SystemExit(f"recorte do EXP-001 alterado: {line['id']}")
        items.append(item(line["id"], path))
        refs[line["id"]] = line["text"]
    write("lines-exp001", items, refs)


def _special(text: str) -> bool:
    return text.startswith("%") and text.endswith("%")


def lines_gnhk() -> None:
    archive = zipfile.ZipFile(GNHK_ZIP)
    target = OUT / "gnhk-lines"
    target.mkdir(parents=True, exist_ok=True)
    items, refs = [], {}
    skipped = 0
    for name in sorted(n for n in archive.namelist() if n.lower().endswith(".jpg")):
        photo_id = Path(name).stem
        original = cv2.imdecode(np.frombuffer(archive.read(name), np.uint8), cv2.IMREAD_COLOR)
        scale = min(1.0, MAX_SIDE / max(original.shape[:2]))
        work = cv2.imread(str(EXP007 / "gnhk" / f"{photo_id}.jpg"), cv2.IMREAD_COLOR)
        words = json.loads(archive.read(name[:-4] + ".json"))
        groups: dict[int, list[dict]] = {}
        for word in words:
            groups.setdefault(int(word["line_idx"]), []).append(word)
        for line_idx, group in sorted(groups.items()):
            if any(w.get("type") != "H" or _special(w.get("text", "")) for w in group):
                skipped += 1
                continue
            points = [
                [w["polygon"][x] * scale, w["polygon"][y] * scale]
                for w in group
                for x, y in CORNERS
            ]
            order = sorted(group, key=lambda w: sum(w["polygon"][x] for x, _ in CORNERS))
            key = f"{photo_id}-l{line_idx:03d}"
            path = target / f"{key}.png"
            cv2.imwrite(str(path), crop_line(work, points))
            items.append(item(key, path))
            refs[key] = " ".join(w["text"] for w in order)
    write("lines-gnhk", items, refs, {"skipped_lines": skipped})


def bressay() -> None:
    archive = zipfile.ZipFile(BRESSAY_ZIP)
    manifest = json.loads((EXP007 / "bressay-x3-manifest.json").read_text(encoding="utf-8"))
    names = archive.namelist()
    target = OUT / "bressay-lines"
    target.mkdir(parents=True, exist_ok=True)
    pages, page_refs, line_items, line_refs, page_lines = [], {}, [], {}, {}
    for page in manifest["pages"]:
        pid = page["id"]
        pages.append({"id": pid, "image": page["image"], "sha256": page["sha256"]})
        page_refs[pid] = archive.read(f"bressay/data/pages/{pid}/{pid}.txt").decode("utf-8")
        prefix = f"bressay/data/lines/{pid}/"
        crops = sorted(n for n in names if n.startswith(prefix) and n.endswith(".png"))
        page_lines[pid] = []
        for crop in crops:
            key = Path(crop).stem
            path = target / f"{key}.png"
            path.write_bytes(archive.read(crop))
            line_items.append(item(key, path))
            line_refs[key] = archive.read(crop[:-4] + ".txt").decode("utf-8").strip()
            page_lines[pid].append(key)
    write("pages-bressay", pages, page_refs)
    write("lines-bressay", line_items, line_refs, {"page_lines": page_lines})


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    lines_exp001()
    lines_gnhk()
    bressay()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
