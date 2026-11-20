"""Registra as impressões digitais (SHA-256) das fotos de ``dataset/raw/exp-027/fotos/`` no arquivo
versionado ``splits/pages-sha256.json`` do EXP-027, associando cada foto a um ``pNN`` pela ordem
informada pelo usuário. Só hashes, tamanhos e a origem vão para o arquivo; nenhum conteúdo.

As fotos são ordenadas pela data de modificação do arquivo (``--by mtime``, o padrão) ou pelo nome
(``--by name``) e casadas, uma a uma, com a lista ``--order``. Roda no ambiente do motor (Pillow),
a partir de ``document-intelligence/``::

    ..\\caderno-leitura-0.1\\motor\\.venv\\Scripts\\python.exe -m tools.anotar.register \\
        --order p10,p11,... --source "descrição da origem" [--low-resolution]

Entradas de outros ``pNN`` são mantidas; as dos ``pNN`` listados são substituídas, com o motivo em
``amendments``.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime

from .paths import Paths, default_paths
from .prepare import SUPPORTED, sha256

SCHEMA = "exp-027-pages/2"


def photo_size(path) -> tuple[int, int]:
    from PIL import Image, ImageOps

    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).size


def register(
    paths: Paths, order: list[str], *, by: str, source: str, low_resolution: bool, reason: str
) -> dict:
    files = [p for p in paths.photos.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED]
    key = (lambda p: (p.stat().st_mtime_ns, p.name)) if by == "mtime" else (lambda p: p.name)
    files.sort(key=key)
    if len(files) != len(order):
        raise SystemExit(
            f"{len(files)} fotos na pasta, {len(order)} páginas na ordem: não registro"
        )
    if len(set(order)) != len(order):
        raise SystemExit("página repetida na ordem")
    current = {}
    if paths.registered.is_file():
        current = json.loads(paths.registered.read_text(encoding="utf-8"))
    pages = dict(current.get("pages", {}))
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    replaced = sorted(pid for pid in order if pid in pages)
    for pid, path in zip(order, files, strict=True):
        width, height = photo_size(path)
        pages[pid] = {
            "sha256": sha256(path),
            "width": width,
            "height": height,
            "format": path.suffix.lower().lstrip("."),
            "low_resolution": low_resolution,
            "source": source,
            "registered_at": now,
        }
    hashes = [entry["sha256"] for entry in pages.values()]
    if len(set(hashes)) != len(hashes):
        raise SystemExit("duas páginas com a mesma foto: não registro")
    amendments = list(current.get("amendments", []))
    amendments.append(
        {"at": now, "pages": order, "replaced": replaced, "by": by, "reason": reason}
    )
    out = {
        "schema": SCHEMA,
        "count": len(pages),
        "pages": dict(sorted(pages.items())),
        "amendments": amendments,
    }
    paths.registered.parent.mkdir(parents=True, exist_ok=True)
    paths.registered.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return {"registered": len(order), "replaced": replaced, "total": len(pages)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Registrar os hashes das fotos")
    parser.add_argument("--order", required=True, help="pNN separados por vírgula, na ordem")
    parser.add_argument("--by", choices=["mtime", "name"], default="mtime")
    parser.add_argument("--source", required=True, help="de onde vieram as fotos")
    parser.add_argument("--low-resolution", action="store_true")
    parser.add_argument("--reason", default="registro das fotos para a ferramenta F-DI-13.01")
    parser.add_argument("--remove", default="", help="pNN a retirar do registro, com o motivo")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    paths = default_paths()
    order = [item.strip() for item in args.order.split(",") if item.strip()]
    report = register(
        paths,
        order,
        by=args.by,
        source=args.source,
        low_resolution=args.low_resolution,
        reason=args.reason,
    )
    remove = [item.strip() for item in args.remove.split(",") if item.strip()]
    if remove:
        data = json.loads(paths.registered.read_text(encoding="utf-8"))
        for pid in remove:
            data["pages"].pop(pid, None)
        data["count"] = len(data["pages"])
        data["amendments"][-1]["removed"] = remove
        paths.registered.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")
        report["removed"] = remove
        report["total"] = data["count"]
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
