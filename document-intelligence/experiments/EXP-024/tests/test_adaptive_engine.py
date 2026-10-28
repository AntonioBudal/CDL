"""EXP-024 (F03): motor adaptativo e travas anti-regressão. Só dados fictícios."""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from functools import cache
from pathlib import Path

import adaptive_ocr_corrector as aoc
import adaptive_organizer as ao
import pytest
import safety_gate
import simulator as sim
import state as st
import streams

HARNESS = Path(__file__).resolve().parents[1] / "harness"


@cache
def engine_with_history(profile: str = "P4", pages: int = 12, regime: str = "R1"):
    engine = ao.AdaptiveOrganizer()
    reader = aoc.AdaptiveReader(engine.state_for)
    user = f"u-{profile}-val"
    times = []
    for page in streams.stream(profile, "val")["adapt"][:pages]:
        fb, _truth = sim.session(
            page,
            regime,
            lambda text, layout, book: engine.organize(user, text, layout, book),  # noqa: B023
            lambda lines, book: reader.correct_lines(user, book, [ln["text"] for ln in lines]),  # noqa: B023
        )
        start = time.perf_counter()
        engine.learn(fb)
        times.append((time.perf_counter() - start) * 1000)
        reader.learn(fb)
    return engine, reader, user, times


def segments_of(result):
    return [(s["start"], s["end"], s["section"], s["review"]) for s in result["segments"]]


# --- âncora e invariantes ------------------------------------------------------------------------


def sample_pages():
    st_ = streams.stream("P3", "val")
    return st_["adapt"][:3] + st_["holdout"][st_["books"][0]][:2]


def test_static_mode_reproduces_exp023_v4():
    engine = ao.AdaptiveOrganizer()
    base = sim.static_organizer()
    for page in sample_pages():
        text, _labels, _units = streams.page_text(page)
        layout = streams.layout(page)
        ours = engine.organize("u-x", text, layout, page["book_id"], adaptive=False)
        theirs = base.organize(text, layout)
        assert segments_of(ours) == [
            (s["start"], s["end"], s["section"], s["review"]) for s in theirs["segments"]
        ]


def test_fresh_user_equals_static():
    engine = ao.AdaptiveOrganizer()
    for page in sample_pages():
        text, _labels, _units = streams.page_text(page)
        layout = streams.layout(page)
        fresh = engine.organize("u-novo", text, layout, page["book_id"])
        static = engine.organize("u-novo", text, layout, page["book_id"], adaptive=False)
        assert segments_of(fresh) == segments_of(static)


def test_organizer_never_rewrites_text():
    engine, _reader, user, _times = engine_with_history()
    for page in sample_pages():
        text, _labels, _units = streams.page_text(page)
        result = engine.organize(user, text, streams.layout(page), page["book_id"])
        covered = []
        for seg in result["segments"]:
            covered.extend(range(seg["start"], seg["end"]))
            assert text[seg["start"] : seg["end"]] in result["sections"][seg["section"]]
        assert covered == sorted(set(covered))  # sem sobreposição
        assert all(text[k].isspace() for k in range(len(text)) if k not in set(covered))


def test_learning_is_deterministic():
    first = st.dumps(engine_with_history()[0].state_for("u-P4-val"))
    engine_with_history.cache_clear()
    second = st.dumps(engine_with_history()[0].state_for("u-P4-val"))
    assert first == second


# --- custo, isolamento e travas ------------------------------------------------------------------


def test_incremental_update_is_fast():
    _engine, _reader, _user, times = engine_with_history()
    assert statistics.median(times[2:]) < 25.0  # p95 medido na F04 (H5)


def test_users_are_isolated():
    engine, _reader, user, _times = engine_with_history()
    assert engine.state_for(user)["updates"] > 0
    other = engine.state_for("u-outro")
    assert other["updates"] == 0 and other["organizer"]["user"]["version"] == 0
    page = sample_pages()[0]
    text, _labels, _units = streams.page_text(page)
    assert segments_of(engine.organize("u-outro", text, None, page["book_id"])) == segments_of(
        engine.organize("u-outro", text, None, page["book_id"], adaptive=False)
    )


def test_projection_keeps_weights_near_the_anchor():
    engine, _reader, user, _times = engine_with_history()
    o = engine.state_for(user)["organizer"]
    assert safety_gate.frobenius(o["delta_W"], o["delta_b"]) <= engine.params["delta_max"] + 1e-9


def destructive(engine, user, gate_params):
    """Rótulos absurdos (tudo em Referências, peso enorme) sobre páginas de resumo e conceito."""
    engine.params.update(gate_params)
    state = engine.state_for(user)
    before = json.dumps(state["organizer"]["delta_W"])
    page = streams.stream("P3", "val")["adapt"][0]
    text, _labels, _units = streams.page_text(page)
    units, vecs, xs = engine.analyse(state, text, None, page["book_id"])
    report = engine.learn_labels(
        state, page["book_id"], units, vecs, xs, [3] * len(units), [50.0] * len(units)
    )
    return report, before, json.dumps(state["organizer"]["delta_W"])


def test_shadow_gate_rolls_back_a_destructive_update():
    engine = ao.AdaptiveOrganizer({"replay": False, "eps_step": 0.05, "delta_max": 50.0})
    report, before, after = destructive(engine, "u-alvo", {})
    assert not report["accepted"] and report["reason"] in ("step_regression", "total_regression")
    assert before == after
    assert engine.state_for("u-alvo")["organizer"]["behaviour"]["rejected_updates"] == 1


def test_without_gate_the_same_update_goes_through():
    engine = ao.AdaptiveOrganizer({"replay": False, "shadow": False, "delta_max": 50.0})
    report, before, after = destructive(engine, "u-alvo", {})
    assert report["accepted"] and before != after


def test_replay_gate_rejects_update_against_the_users_own_corrections():
    engine, _reader, user, _times = engine_with_history("P3", 10)
    engine.params.update({"shadow": False, "delta_max": 50.0})
    assert engine.state_for(user)["organizer"]["replay"]
    report, before, after = destructive(engine, user, {})
    assert not report["accepted"] and report["reason"] == "replay_regression" and before == after


@pytest.mark.parametrize(
    ("kwargs", "gated"),
    [
        (
            {"reverted": True, "rating": None, "corrections": 3, "blind": False, "retention": 1.0},
            True,
        ),
        (
            {"reverted": False, "rating": 1, "corrections": 0, "blind": False, "retention": 1.0},
            True,
        ),
        (
            {"reverted": False, "rating": 1, "corrections": 2, "blind": False, "retention": 1.0},
            False,
        ),
        (
            {"reverted": False, "rating": None, "corrections": 0, "blind": True, "retention": 1.0},
            False,
        ),
    ],
)
def test_reward_gating(kwargs, gated):
    weights = safety_gate.page_weights(**kwargs, params=ao.DEFAULTS)
    assert weights.gated == gated
    if kwargs["blind"]:
        assert weights.keep == ao.DEFAULTS["keep_blind"]
    if kwargs["rating"] == 1 and not gated:
        assert (
            weights.keep == 0.0 and weights.moved == 1.0
        )  # nota baixa não anula correção explícita


# --- estado, E4, leitura -------------------------------------------------------------------------


def test_state_roundtrip_and_size():
    engine, _reader, user, _times = engine_with_history()
    text = st.dumps(engine.state_for(user))
    assert st.dumps(st.loads(text)) == text
    assert st.size_bytes(engine.state_for(user)) < 512 * 1024


def test_click_redecodes_with_the_clicked_unit_fixed():
    engine = ao.AdaptiveOrganizer()
    page = streams.stream("P1", "val")["adapt"][3]
    text, _labels, _units = streams.page_text(page)
    result = engine.organize("u-clique", text, streams.layout(page), page["book_id"])
    index = result["review_order"][0]
    target = next(s for s in ao.SECTIONS if s != result["segments"][index]["section"])
    after = engine.click(result, index, target)
    assert after["segments"][index]["section"] == target
    assert not after["segments"][index]["review"]
    local = engine.click(after, index, target, local=True)
    assert local["segments"][index]["section"] == target
    assert engine.state_for("u-clique")["updates"] == 0  # o passo local não mexe no estado salvo


def test_reader_restores_accents_and_protects_known_words():
    engine = ao.AdaptiveOrganizer()
    reader = aoc.AdaptiveReader(engine.state_for)
    state = engine.state_for("u-leitura")
    lexicon = state["reading"]["lexicon"]["books"].setdefault("b-teste", {})
    lexicon["acao"] = {"ação": 5.0}
    lexicon["hermeneutica"] = {"hermenêutica": 4.0}
    lexicon["coragem"] = {"coragem": 6.0}
    assert (
        reader.correct_line("u-leitura", "b-teste", "a acao e a hermeneutica")
        == "a ação e a hermenêutica"
    )
    assert reader.correct_line("u-leitura", "b-teste", "coragem") == "coragem"
    assert (
        reader.correct_line("u-outro", "b-teste", "acao") == "acao"
    )  # léxico de outro usuário não vale


def test_reader_learning_yields_curated_pairs_and_confusions():
    _engine, reader, user, _times = engine_with_history("P1", 12)
    state = reader.state_for(user)
    assert state["reading"]["confusions"]
    assert any(name.endswith(">ç") for name in state["reading"]["confusions"])  # W1 troca ç por c


def test_engine_modules_do_not_import_numpy():
    code = (
        f"import sys; sys.path.insert(0, r'{HARNESS}');"
        "import adaptive_organizer, adaptive_ocr_corrector, safety_gate, diff_signal, state;"
        "print('numpy' in sys.modules)"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "False"
