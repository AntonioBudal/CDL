"""EXP-044 — ingere linhas da TraPrInq (zip de exportação do Transkribus: imagens + PAGE XML) no
catálogo, lendo direto do zip, sem extrair tudo. Ambiente do subprojeto.

Regra de limpeza (a mesma para todas as linhas, critérios de transcrição da TraPrInq):
* fora: linha com caractere fora do dicionário do leitor (abreviaturas com macron, ꝯ, ꝑ, ¶…);
* fora: linha com ``_`` (texto riscado ou ilegível) ou ``??`` (dúvida de leitura);
* texto mantido como transcrito (grafia, acentos e maiúsculas do manuscrito).

Uso: ``python traprinq.py --zip Training_Set_Model9.zip [--inspect]``
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

import page
import pick
from PIL import Image

from tools.catalogo import Catalog

WORK = Path("D:/Leitorum-DI/trabalho/exp-044")
FOLDER = WORK / "traprinq"
SOURCE = "zenodo-traprinq"
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")


def clean_reason(text: str, charset: set[str]) -> str | None:
    if "_" in text or "??" in text:
        return "duvida_ou_riscado"
    if not pick.groups.valid_text(text, charset):
        return "fora_do_dicionario"
    return None


def pairs(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    """(xml, imagem) pelo nome-base; o XML do Transkribus fica em ``<doc>/page/<nome>.xml``."""
    names = archive.namelist()
    images = {}
    for name in names:
        if name.lower().endswith(IMAGE_EXT):
            folder = name.rsplit("/", 1)[0] if "/" in name else ""
            images[(folder, Path(name).stem)] = name
    out = []
    for name in names:
        if not name.lower().endswith(".xml") or "/page/" not in f"/{name}":
            continue
        folder = name.rsplit("/page/", 1)[0] if "/page/" in name else ""
        image = images.get((folder, Path(name).stem))
        if image:
            out.append((name, image))
    return sorted(out)


def document_of(xml_name: str) -> str:
    return xml_name.rsplit("/page/", 1)[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True)
    parser.add_argument("--inspect", action="store_true", help="só conta, não ingere")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    charset = pick.groups.load_charset(Path("D:/Leitorum-DI/trabalho/exp-031p/charset.json"))
    archive = zipfile.ZipFile(FOLDER / args.zip)
    found = pairs(archive)
    reasons, docs, lines_total, added = Counter(), set(), 0, 0
    cat = None if args.inspect else Catalog()
    try:
        for number, (xml_name, image_name) in enumerate(found, 1):
            doc = page.parse(archive.read(xml_name))
            docs.add(document_of(xml_name))
            image = None
            for line in doc["lines"]:
                lines_total += 1
                reason = clean_reason(line["text"], charset)
                reasons[reason or "aceita"] += 1
                if reason or cat is None:
                    continue
                if image is None:
                    image = Image.open(io.BytesIO(archive.read(image_name))).convert("L")
                out = io.BytesIO()
                image.crop(page.box(line["points"])).save(out, "PNG")
                result = cat.ingest_line(
                    SOURCE,
                    f"{args.zip}/{xml_name}#{line['id']}",
                    image=out.getvalue(),
                    text=line["text"],
                    url=f"https://zenodo.org/records/13986218#{args.zip}/{xml_name}",
                    script="manuscript",
                    split="train",
                    language="pt",
                    acquired_via="exp-044",
                    extra={"document": document_of(xml_name)},
                )
                added += result.created
            if image is not None:
                image.close()
            if cat is not None and number % 20 == 0:
                cat.flush()
                print(f"{number}/{len(found)} páginas, {added} linhas novas", flush=True)
    finally:
        if cat is not None:
            cat.flush()
            cat.close()
    report = {
        "zip": args.zip,
        "pages": len(found),
        "documents": len(docs),
        "lines": lines_total,
        "reasons": dict(reasons),
        "added": added,
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    log = FOLDER / "ingestao.json"
    previous = json.loads(log.read_text(encoding="utf-8")) if log.is_file() else {}
    previous[args.zip + (":inspecao" if args.inspect else "")] = report
    log.write_text(json.dumps(previous, ensure_ascii=False, indent=1), "utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
