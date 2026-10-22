"""Linhas do BRESSAY para o ajuste fino (EXP-014), fora do Git em ``dataset/processed/exp-014/``.

* ``train``: todas as linhas das páginas da divisão oficial de TREINO (recortes exatos do dataset);
* ``val``: as linhas de VALIDAÇÃO já extraídas no EXP-011;
* ``test-exp001`` e ``test-all``: as 398 linhas do EXP-001 e todas as linhas de teste do EXP-009.

Grava ``<conjunto>.json`` com caminho da imagem e transcrição (só para treino e avaliação; nunca
impresso).
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "dataset" / "processed" / "exp-014"
BRESSAY_ZIP = ROOT / "dataset" / "raw" / "exp-001" / "bressay.zip"
EXP009 = ROOT / "dataset" / "processed" / "exp-009"
EXP011 = ROOT / "dataset" / "processed" / "exp-011"


def from_worker(worker: Path, refs: Path) -> list[dict]:
    pages = json.loads(worker.read_text(encoding="utf-8"))["pages"]
    texts = json.loads(refs.read_text(encoding="utf-8"))["refs"]
    return [{"id": p["id"], "image": p["image"], "text": texts[p["id"]]} for p in pages]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    archive = zipfile.ZipFile(BRESSAY_ZIP)
    pages = {i.decode() for i in archive.read("bressay/sets/training.txt").split()}
    target = OUT / "train-lines"
    target.mkdir(exist_ok=True)
    items = []
    for name in sorted(archive.namelist()):
        if name.startswith("bressay/data/lines/") and name.endswith(".png"):
            if name.split("/")[3] not in pages:
                continue
            path = target / Path(name).name
            path.write_bytes(archive.read(name))
            text = archive.read(name[:-4] + ".txt").decode("utf-8").strip()
            items.append(
                {"id": path.stem, "image": path.relative_to(ROOT).as_posix(), "text": text}
            )
    sets = {
        "train": items,
        "val": from_worker(EXP011 / "val-lines-worker.json", EXP011 / "val-lines-refs.json"),
        "test-exp001": from_worker(
            EXP009 / "lines-exp001-worker.json", EXP009 / "lines-exp001-refs.json"
        ),
        "test-all": from_worker(
            EXP009 / "lines-bressay-worker.json", EXP009 / "lines-bressay-refs.json"
        ),
    }
    for name, content in sets.items():
        (OUT / f"{name}.json").write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        print(name, len(content), "linhas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
