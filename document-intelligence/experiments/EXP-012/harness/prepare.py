"""Manifestos do EXP-012 (fora do Git, em ``dataset/processed/exp-012/``).

Três variantes de página: BRESSAY nativa, BRESSAY 3× e GNHK (fotos de trabalho do EXP-007). Para
cada uma: ``<variante>-worker.json`` (imagens e hashes) e ``<variante>-refs.json`` (texto da página,
só para o avaliador). No GNHK, o texto da página é o das palavras anotadas, agrupadas pelo índice de
linha e em ordem horizontal, sem as marcas especiais. Nenhum texto é impresso.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "dataset" / "processed" / "exp-012"
EXP007 = ROOT / "dataset" / "processed" / "exp-007"
BRESSAY_ZIP = ROOT / "dataset" / "raw" / "exp-001" / "bressay.zip"
GNHK_ZIP = ROOT / "dataset" / "raw" / "exp-007" / "gnhk" / "test_data.zip"
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


def write(name: str, manifest: dict, refs: dict) -> None:
    pages = [
        {k: p[k] for k in ("id", "image", "sha256", "width", "height")} for p in manifest["pages"]
    ]
    (OUT / f"{name}-worker.json").write_text(json.dumps({"pages": pages}), encoding="utf-8")
    (OUT / f"{name}-refs.json").write_text(
        json.dumps({"refs": refs}, ensure_ascii=False), encoding="utf-8"
    )
    print(name, len(pages), "páginas")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    bressay = zipfile.ZipFile(BRESSAY_ZIP)
    for variant in ("bressay-native", "bressay-x3"):
        manifest = json.loads((EXP007 / f"{variant}-manifest.json").read_text(encoding="utf-8"))
        refs = {
            p["id"]: bressay.read(f"bressay/data/pages/{p['id']}/{p['id']}.txt").decode("utf-8")
            for p in manifest["pages"]
        }
        write(variant, manifest, refs)
    gnhk = zipfile.ZipFile(GNHK_ZIP)
    manifest = json.loads((EXP007 / "gnhk-manifest.json").read_text(encoding="utf-8"))
    refs = {
        p["id"]: gnhk_page_text(json.loads(gnhk.read(f"test/{p['id']}.json")))
        for p in manifest["pages"]
    }
    write("gnhk", manifest, refs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
