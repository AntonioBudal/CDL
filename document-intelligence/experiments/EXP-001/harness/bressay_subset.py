"""Congela um subconjunto de linhas do split de teste oficial do BRESSAY para o EXP-001.

LICENSE STATUS: NEEDS VALIDATION — o Zenodo declara CC-BY-4.0, mas o README do dataset restringe
o uso a pesquisa e ensino não comerciais. Uso experimental local autorizado pelo usuário em
2026-10-01. Por isso as imagens e as transcrições ficam só em ``dataset/raw/`` (fora do Git); o
arquivo versionado de seleção traz apenas identificadores e hashes.

Uso: ``python bressay_subset.py`` (requer ``dataset/raw/exp-001/bressay.zip``).
"""

from __future__ import annotations

import hashlib
import json
import random
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / "dataset" / "raw" / "exp-001" / "bressay.zip"
ARCHIVE_MD5 = "e4a4093304efff8322b605c8b79aa957"
SUBSET_DIR = ROOT / "dataset" / "raw" / "exp-001" / "bressay-subset"
MANIFEST = SUBSET_DIR / "manifest.json"
SELECTION = ROOT / "dataset" / "fixtures" / "exp-001" / "bressay-selection.json"
SCHEMA = "leitorum-di-lines/1"
SEED = 1234
LINES_PER_PAGE = 2
MIN_CHARS = 10
# Marcas de anotação do BRESSAY (ilegível, rasurado, sobrescrito, subscrito): linhas excluídas.
ANNOTATION_MARKS = ("@@", "--", "##", "$$")
LINES_PREFIX = "bressay/data/lines/"


def md5_file(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - conferência contra o checksum publicado no Zenodo
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_eligible(text: str) -> bool:
    return len(text) >= MIN_CHARS and not any(mark in text for mark in ANNOTATION_MARKS)


def select_lines(archive: zipfile.ZipFile, seed: int = SEED) -> list[tuple[str, str, str]]:
    """Devolve ``(página, id da linha, texto)`` — até ``LINES_PER_PAGE`` por página de teste."""
    pages = sorted(archive.read("bressay/sets/test.txt").decode("utf-8").split())
    by_page: dict[str, list[str]] = defaultdict(list)
    for name in archive.namelist():
        if name.startswith(LINES_PREFIX) and name.endswith(".png"):
            page, filename = name[len(LINES_PREFIX) :].split("/")
            by_page[page].append(filename[: -len(".png")])

    rng = random.Random(seed)
    selected = []
    for page in pages:
        eligible = []
        for line_id in sorted(by_page.get(page, [])):
            raw = archive.read(f"{LINES_PREFIX}{page}/{line_id}.txt").decode("utf-8")
            text = unicodedata.normalize("NFC", " ".join(raw.split()))
            if is_eligible(text):
                eligible.append((page, line_id, text))
        selected.extend(sorted(rng.sample(eligible, min(LINES_PER_PAGE, len(eligible)))))
    return selected


def main() -> int:
    if md5_file(ARCHIVE) != ARCHIVE_MD5:
        raise SystemExit("MD5 do bressay.zip não confere com o publicado no Zenodo.")

    SUBSET_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for page, line_id, text in select_lines(archive):
            data = archive.read(f"{LINES_PREFIX}{page}/{line_id}.png")
            image = SUBSET_DIR / f"{line_id}.png"
            image.write_bytes(data)
            lines.append(
                {
                    "id": line_id,
                    "image": image.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "text": text,
                    "writer": page,
                    "origin": "real",
                }
            )

    header = {
        "schema": SCHEMA,
        "dataset": "bressay-test-subset",
        "origin": "real",
        "source": "https://zenodo.org/records/11637681 (DOI 10.5281/zenodo.11637681)",
        "license_status": "NEEDS VALIDATION",
        "archive_md5": ARCHIVE_MD5,
        "split": "test (oficial; uma página = um autor)",
        "seed": SEED,
        "lines_per_page": LINES_PER_PAGE,
        "filter": f"mínimo de {MIN_CHARS} caracteres; sem marcas de anotação {ANNOTATION_MARKS}",
    }
    MANIFEST.write_text(
        json.dumps({**header, "lines": lines}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    public = [{key: line[key] for key in ("id", "writer", "sha256")} for line in lines]
    SELECTION.write_text(
        json.dumps({**header, "lines": public}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    writers = len({line["writer"] for line in lines})
    print(f"{len(lines)} linhas de {writers} autores; manifesto privado em {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
