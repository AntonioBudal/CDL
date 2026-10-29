"""EXP-025, F05: adaptador enxuto sobre o v2 (E1 + E2 + gating). Só dados fictícios."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1] / "harness"
EXPS = HARNESS.parents[1]
for path in (HARNESS, EXPS / "EXP-023" / "harness", EXPS / "EXP-024" / "harness"):
    if str(path) not in sys.path:
        sys.path.append(str(path))

import adapter_v2 as av  # noqa: E402
import adaptive_organizer as ao  # noqa: E402  (EXP-024)
import feedback_doc  # noqa: E402
import organizer_v2 as v2  # noqa: E402
import safety_gate  # noqa: E402  (EXP-024)
import simulator as sim  # noqa: E402  (EXP-024)
import state as st  # noqa: E402  (EXP-024)
import streams  # noqa: E402  (EXP-024)

ART = HARNESS.parent / "artifacts"
THRESHOLDS = EXPS / "EXP-024" / "artifacts" / "thresholds.json"


@pytest.fixture(scope="module")
def adapter():
    sha = (ART / "organizer-v2.sha256").read_text(encoding="utf-8").strip()
    return av.AdapterV2(v2.load(), sha)


def documents(adapter, profile: str, n: int, regime: str = "R1", state=None):
    """Páginas fictícias de validação do EXP-024, sugeridas pelo adaptador e salvas."""
    stream = streams.stream(profile, "val")
    out = []
    for page in stream["adapt"][:n]:
        seen = {}

        def organize(text, layout, book, seen=seen):
            seen["result"] = adapter.organize(state, text, layout, book)
            return seen["result"]

        feedback, _truth = sim.session(page, regime, organize)
        out.append(
            (feedback_doc.to_document(feedback, seen["result"]["segments"]), page["book_id"])
        )
    return out


def test_params_are_the_frozen_ones_of_exp024():
    frozen = {**ao.DEFAULTS, **json.loads(THRESHOLDS.read_text(encoding="utf-8"))["organizer"]}
    assert {k: frozen[k] for k in av.PARAMS} == av.PARAMS


def test_empty_state_matches_v2_in_every_parity_case(adapter):
    cases = json.loads((ART / "parity-v2.json").read_text(encoding="utf-8"))["cases"]
    state = adapter.new_state("u-teste")
    for case in cases:
        result = adapter.organize(state, case["text"], case["lines"])
        got = [
            {
                **{k: s[k] for k in ("start", "end", "section", "confidence", "review")},
                "text": case["text"][s["start"] : s["end"]],
            }
            for s in result["segments"]
        ]
        assert got == case["expected"]["segments"], case["id"]
        assert result["sections"] == case["expected"]["sections"], case["id"]


def test_learning_is_deterministic_and_isolated(adapter):
    docs = documents(adapter, "P1", 12)
    a1, a2, b = (adapter.new_state(u) for u in ("u-a", "u-a", "u-b"))
    before_b = st.dumps(b)
    codes = [adapter.learn(a1, doc, book) for doc, book in docs]
    for doc, book in docs:
        adapter.learn(a2, doc, book)
    assert st.dumps(a1) == st.dumps(a2)
    assert st.dumps(b) == before_b
    assert "learned" in codes
    assert a1["reviewed"] == sum(d["organizer"]["outcome"] == "saved" for d, _ in docs)


def test_reverted_and_low_retention_pages_do_not_update(adapter):
    doc, book = documents(adapter, "P2", 1)[0]
    state = adapter.new_state("u-gate")
    reverted = json.loads(json.dumps(doc))
    reverted["organizer"]["outcome"] = "reverted"
    reverted["organizer"].pop("saved_sections", None)
    assert adapter.learn(state, reverted, book) == "gated"
    lost = json.loads(json.dumps(doc))
    lost["organizer"]["saved_sections"] = dict.fromkeys(av.SECTIONS, "")
    lost["reading"]["kinds"] = {"same": 0, "ocr": 0, "rewrite": 3, "ambiguous": 0}
    assert adapter.learn(state, lost, book) == "gated"
    assert state["organizer"]["steps"] == 0
    assert state["organizer"]["behaviour"] == {
        "pages": 2,
        "reverted": 1,
        "blind": 0,
        "rejected_updates": 0,
    }


def test_misaligned_page_does_not_learn(adapter):
    doc, book = documents(adapter, "P3", 1)[0]
    shifted = json.loads(json.dumps(doc))
    shifted["organizer"]["segments"][0]["end"] -= 1
    assert adapter.learn(adapter.new_state("u-m"), shifted, book) == "misaligned"


def test_projection_keeps_delta_inside_the_radius(adapter):
    state = adapter.new_state("u-proj")
    for doc, book in documents(adapter, "P4", 30) * 3:
        adapter.learn(state, doc, book)
    o = state["organizer"]
    assert safety_gate.frobenius(o["delta_W"], o["delta_b"]) <= av.PARAMS["delta_max"] + 1e-9


def test_guard_needs_ten_measures_and_compares_with_v2(adapter):
    state = adapter.new_state("u-guarda")
    assert adapter.guard_allows(state) is False
    state["guard"] = {"adapter": [0.9] * 9, "static": [0.5] * 9}
    assert adapter.guard_allows(state) is False
    state["guard"] = {"adapter": [0.9] * 10, "static": [0.5] * 10}
    assert adapter.guard_allows(state) is True
    state["guard"] = {"adapter": [0.4] * 20, "static": [0.5] * 20}
    assert adapter.guard_allows(state) is False


def test_state_carries_no_page_text(adapter):
    docs = documents(adapter, "P1", 10)
    state = adapter.new_state("u-priv")
    for doc, book in docs:
        adapter.learn(state, doc, book)
    dumped = st.dumps(state)
    structure = st.dumps(adapter.new_state("u-priv"))  # nomes de chave (ex.: "references")
    words = {w for doc, _ in docs for w in re.findall(r"[^\W\d_]{6,}", doc["organizer"]["text"])}
    words = {w for w in words if w not in structure}
    assert words and not [w for w in words if w in dumped]
    assert hashlib.sha256(dumped.encode("utf-8")).hexdigest()
