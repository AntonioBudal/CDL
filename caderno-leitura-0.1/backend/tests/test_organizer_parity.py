"""Features 089 e 091, portão: o organizador do produto reproduz o EXP-025 em todos os casos de paridade.

O fixture v2 vem de ``document-intelligence/experiments/EXP-025/harness/export_parity.py`` (páginas fictícias
do EXP-023 e do EXP-024, MIT). Igualdade exata de trechos, seções e cabeçalhos explícitos.

O fixture v1 (``EXP-023/harness/export_parity.py``) fica para a não regressão: onde nenhuma pista nova dispara,
o v2 é idêntico ao v1 (ADR-011).
"""

import hashlib
import json
from pathlib import Path

import pytest

from app.services.organizer import engine_v2, loader

FIXTURES = Path(__file__).with_name("fixtures")
FIXTURE = FIXTURES / "organizer-parity-v2.json"
FIXTURE_SHA256 = "6726ddc4ce9049ec45f393fe84ef9412d70068cbb0c49819ade91e5713b71573"
FIXTURE_V1 = FIXTURES / "organizer-parity-v1.json"
FIXTURE_V1_SHA256 = "db3f3a3819dd5492db75c0838a50d5ccbca76ac6fc882177fed4e6b041c45609"
V1_ARTIFACT_SHA256 = "60d6538de49495e4bfc01e00f048d5f4c0d1e55a7a84d6df33de9fee99c40d28"


def read_fixture(path: Path, sha256: str) -> dict:
    body = path.read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(body).hexdigest() == sha256
    return json.loads(body.decode("utf-8"))


def organized(case: dict) -> dict:
    result = loader.organize(case["text"], case["lines"])
    return {
        "segments": [{k: s[k] for k in ("start", "end", "text", "section", "confidence", "review")} for s in result["segments"]],
        "sections": result["sections"],
        "explicit_headings": result["explicit_headings"],
    }


@pytest.fixture(scope="module")
def parity():
    data = read_fixture(FIXTURE, FIXTURE_SHA256)
    assert data["artifact_sha256"] == loader.EXPECTED_SHA256
    return data["cases"]


@pytest.fixture(scope="module")
def parity_v1():
    data = read_fixture(FIXTURE_V1, FIXTURE_V1_SHA256)
    assert data["artifact_sha256"] == V1_ARTIFACT_SHA256
    return data["cases"]


def test_artifact_is_available():
    loader.reset_cache()
    assert loader.status() == {"available": True, "reason": None, "version": "2"}


def test_parity_with_experiment_in_every_case(parity):
    assert len(parity) == 192
    mismatches = [case["id"] for case in parity if organized(case) != case["expected"]]
    assert mismatches == []


def test_v2_matches_v1_wherever_no_new_cue_fires(parity_v1):
    assert len(parity_v1) == 144
    no_cue = changed_sections = changed_without_cue = 0
    for case in parity_v1:
        got = organized(case)
        fires = any(any(engine_v2.cue_values(s["text"])) for s in got["segments"])
        no_cue += not fires
        changed_sections += got["sections"] != case["expected"]["sections"]
        changed_without_cue += not fires and got != case["expected"]
    assert changed_sections == 0
    assert changed_without_cue == 0
    assert no_cue == 140
