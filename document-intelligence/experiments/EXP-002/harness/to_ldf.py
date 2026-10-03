"""Conversão da saída de layout para o LDF 1.0 e validação contra o JSON Schema versionado.

Correspondência aprovada (plan.md): ``title`` → bloco ``heading``; ``paragraph`` → ``paragraph``;
``margin_note`` → ``margin_note``; ``graphic_box`` → ``structure.diagrams[]``.

Lacuna conhecida: no LDF 1.0, ``diagrams[]`` não tem campo para a região (bbox) do diagrama — só nós
e arestas com bbox próprias. A região do ``graphic_box`` não pode ser representada sem alterar o
contrato; ela é devolvida à parte em ``gaps`` para o relatório. Linhas vêm sem texto (o EXP-002 não
reconhece texto) e com ``confidence`` 0.
"""

from __future__ import annotations

import json
import uuid
from functools import cache
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "ldf-1.0.schema.json"
BLOCK_TYPE = {"title": "heading", "paragraph": "paragraph", "margin_note": "margin_note"}
NAMESPACE = uuid.UUID("6f1c2a52-0b6e-4f5f-9d3a-2b7c5a1e0e02")


@cache
def _validator() -> jsonschema.Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator_class = jsonschema.validators.validator_for(schema)
    return validator_class(schema, format_checker=jsonschema.FormatChecker())


def _ints(values) -> list[int]:
    return [round(float(v)) for v in values]


def to_ldf(
    page: dict[str, Any], prediction: dict[str, Any], detector: str, elapsed_ms: float = 0.0
) -> tuple[dict[str, Any], list[str]]:
    """Monta o documento LDF de uma página; devolve ``(documento, lacunas)``."""
    gaps: list[str] = []
    lines = []
    line_ids = []
    for index, line in enumerate(prediction.get("lines", []), start=1):
        line_id = f"line_{index:03d}"
        line_ids.append((line_id, line["bbox"]))
        item = {
            "id": line_id,
            "bbox": _ints(line["bbox"]),
            "text": "",
            "confidence": 0.0,
            "is_handwritten": True,
        }
        if line.get("polygon"):
            item["polygon"] = [_ints(point) for point in line["polygon"]]
        lines.append(item)

    def members(bbox) -> list[str]:
        x0, y0, x1, y1 = bbox
        found = []
        for line_id, (lx0, ly0, lx1, ly1) in line_ids:
            cx, cy = (lx0 + lx1) / 2, (ly0 + ly1) / 2
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                found.append(line_id)
        return found

    blocks, diagrams = [], []
    for index, block in enumerate(prediction.get("blocks", []), start=1):
        if block["type"] == "graphic_box":
            diagrams.append({"id": f"diagram_{index:03d}", "nodes": [], "edges": []})
            gaps.append(f"diagram_{index:03d}: região {_ints(block['bbox'])} sem campo no LDF 1.0")
            continue
        item = {
            "id": f"block_{index:03d}",
            "type": BLOCK_TYPE[block["type"]],
            "bbox": _ints(block["bbox"]),
            "line_ids": members(block["bbox"]),
        }
        if "score" in block:
            item["confidence"] = max(0.0, min(1.0, float(block["score"])))
        blocks.append(item)

    document = {
        "ldf_version": "1.0.0",
        "document_id": str(uuid.uuid5(NAMESPACE, page["id"])),
        "created_at": "2026-10-02T00:00:00Z",
        "source_image": {
            "filename": Path(page["image"]).name,
            "width": int(page["width"]),
            "height": int(page["height"]),
            "sha256": page["sha256"],
        },
        "pipeline_metadata": {
            "model_versions": {"layout": detector},
            "processing_time_ms": max(0, round(elapsed_ms)),
        },
        "recognition": {"lines": lines},
        "structure": {"reading_order": [], "blocks": blocks, "diagrams": diagrams},
        "semantics": {"sections": [], "entities": []},
        "human_corrections": [],
    }
    return document, gaps


def validation_errors(document: dict[str, Any]) -> list[str]:
    """Mensagens de erro de validação contra o JSON Schema do LDF 1.0 (lista vazia = válido)."""
    return [
        f"{'/'.join(str(p) for p in error.absolute_path)}: {error.message}"
        for error in _validator().iter_errors(document)
    ]
