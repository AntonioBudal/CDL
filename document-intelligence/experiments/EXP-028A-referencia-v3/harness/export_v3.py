"""T007 — exporta a referência v3 a partir das anotações ``di-annotation/1``:

* ``raw/exp-028a/referencia-v3/pNN.txt`` (fora do Git): uma linha do papel por linha, na ordem de
  leitura, com o texto da 1ª passada (formato da referência do EXP-027: ``$…$``, ``[?]``);
* ``splits/test-manifest-v3.json`` (versionado): só hashes e contagens — hash da imagem (marcada
  ``low_resolution`` quando for o caso), hash do texto exportado, número de linhas e as classes.

Recusa exportar se alguma das 20 páginas não tiver a 1ª passada completa (``--partial`` só para
testes). Uso: ``python export_v3.py``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime

import common


def page_text(doc: dict) -> str:
    lines = sorted(doc["lines"], key=lambda line: line["order"])
    return "\n".join(line["pass1"]["text"] for line in lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    from tools.anotar import store

    parser = argparse.ArgumentParser(description="Exportar a referência v3")
    parser.add_argument("--partial", action="store_true", help="só para testes")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    paths = common.anotar_paths()
    test = json.loads((common.SPLITS / "test-manifest.json").read_text(encoding="utf-8"))
    registered = json.loads(paths.registered.read_text(encoding="utf-8"))["pages"]
    docs, missing = {}, []
    for pid in sorted(test["pages"]):
        path = paths.annotations / f"{pid}.json"
        doc = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        if not doc or not doc["status"]["pass1_done"] or store.validate(doc):
            missing.append(pid)
            continue
        docs[pid] = doc
    if missing and not args.partial:
        print(json.dumps({"exported": 0, "incomplete": missing}, ensure_ascii=False))
        return 1
    common.REFERENCE_V3.mkdir(parents=True, exist_ok=True)
    pages = {}
    for pid, doc in docs.items():
        text = page_text(doc)
        (common.REFERENCE_V3 / f"{pid}.txt").write_text(text, encoding="utf-8", newline="\n")
        image = registered.get(pid, {})
        pages[pid] = {
            "image_sha256": image.get("sha256"),
            "low_resolution": bool(image.get("low_resolution")),
            "reference_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "annotation_sha256": doc["content_sha256"],
            "lines": len(doc["lines"]),
            "draft_source": doc["draft_source"],
            **{k: test["pages"][pid].get(k) for k in ("escrita", "formulas", "foto")},
        }
    manifest = {
        "schema": "exp-028a-test-split/3",
        "version": 3,
        "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": "EXP-028A",
        "based_on": "test-manifest.json v2 (mesmas 20 páginas)",
        "reference": "referência v3: 1ª passada do autor, linha a linha, conferida no caderno",
        "size": len(pages),
        "pages": pages,
        "incomplete": missing,
        "rule": "só para medir; nunca treino, limiar, dicionário ou ajuste de rascunho",
    }
    (common.SPLITS / "test-manifest-v3.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8"
    )
    print(json.dumps({"exported": len(pages), "incomplete": missing,
                      "lines": sum(p["lines"] for p in pages.values())}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
