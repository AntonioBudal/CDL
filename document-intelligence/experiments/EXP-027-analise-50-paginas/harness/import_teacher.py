"""Importa transcrições de um "professor" externo (ex.: respostas do Gemini coladas em ``.txt``)
como sistema ``processed/exp-027/<system>/pNN.json``, no formato de linhas do motor. A resposta
original fica intocada em ``raw/exp-027/<system>/``; a ferramenta de transcrição pode usá-la como
rascunho (``--teacher <system>``) e o ``score.py --system <system>`` a pontua contra a referência
corrigida à mão.

Formato aceito nos ``.txt``: blocos iniciados por uma linha ``=== pNN ===`` (ou só ``pNN``), com uma
linha por linha do caderno; um prefixo ``NN:`` ou ``NN.`` numérico no começo da linha é removido.
Vários blocos por arquivo e vários arquivos são aceitos; o último bloco de cada página vale.
Nenhum texto sai no console: só contagens.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime

from paths import PROCESSED, RAW

HEADER = re.compile(r"^\s*(?:=+\s*)?(p\d{2})\s*(?:=+\s*)?$", re.IGNORECASE)
NUMBERED = re.compile(r"^\s*\d{1,3}\s*[:.)\-]\s?")
FENCE = re.compile(r"^\s*```")


def parse_blocks(text: str) -> dict[str, list[str]]:
    pages: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.replace("\r\n", "\n").split("\n"):
        if FENCE.match(raw):
            continue
        header = HEADER.match(raw)
        if header:
            current = header.group(1).lower()
            pages[current] = []
            continue
        if current is None:
            continue
        line = NUMBERED.sub("", raw).strip()
        if line:
            pages[current].append(line)
    return {pid: lines for pid, lines in pages.items() if lines}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Importar transcrições de um professor externo")
    parser.add_argument("--system", default="gemini")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    source_dir = RAW / args.system
    files = sorted(source_dir.glob("*.txt")) if source_dir.is_dir() else []
    if not files:
        print(f"nenhum .txt em {source_dir}")
        return 2
    pages: dict[str, list[str]] = {}
    for path in files:
        pages.update(parse_blocks(path.read_text(encoding="utf-8")))
    out_dir = PROCESSED / args.system
    out_dir.mkdir(parents=True, exist_ok=True)
    for pid, lines in pages.items():
        (out_dir / f"{pid}.json").write_text(
            json.dumps(
                {
                    "schema": "exp-027-teacher/1",
                    "system": args.system,
                    "imported_at": datetime.now(UTC).isoformat(),
                    "lines": [{"text": line, "confidence": None, "bbox": None} for line in lines],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "files": len(files),
                "pages": len(pages),
                "ids": sorted(pages),
                "lines_total": sum(len(v) for v in pages.values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
