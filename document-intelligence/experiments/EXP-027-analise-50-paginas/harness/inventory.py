"""T001a — inventário das fotos exportadas: nomes neutros ``pNN``, SHA-256, formato, tamanho,
orientação EXIF e data da foto (só presença, nunca o conteúdo). Roda no ambiente do motor (PIL).

Ordem das páginas: data EXIF da foto; sem EXIF, nome do arquivo. Grava ``manifest.json`` (fora do
Git) e ``splits/pages-sha256.json`` (versionado: só id, hash e dimensões).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from paths import MANIFEST, PHOTOS, SPLITS, page_id

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def describe(path: Path) -> dict:
    """Metadados técnicos de uma foto; ``None`` nas chaves que o formato não oferece."""
    from PIL import Image, ImageOps

    info = {
        "source_suffix": path.suffix.lower(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "readable": True,
        "width": None,
        "height": None,
        "exif_present": False,
        "exif_orientation": None,
        "exif_datetime_present": False,
        "sort_key": None,
    }
    try:
        with Image.open(path) as image:
            exif = image.getexif()
            info["exif_present"] = bool(exif)
            info["exif_orientation"] = exif.get(0x0112)
            taken = exif.get(0x0132)  # DateTime; 0x9003 (original) fica no sub-IFD
            try:
                taken = exif.get_ifd(0x8769).get(0x9003) or taken
            except Exception:  # noqa: BLE001 — EXIF sem sub-IFD
                pass
            info["exif_datetime_present"] = bool(taken)
            info["sort_key"] = str(taken) if taken else None
            oriented = ImageOps.exif_transpose(image)
            info["width"], info["height"] = oriented.size
    except Exception as error:  # noqa: BLE001 — HEIC sem plugin, arquivo corrompido
        info["readable"] = False
        info["error"] = type(error).__name__
    return info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventário das fotos do EXP-027")
    parser.add_argument("--expect", type=int, default=50)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    files = sorted(p for p in PHOTOS.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not files:
        print(f"nenhuma foto em {PHOTOS}")
        return 2
    described = [(path, describe(path)) for path in files]
    # ordem: data EXIF (quando todas têm), senão nome
    if all(info["sort_key"] for _, info in described):
        described.sort(key=lambda item: (item[1]["sort_key"], item[0].name))
        order = "exif_datetime"
    else:
        order = "filename"
    pages = {}
    for index, (path, info) in enumerate(described, start=1):
        pages[page_id(index)] = {"file": path.name, **info}
    manifest = {
        "schema": "exp-027-manifest/1",
        "created_at": datetime.now(UTC).isoformat(),
        "order": order,
        "count": len(pages),
        "expected": args.expect,
        "pages": pages,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    SPLITS.mkdir(parents=True, exist_ok=True)
    public = {
        "schema": "exp-027-pages/1",
        "count": len(pages),
        "pages": {
            pid: {"sha256": p["sha256"], "width": p["width"], "height": p["height"]}
            for pid, p in pages.items()
        },
    }
    (SPLITS / "pages-sha256.json").write_text(
        json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    unreadable = [pid for pid, p in pages.items() if not p["readable"]]
    suffixes = sorted({p["source_suffix"] for p in pages.values()})
    print(
        json.dumps(
            {
                "count": len(pages),
                "expected": args.expect,
                "order": order,
                "suffixes": suffixes,
                "unreadable": unreadable,
                "with_exif": sum(1 for p in pages.values() if p["exif_present"]),
                "with_exif_datetime": sum(1 for p in pages.values() if p["exif_datetime_present"]),
                "megapixels_median": sorted(
                    (p["width"] or 0) * (p["height"] or 0) / 1e6 for p in pages.values()
                )[len(pages) // 2],
            },
            ensure_ascii=False,
        )
    )
    return 0 if len(pages) == args.expect and not unreadable else 1


if __name__ == "__main__":
    raise SystemExit(main())
