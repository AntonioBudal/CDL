"""T001 (modo só texto) — lê a exportação Markdown do Leitorum (``raw/exp-027/export/*.md`` ou
``.zip``) e separa, por estudo, o texto **bruto do motor** ("Resposta Original de Importação",
exportado com a opção de incluir a resposta original) e o texto **revisado** (Resumo, Explicação,
Conceitos Principais, Referências e Conexões, Minhas Anotações). Grava, fora do Git:

- ``processed/exp-027/motor/pNN.json`` — linhas do motor no formato do ``run_motor.py`` (sem caixas);
- ``raw/exp-027/referencia/pNN.txt`` — texto revisado como referência **provisória** (só se ainda não
  existir um ``pNN.txt`` escrito à mão), com ``draft_source: export`` na classificação;
- ``processed/exp-027/manifest.json`` — ids, hash do texto bruto, contagens.

Nenhum texto sai no console: só contagens. A ordem ``pNN`` é a ordem dos estudos no arquivo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from paths import CLASSIFICATION, EXPORT, MANIFEST, MOTOR_OUT, REFERENCE, page_id

SOURCE_HEADING = "Resposta Original de Importação"
REVISED_HEADINGS = (
    "Resumo",
    "Explicação",
    "Conceitos Principais",
    "Referências e Conexões",
    "Minhas Anotações",
)
FOOTNOTE = re.compile(r"\[\^\d+\]")  # notas de destaques injetadas na exportação
HIGHLIGHT_MARKS = re.compile(r"==|\*\*|__")


def load_markdown() -> tuple[str, str]:
    """Conteúdo do primeiro ``.md`` em ``export/`` (dentro de um ``.zip``, se for o caso)."""
    for path in sorted(EXPORT.iterdir()):
        if path.suffix.lower() == ".md":
            return path.name, path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                names = [n for n in archive.namelist() if n.lower().endswith(".md")]
                if names:
                    return f"{path.name}:{names[0]}", archive.read(names[0]).decode("utf-8")
    raise SystemExit(f"nenhum .md em {EXPORT}")


def split_studies(markdown: str) -> list[dict[str, str]]:
    """Estudos (``### título``) com as seções (``#### nome``) de cada um; títulos não são guardados."""
    studies: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    section: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        if current is not None and section is not None:
            current[section] = "\n".join(buffer).strip()

    for raw in markdown.splitlines():
        line = raw.rstrip()
        if line.startswith("### ") and not line.startswith("#### "):
            flush()
            current = {}
            studies.append(current)
            section, buffer = None, []
        elif line.startswith("#### "):
            flush()
            section, buffer = line[5:].strip(), []
        elif line.startswith("## ") or line.startswith("# "):
            flush()
            current, section, buffer = None, None, []
        elif section is not None:
            buffer.append(line)
    flush()
    return studies


def clean(text: str) -> str:
    text = FOOTNOTE.sub("", text)
    text = HIGHLIGHT_MARKS.sub("", text)
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parser da exportação Markdown do Leitorum")
    parser.add_argument("--expect", type=int, default=50)
    parser.add_argument(
        "--force-reference", action="store_true", help="sobrescreve pNN.txt existentes"
    )
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    name, markdown = load_markdown()
    studies = split_studies(markdown)
    with_source = [s for s in studies if s.get(SOURCE_HEADING, "").strip()]
    MOTOR_OUT.mkdir(parents=True, exist_ok=True)
    REFERENCE.mkdir(parents=True, exist_ok=True)
    CLASSIFICATION.mkdir(parents=True, exist_ok=True)
    pages = {}
    counts = {
        "revised_differs": 0,
        "revised_identical": 0,
        "revised_empty": 0,
        "reference_written": 0,
    }
    for index, study in enumerate(with_source, start=1):
        pid = page_id(index)
        source = clean(study[SOURCE_HEADING])
        revised = clean("\n".join(study.get(h, "") for h in REVISED_HEADINGS if study.get(h)))
        lines = [line for line in source.splitlines() if line]
        (MOTOR_OUT / f"{pid}.json").write_text(
            json.dumps(
                {
                    "schema": "exp-027-export/1",
                    "lines": [{"text": line, "confidence": None, "bbox": None} for line in lines],
                    "engine": {
                        "name": "leitorum-motor (via exportação)",
                        "source": "source_response",
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        if not revised:
            status = "revised_empty"
        elif " ".join(revised.split()) == " ".join(source.split()):
            status = "revised_identical"
        else:
            status = "revised_differs"
        counts[status] += 1
        reference = REFERENCE / f"{pid}.txt"
        if status == "revised_differs" and (args.force_reference or not reference.is_file()):
            reference.write_text(revised + "\n", encoding="utf-8")
            cls_path = CLASSIFICATION / f"{pid}.json"
            cls = json.loads(cls_path.read_text(encoding="utf-8")) if cls_path.is_file() else {}
            cls.update({"draft_source": "export", "provisional": True})
            cls_path.write_text(json.dumps(cls, ensure_ascii=False, indent=2), encoding="utf-8")
            counts["reference_written"] += 1
        pages[pid] = {
            "file": None,
            "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "motor_lines": len(lines),
            "motor_chars": len(source),
            "revised_chars": len(revised),
            "revised_status": status,
            "readable": True,
            "width": None,
            "height": None,
        }
    manifest = {
        "schema": "exp-027-manifest/1",
        "created_at": datetime.now(UTC).isoformat(),
        "order": "export_order",
        "origin": name,
        "count": len(pages),
        "expected": args.expect,
        "studies_in_file": len(studies),
        "pages": pages,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "studies_in_file": len(studies),
                "with_source": len(pages),
                "expected": args.expect,
                **counts,
                "motor_lines_total": sum(p["motor_lines"] for p in pages.values()),
            },
            ensure_ascii=False,
        )
    )
    return 0 if len(pages) == args.expect else 1


if __name__ == "__main__":
    raise SystemExit(main())
