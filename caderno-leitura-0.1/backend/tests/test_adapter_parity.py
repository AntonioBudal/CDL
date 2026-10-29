"""Feature 091-C, portão: o adaptador do produto reproduz o do EXP-025 passo a passo (só dados fictícios).

O fixture vem de ``document-intelligence/experiments/EXP-025/harness/export_adapter_parity.py``: 40 páginas
fictícias do EXP-024, 2 usuários. Em cada passo, a sugestão antes de aprender, o código do ``learn``, a norma de ΔW
e o SHA-256 do estado serializado têm de ser os mesmos. Com o estado vazio, o adaptador é o v2.
"""

import hashlib
import json
from pathlib import Path

import pytest

from app.services.organizer import adapter, adapter_state, engine_v2, loader

FIXTURES = Path(__file__).with_name("fixtures")
FIXTURE = FIXTURES / "adapter-parity-v2.json"
FIXTURE_SHA256 = "bef19d2605d53d79fe588ebbc137efccc8263b290730bb52d1bb476a9c58bb3e"
PARITY_V2 = FIXTURES / "organizer-parity-v2.json"


def read(path: Path) -> dict:
    return json.loads(path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8"))


@pytest.fixture(scope="module")
def engine():
    data = json.loads(loader.ARTIFACT.read_text(encoding="utf-8"))
    return adapter.AdapterV2(engine_v2.from_artifact(data), loader.EXPECTED_SHA256)


@pytest.fixture(scope="module")
def parity():
    body = FIXTURE.read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(body).hexdigest() == FIXTURE_SHA256
    data = json.loads(body.decode("utf-8"))
    assert data["artifact_sha256"] == loader.EXPECTED_SHA256
    assert data["params"] == adapter.PARAMS
    return data["steps"]


def test_flow_is_reproduced_step_by_step(engine, parity):
    assert len(parity) == 40
    states = {}
    for k, step in enumerate(parity):
        state = states.setdefault(step["user"], engine.new_state(step["user"]))
        organizer = step["document"]["organizer"]
        result = engine.organize(state, organizer["text"], organizer["lines"], step["book_id"])
        got = [{key: s[key] for key in ("start", "end", "section", "confidence", "review")} for s in result["segments"]]
        assert got == step["expected_segments"], k
        assert engine.learn(state, step["document"], step["book_id"]) == step["code"], k
        o = state["organizer"]
        assert round(adapter_state.frobenius(o["delta_W"], o["delta_b"]), 6) == step["delta_norm"], k
        assert state["reviewed"] == step["reviewed"], k
        assert engine.guard_allows(state) == step["guard_allows"], k
        assert hashlib.sha256(adapter_state.dumps(state).encode("utf-8")).hexdigest() == step["state_sha256"], k


def test_empty_state_is_the_v2(engine):
    state = engine.new_state("u-teste")
    for case in read(PARITY_V2)["cases"]:
        result = engine.organize(state, case["text"], case["lines"])
        got = [
            {**{key: s[key] for key in ("start", "end", "section", "confidence", "review")}, "text": case["text"][s["start"]:s["end"]]}
            for s in result["segments"]
        ]
        assert got == case["expected"]["segments"], case["id"]
        assert result["sections"] == case["expected"]["sections"], case["id"]


def test_state_round_trips_through_json(engine, parity):
    state = engine.new_state("u-a")
    for step in parity[:6]:
        if step["user"] == "u-a":
            engine.learn(state, step["document"], step["book_id"])
    assert adapter_state.dumps(adapter_state.loads(adapter_state.dumps(state))) == adapter_state.dumps(state)
