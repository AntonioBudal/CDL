"""Extrai as divisões oficiais de teste do GNHK e do BRESSAY e monta a verdade de chão.

Saídas:

* ``dataset/processed/exp-007/`` (fora do Git): imagens de trabalho e manifestos com geometria —
  ``gnhk-manifest.json``, ``bressay-x3-manifest.json`` e ``bressay-native-manifest.json``;
* ``experiments/EXP-007/subsets.json`` (versionado): nomes e SHA-256 dos arquivos de origem, sem
  conteúdo;
* um resumo numérico da verdade de chão em ``--report``.

Fotos do GNHK: a orientação dos metadados é aplicada (é o referencial das anotações) e o lado maior
é
limitado a ``MAX_SIDE`` px, a escala em que o pipeline foi validado; a anotação é escalada junto. As
imagens de trabalho são regravadas sem metadados. Páginas do BRESSAY: gravadas na escala nativa e
ampliadas ``UPSCALE`` vezes.

Uso (a partir de ``document-intelligence/``):
``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-007/harness/prepare.py --report evaluation/benchmarks/<arquivo>.json``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from bressay import page_truth, scale_truth
from gnhk import lines_from_words

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset" / "processed" / "exp-007"
GNHK_ZIP = ROOT / "dataset" / "raw" / "exp-007" / "gnhk" / "test_data.zip"
GNHK_SHA256 = "6f3d65d91535d1665050afd83a9f3831394d80accfae88c5b91bbb990781eacb"
BRESSAY_ZIP = ROOT / "dataset" / "raw" / "exp-001" / "bressay.zip"
MAX_SIDE = 2048
UPSCALE = 3
JPEG_QUALITY = 95


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _page(page_id, image: Path, level: str, family: str, shape, truth) -> dict[str, Any]:
    return {
        "id": page_id,
        "image": _relative(image),
        "sha256": sha256_file(image),
        "width": int(shape[1]),
        "height": int(shape[0]),
        "level": level,
        "family": family,
        "lines": truth["lines"],
        "blocks": truth.get("blocks", []),
        "reading_order": truth.get("reading_order", []),
        "ignore": truth.get("ignore", []),
    }


def prepare_gnhk() -> tuple[dict, list[dict], dict]:
    if sha256_file(GNHK_ZIP) != GNHK_SHA256:
        raise SystemExit("GNHK: SHA-256 do zip de teste não confere")
    archive = zipfile.ZipFile(GNHK_ZIP)
    target = OUT / "gnhk"
    target.mkdir(parents=True, exist_ok=True)
    pages, sources, unusable = [], [], []
    words_total = 0
    for name in sorted(n for n in archive.namelist() if n.lower().endswith(".jpg")):
        raw = archive.read(name)
        page_id = Path(name).stem
        sources.append({"id": page_id, "member": name, "sha256": sha256_bytes(raw)})
        image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        scale = min(1.0, MAX_SIDE / max(image.shape[:2]))
        if scale < 1.0:
            size = (round(image.shape[1] * scale), round(image.shape[0] * scale))
            image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
        words = json.loads(archive.read(name[: -len(".jpg")] + ".json"))
        words_total += len(words)
        lines, ignore = lines_from_words(words, scale)
        path = target / f"{page_id}.jpg"
        cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not lines:
            unusable.append(page_id)
            continue
        region = page_id.split("_")[1] if page_id.count("_") >= 2 else "outros"
        pages.append(
            _page(page_id, path, region, "gnhk", image.shape, {"lines": lines, "ignore": ignore})
        )
    manifest = {"schema": "leitorum-di-pages/1", "dataset": "exp-007-gnhk-test", "pages": pages}
    summary = {
        "source_photos": len(sources),
        "usable_photos": len(pages),
        "unusable_photos": unusable,
        "words": words_total,
        "lines": sum(len(p["lines"]) for p in pages),
        "ignored_regions": sum(len(p["ignore"]) for p in pages),
        "lines_per_photo_median": statistics.median(len(p["lines"]) for p in pages),
        "by_region": dict(Counter(p["level"] for p in pages)),
        "max_side_px": MAX_SIDE,
    }
    return manifest, sources, summary


def _gray(archive: zipfile.ZipFile, name: str) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(archive.read(name), np.uint8), cv2.IMREAD_GRAYSCALE)


def prepare_bressay() -> tuple[dict, dict, list[dict], dict]:
    archive = zipfile.ZipFile(BRESSAY_ZIP)
    wanted = [item.decode() for item in archive.read("bressay/sets/test.txt").split()]
    crops: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for name in archive.namelist():
        for kind in ("paragraphs", "lines"):
            prefix = f"bressay/data/{kind}/"
            if name.startswith(prefix) and name.endswith(".png"):
                crops[name[len(prefix) :].split("/")[0]][kind].append(name)

    native_dir, big_dir = OUT / "bressay-native", OUT / f"bressay-x{UPSCALE}"
    native_dir.mkdir(parents=True, exist_ok=True)
    big_dir.mkdir(parents=True, exist_ok=True)
    native_pages, big_pages, sources, incomplete = [], [], [], []
    crops_total = crops_missing = 0
    heights = []
    for page_id in sorted(wanted):
        member = f"bressay/data/pages/{page_id}/{page_id}.png"
        raw = archive.read(member)
        sources.append({"id": page_id, "member": member, "sha256": sha256_bytes(raw)})
        color = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        truth = page_truth(
            gray,
            {Path(n).stem: _gray(archive, n) for n in crops[page_id]["paragraphs"]},
            {Path(n).stem: _gray(archive, n) for n in crops[page_id]["lines"]},
        )
        total = len(crops[page_id]["paragraphs"]) + len(crops[page_id]["lines"])
        crops_total += total
        crops_missing += len(truth["missing"])
        if truth["missing"] or not truth["lines"]:
            incomplete.append({"id": page_id, "missing": len(truth["missing"]), "crops": total})
            continue
        heights.extend(line["bbox"][3] - line["bbox"][1] for line in truth["lines"])
        native_path = native_dir / f"{page_id}.png"
        cv2.imwrite(str(native_path), color)
        native_pages.append(_page(page_id, native_path, "native", "essay", color.shape, truth))
        big = cv2.resize(color, None, fx=UPSCALE, fy=UPSCALE, interpolation=cv2.INTER_CUBIC)
        big_path = big_dir / f"{page_id}.png"
        cv2.imwrite(str(big_path), big)
        big_pages.append(
            _page(page_id, big_path, f"x{UPSCALE}", "essay", big.shape, scale_truth(truth, UPSCALE))
        )

    def manifest(name: str, pages: list[dict]) -> dict:
        return {"schema": "leitorum-di-pages/1", "dataset": f"exp-007-{name}-test", "pages": pages}

    summary = {
        "source_pages": len(sources),
        "usable_pages": len(native_pages),
        "incomplete_pages": incomplete,
        "crops": crops_total,
        "crops_located": crops_total - crops_missing,
        "location_rate": (crops_total - crops_missing) / crops_total if crops_total else None,
        "lines": sum(len(p["lines"]) for p in native_pages),
        "blocks": sum(len(p["blocks"]) for p in native_pages),
        "blocks_per_page_median": statistics.median(len(p["blocks"]) for p in native_pages),
        "line_height_native_median_px": statistics.median(heights),
        "page_width_native_median_px": statistics.median(p["width"] for p in native_pages),
        "upscale": UPSCALE,
    }
    return (
        manifest("bressay-native", native_pages),
        manifest(f"bressay-x{UPSCALE}", big_pages),
        sources,
        summary,
    )


def _write(path: Path, content: Any, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(content, ensure_ascii=False, indent=indent) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepara os dados do EXP-007")
    parser.add_argument("--report", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    gnhk_manifest, gnhk_sources, gnhk_summary = prepare_gnhk()
    native, big, bressay_sources, bressay_summary = prepare_bressay()
    _write(OUT / "gnhk-manifest.json", gnhk_manifest)
    _write(OUT / "bressay-native-manifest.json", native)
    _write(OUT / f"bressay-x{UPSCALE}-manifest.json", big)
    _write(
        EXPERIMENT / "subsets.json",
        {
            "schema": "leitorum-di-subsets/1",
            "note": "Só nomes e SHA-256 dos arquivos de origem. O conteúdo não é versionado.",
            "gnhk": {
                "archive": "test_data.zip",
                "archive_sha256": GNHK_SHA256,
                "split": "teste oficial",
                "files": gnhk_sources,
            },
            "bressay": {
                "archive": "bressay.zip (DOI 10.5281/zenodo.11637681)",
                "split": "bressay/sets/test.txt",
                "files": bressay_sources,
            },
        },
        indent=1,
    )
    report = {
        "schema": "leitorum-di-ground-truth/1",
        "experiment": "EXP-007",
        "gnhk": gnhk_summary,
        "bressay": bressay_summary,
    }
    _write(Path(args.report), report, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
