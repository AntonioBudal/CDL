"""Importa para o catálogo as amostras aprovadas do EXP-043 (``D:\\Leitorum-
DI\\amostras\\exp-043``), pelo mesmo caminho que os conectores da E4 vão usar
(``Catalog.ingest_line``). Fontes ``PENDING_REVIEW`` já foram apagadas no fim do EXP-043; o
sintético não entra (é gerado na hora do treino).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .catalog import Catalog

HTR_UNITED_CATALOG = "https://raw.githubusercontent.com/HTR-United/htr-united/master/htr-united.yml"
SKIP = {"sintetico", "htr-united"}
STATUS = {"APPROVED": "APPROVED", "APPROVED_NC": "APPROVED", "EXPERIMENT_ONLY": "EXPERIMENT_ONLY"}


def conditions_of(license_name: str | None, status: str | None) -> list[str]:
    """Condições a partir do nome da licença, por palavra inteira.

    ``CC-BY-NC-SA-4.0`` → by, sa, nc.
    """
    text = (license_name or "").upper()
    tokens = set(re.split(r"[^A-ZÃÇ]+", text))
    out = []
    if "BY" in tokens:
        out.append("by")
    if "SA" in tokens:
        out.append("sa")
    if "NC" in tokens or status == "APPROVED_NC" or "NÃO COMERCIAL" in text:
        out.append("nc")
    return out


def era_of(value) -> str | None:
    if isinstance(value, dict):
        return f"{value.get('notBefore', '?')}-{value.get('notAfter', '?')}"
    return value


def language_of(value) -> str | None:
    return ",".join(value) if isinstance(value, list) else value


def import_samples(catalog: Catalog, samples: Path) -> dict:
    catalog_yml = next((samples / "htr-united" / "arquivos").glob("*.yml"), None)
    report = {}
    for manifest in sorted(samples.glob("*/manifesto.jsonl")):
        folder = manifest.parent.name
        if folder in SKIP:
            continue
        rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
        rows = [r for r in rows if r.get("status") in STATUS]
        if not rows:
            continue
        first = rows[0]
        teklia = not folder.startswith("htr-united-")
        source_id = ("teklia-" if teklia else "htru-") + folder.removesuffix("-line").removeprefix(
            "htr-united-"
        ).lower()
        if teklia:
            terms_file = samples / folder / "arquivos" / f"{first.get('terms_sha256')}.termos"
            terms, terms_url = (
                (terms_file.read_bytes(), first.get("terms_url"))
                if terms_file.is_file()
                else (None, None)
            )
            name = f"{first['source'].split('/')[1]} (Teklia, Hugging Face)"
        else:
            terms = catalog_yml.read_bytes() if catalog_yml else None
            terms_url = HTR_UNITED_CATALOG
            name = first["source"].replace("HTR-United/", "") + " (HTR-United)"
        status = STATUS[first["status"]]
        conditions = conditions_of(first.get("license"), first.get("status"))
        catalog.add_source(
            source_id,
            name=name,
            url=first["source_url"],
            license=first.get("license"),
            conditions=conditions,
            status=status,
            access="api" if teklia else "download",
            terms=terms,
            terms_url=terms_url,
            notes="importado do EXP-043 (amostra); licença conferida na fonte original",
        )
        created = existing = refused = 0
        native_ids = set()
        for row in rows:
            native = f"{row.get('split', 'train')}-{row['row_index']}" if teklia else row["sha256"]
            native_ids.add(native)
            url = (
                f"{row['source_url']}#{native}"
                if teklia
                else f"{row.get('page_url')}#line-{row['sha256'][:12]}"
            )
            image = (samples / folder / "arquivos" / row["file"]).read_bytes()
            result = catalog.ingest_line(
                source_id,
                native,
                image=image,
                text=row.get("text"),
                url=url,
                language=language_of(row.get("language")),
                era=era_of(row.get("era")),
                script="manuscript",
                split=row.get("split") if teklia else None,
                acquired_via="exp-043",
                conditions=conditions,
            )
            if result.created:
                created += 1
            elif result.reason == "ja_existe":
                existing += 1
            else:
                refused += 1
        report[source_id] = {
            "manifest_rows": len(rows),
            "unique": len(native_ids),
            "created": created,
            "existing": existing,
            "refused": refused,
        }
    return report
