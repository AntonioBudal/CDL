"""Recortes das linhas da divisão de VALIDAÇÃO do BRESSAY, para calibrar a correção (EXP-011).

Grava, fora do Git em ``dataset/processed/exp-011/``: os recortes,
``val-lines-worker.json`` (só imagens e hashes) e ``val-lines-refs.json`` (transcrições, lidas só
pelo avaliador). Nenhum texto é impresso.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "dataset" / "processed" / "exp-011"
BRESSAY_ZIP = ROOT / "dataset" / "raw" / "exp-001" / "bressay.zip"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    archive = zipfile.ZipFile(BRESSAY_ZIP)
    pages = {item.decode() for item in archive.read("bressay/sets/validation.txt").split()}
    target = OUT / "val-lines"
    target.mkdir(parents=True, exist_ok=True)
    items, refs = [], {}
    for name in sorted(archive.namelist()):
        if not (name.startswith("bressay/data/lines/") and name.endswith(".png")):
            continue
        if name.split("/")[3] not in pages:
            continue
        key = Path(name).stem
        data = archive.read(name)
        path = target / f"{key}.png"
        path.write_bytes(data)
        relative = path.relative_to(ROOT).as_posix()
        items.append({"id": key, "image": relative, "sha256": hashlib.sha256(data).hexdigest()})
        refs[key] = archive.read(name[:-4] + ".txt").decode("utf-8").strip()
    worker = {"dataset": "exp-011-val-lines", "pages": items}
    (OUT / "val-lines-worker.json").write_text(json.dumps(worker), encoding="utf-8")
    (OUT / "val-lines-refs.json").write_text(
        json.dumps({"refs": refs}, ensure_ascii=False), encoding="utf-8"
    )
    print("linhas de validação:", len(items), "de", len(pages), "páginas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
