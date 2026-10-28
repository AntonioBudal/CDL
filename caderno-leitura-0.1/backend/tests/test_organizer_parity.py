"""Feature 089, portão: o organizador do produto reproduz o EXP-023 em todos os casos de paridade.

O fixture vem de ``document-intelligence/experiments/EXP-023/harness/export_parity.py`` (páginas fictícias,
MIT). Igualdade exata de trechos, seções e cabeçalhos explícitos.
"""

import hashlib
import json
from pathlib import Path

import pytest

from app.services.organizer import loader

FIXTURE = Path(__file__).with_name("fixtures") / "organizer-parity-v1.json"
FIXTURE_SHA256 = "db3f3a3819dd5492db75c0838a50d5ccbca76ac6fc882177fed4e6b041c45609"


@pytest.fixture(scope="module")
def parity():
    body = FIXTURE.read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(body).hexdigest() == FIXTURE_SHA256
    data = json.loads(body.decode("utf-8"))
    assert data["artifact_sha256"] == loader.EXPECTED_SHA256
    return data["cases"]


def test_artifact_is_available():
    loader.reset_cache()
    assert loader.status() == {"available": True, "reason": None, "version": "1"}


def test_parity_with_experiment_in_every_case(parity):
    assert len(parity) == 144
    mismatches = []
    for case in parity:
        result = loader.organize(case["text"], case["lines"])
        got = {
            "segments": [{k: s[k] for k in ("start", "end", "text", "section", "confidence", "review")} for s in result["segments"]],
            "sections": result["sections"],
            "explicit_headings": result["explicit_headings"],
        }
        if got != case["expected"]:
            mismatches.append(case["id"])
    assert mismatches == []
