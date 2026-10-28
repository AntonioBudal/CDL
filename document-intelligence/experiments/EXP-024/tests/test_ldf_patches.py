"""EXP-024 (F03): os patches do diff são RFC 6902 válidos e aplicáveis pelo contrato LDF 2.0.

Precisa de ``leitorum_di`` (e ``jsonschema``): roda pelo ambiente principal do projeto
(``uv run pytest experiments/EXP-024/tests/test_ldf_patches.py``) e é pulado no ambiente do EXP-023.
"""

from __future__ import annotations

import sys
from pathlib import Path

import diff_signal as ds
import pytest

SRC = Path(__file__).resolve().parents[3] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
pytest.importorskip("jsonschema")
ldf = pytest.importorskip("leitorum_di.contracts.ldf")

IMAGE = {"filename": "pagina_ficticia.png", "width": 1200, "height": 1600, "sha256": "0" * 64}
WHEN = "2026-10-28T12:00:00Z"


def document(texts: list[str]) -> dict:
    lines = [
        {"bbox": [100, 100 + 80 * k, 900, 150 + 80 * k], "text": t} for k, t in enumerate(texts)
    ]
    stages = {
        "layout": {"component": ldf.component("detector-ficticio", "0.1.0")},
        "recognition": {"component": ldf.component("leitor-ficticio", "0.1.0")},
    }
    return ldf.build_document(image=IMAGE, lines=lines, regions=[], stages=stages, created_at=WHEN)


def test_reading_corrections_are_valid_ldf_and_apply():
    source = ["O capitulo trata da leitura atíva.", "Isso irnporta porque fixa as ideias."]
    saved = {
        "summary": "O capítulo trata da leitura ativa.",
        "explanation": "Isso importa porque fixa as ideias.",
    }
    doc = document(source)
    line_ids = [line["id"] for line in doc["recognition"]["lines"]]
    edits = ds.align_reading(source, saved)
    doc["human_corrections"] = ds.to_ldf_corrections(line_ids, edits, "leitor-ficticio", WHEN)
    assert len(doc["human_corrections"]) == 2
    ldf.ensure_valid(doc)
    corrected = ldf.apply_corrections(doc)
    assert [line["text"] for line in corrected["recognition"]["lines"]] == [
        saved["summary"],
        saved["explanation"],
    ]


def test_organizer_patch_applies_with_the_contract_operations():
    from leitorum_di.contracts.ldf.corrections import apply_operation

    result = {
        "schema": "organizer-result/1",
        "segments": [{"index": 0, "section": "explanation"}, {"index": 1, "section": "summary"}],
    }
    outcomes = [
        ds.UnitOutcome(0, "explanation", "explanation", "kept", 1.0),
        ds.UnitOutcome(1, "summary", "references", "moved", 1.0),
    ]
    for op in ds.to_organizer_patch(outcomes):
        apply_operation(result, op)
    assert [s["section"] for s in result["segments"]] == ["explanation", "references"]
