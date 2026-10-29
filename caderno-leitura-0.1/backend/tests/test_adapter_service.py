"""Feature 091-C (C013): adaptador dormente por usuário. Banco descartável e textos fictícios do fixture de paridade."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import pytest

from app.core.config import get_organizer_adapter_enabled
from app.models.organizer_feedback import OrganizerFeedback, OrganizerUserState
from app.services.organizer import adapter, adapter_service, adapter_state, loader
from feedback_harness import OTHER, OWNER, harness  # noqa: F401

STEPS = json.loads(
    (Path(__file__).with_name("fixtures") / "adapter-parity-v2.json").read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
)["steps"]
PAGE = (
    "O capítulo trata de um tema de teste e apresenta a ideia central do autor fictício.\n"
    "Isso importa porque mostra se o texto vai para a seção certa, ou seja, se a regra funciona.\n"
    "- A margem e o centro — Lúcia Dantas"
)


def study_from(harness, step: dict, uid: str = OWNER) -> int:
    """Estudo fictício com as seções salvas do passo do fixture (páginas de validação do EXP-024)."""
    organizer = step["document"]["organizer"]
    sections = organizer.get("saved_sections") or {"summary": "", "explanation": organizer["text"], "concepts": "", "references": ""}
    return harness.study(uid, source="\n".join(line["text"] for line in organizer["lines"]), sections=sections)


def suggestion_of(step: dict) -> dict:
    organizer = step["document"]["organizer"]
    return {
        "engine": {"version": "2", "sha256": loader.EXPECTED_SHA256, "adapter": None},
        "outcome": organizer["outcome"],
        "text": organizer["text"],
        "segments": organizer["segments"],
        "lines": organizer["lines"],
    }


def feed(harness, steps: list[dict], uid: str = OWNER) -> None:
    for step in steps:
        study = study_from(harness, step, uid)
        assert harness.send(study, {"origin": "digitize", "organizer": suggestion_of(step)}, uid).status_code == 204


def state_of(harness, uid: str = OWNER) -> OrganizerUserState | None:
    with harness.factory() as session:
        return session.get(OrganizerUserState, uid)


def organize(harness, uid: str = OWNER) -> dict:
    response = harness.client(uid).post("/api/imports/organize", json={"text": PAGE})
    assert response.status_code == 200
    return response.json()


def test_switch_is_off_by_default_and_refuses_invalid_values(monkeypatch):
    monkeypatch.delenv("LEITORUM_ORGANIZER_ADAPTER", raising=False)
    assert get_organizer_adapter_enabled() is False
    monkeypatch.setenv("LEITORUM_ORGANIZER_ADAPTER", "on")
    assert get_organizer_adapter_enabled() is True
    monkeypatch.setenv("LEITORUM_ORGANIZER_ADAPTER", "talvez")
    with pytest.raises(ValueError, match="LEITORUM_ORGANIZER_ADAPTER"):
        get_organizer_adapter_enabled()


def test_state_learns_from_every_record_even_when_switched_off(harness, monkeypatch):
    monkeypatch.delenv("LEITORUM_ORGANIZER_ADAPTER", raising=False)
    user_a = [s for s in STEPS if s["user"] == "u-a"][:5]
    feed(harness, user_a)
    stored = state_of(harness)
    state = adapter_state.loads(stored.state)
    assert stored.artifact_sha256 == loader.EXPECTED_SHA256
    assert stored.reviewed_count == state["reviewed"] == sum(s["document"]["organizer"]["outcome"] == "saved" for s in user_a)
    assert state["organizer"]["steps"] > 0
    assert organize(harness)["engine"]["adapter"] is None


def test_switched_off_keeps_v2_even_with_30_reviewed_and_a_favourable_guard(harness, monkeypatch):
    monkeypatch.delenv("LEITORUM_ORGANIZER_ADAPTER", raising=False)
    monkeypatch.setattr(adapter_service, "reviewed_count", lambda *_: 50)
    monkeypatch.setattr(adapter.AdapterV2, "guard_allows", lambda *_: True)
    feed(harness, STEPS[:2])
    body = organize(harness)
    assert body["engine"]["adapter"] is None


def test_switched_on_needs_30_reviewed_and_the_guard(harness, monkeypatch):
    monkeypatch.setenv("LEITORUM_ORGANIZER_ADAPTER", "on")
    feed(harness, [s for s in STEPS if s["user"] == "u-a"][:3])
    monkeypatch.setattr(adapter.AdapterV2, "guard_allows", lambda *_: True)
    monkeypatch.setattr(adapter_service, "reviewed_count", lambda *_: 29)
    assert organize(harness)["engine"]["adapter"] is None
    monkeypatch.setattr(adapter_service, "reviewed_count", lambda *_: 30)
    assert organize(harness)["engine"]["adapter"] == 30
    monkeypatch.setattr(adapter.AdapterV2, "guard_allows", lambda *_: False)
    assert organize(harness)["engine"]["adapter"] is None


def test_suggestion_with_state_matches_the_reference_adapter(harness, monkeypatch):
    monkeypatch.setenv("LEITORUM_ORGANIZER_ADAPTER", "on")
    feed(harness, [s for s in STEPS if s["user"] == "u-a"][:6])
    monkeypatch.setattr(adapter.AdapterV2, "guard_allows", lambda *_: True)
    monkeypatch.setattr(adapter_service, "reviewed_count", lambda *_: 30)
    state = adapter_state.loads(state_of(harness).state)
    expected = loader.adapter_engine().organize(state, PAGE)
    body = organize(harness)
    assert [(s["start"], s["end"], s["section"]) for s in body["segments"]] == [
        (s["start"], s["end"], s["section"]) for s in expected["segments"]
    ]


def test_users_are_isolated(harness, monkeypatch):
    monkeypatch.delenv("LEITORUM_ORGANIZER_ADAPTER", raising=False)
    feed(harness, [s for s in STEPS if s["user"] == "u-b"][:2], OTHER)
    before = state_of(harness, OTHER).state
    feed(harness, [s for s in STEPS if s["user"] == "u-a"][:4], OWNER)
    assert state_of(harness, OTHER).state == before
    assert state_of(harness, OWNER).state != before


def test_state_of_another_artifact_is_left_alone(harness, monkeypatch):
    monkeypatch.setenv("LEITORUM_ORGANIZER_ADAPTER", "on")
    feed(harness, STEPS[:1])
    with harness.factory() as session:
        session.get(OrganizerUserState, OWNER).artifact_sha256 = "outro-artefato"
        session.commit()
    frozen = state_of(harness).state
    feed(harness, [s for s in STEPS if s["user"] == "u-a"][1:3])
    assert state_of(harness).state == frozen
    monkeypatch.setattr(adapter_service, "reviewed_count", lambda *_: 99)
    monkeypatch.setattr(adapter.AdapterV2, "guard_allows", lambda *_: True)
    assert organize(harness)["engine"]["adapter"] is None


def test_reverted_and_misaligned_records_do_not_teach(harness):
    reverted = json.loads(json.dumps(STEPS[0]))
    reverted["document"]["organizer"]["outcome"] = "reverted"
    reverted["document"]["organizer"].pop("saved_sections", None)
    feed(harness, [reverted])
    state = adapter_state.loads(state_of(harness).state)
    assert state["organizer"]["behaviour"]["reverted"] == 1 and state["organizer"]["steps"] == 0

    no_lines = json.loads(json.dumps([s for s in STEPS if s["user"] == "u-a"][1]))
    study = study_from(harness, no_lines)
    body = suggestion_of(no_lines)
    body.pop("lines")
    harness.send(study, {"origin": "digitize", "organizer": body})
    state = adapter_state.loads(state_of(harness).state)
    assert state["organizer"]["steps"] == 0  # sem as linhas, a página com layout não realinha


def test_learning_failure_keeps_the_record(harness, monkeypatch):
    def broken(*_args, **_kwargs):
        raise RuntimeError("falha forçada")

    monkeypatch.setattr(adapter.AdapterV2, "learn", broken)
    study = study_from(harness, STEPS[0])
    assert harness.send(study, {"origin": "digitize", "organizer": suggestion_of(STEPS[0])}).status_code == 204
    assert [r.study_id for r in harness.records()] == [study]
    assert state_of(harness) is None


def test_update_cost_and_state_size(harness):
    """SC-005: p95 da atualização ≤ 150 ms e estado ≤ 1 MB, em 200 registros fictícios (o fluxo em ciclo)."""
    engine = loader.adapter_engine()
    state = engine.new_state("u-custo")
    times = []
    for k in range(200):
        step = STEPS[k % len(STEPS)]
        t0 = time.perf_counter()
        engine.learn(state, step["document"], f"{step['book_id']}-{k // len(STEPS)}")
        times.append((time.perf_counter() - t0) * 1000)
    assert sorted(times)[int(0.95 * len(times)) - 1] <= 150
    assert len(adapter_state.dumps(state).encode("utf-8")) <= adapter_service.MAX_STATE_BYTES


def test_oversized_state_drops_lightest_books(monkeypatch):
    engine = loader.adapter_engine()
    state = engine.new_state("u-grande")
    for k, step in enumerate(STEPS[:12]):
        engine.learn(state, step["document"], f"livro-{k}")
    full = len(adapter_state.dumps(state).encode("utf-8"))
    monkeypatch.setattr(adapter_service, "MAX_STATE_BYTES", full - 1)
    text, pruned = adapter_service._fit(state)
    assert pruned and len(text.encode("utf-8")) < full
    assert state["organizer"]["user"]["counts"]  # o escopo do leitor fica


def test_logs_and_state_carry_no_text(harness, caplog):
    with caplog.at_level(logging.DEBUG):
        feed(harness, [s for s in STEPS if s["user"] == "u-a"][:3])
    assert "adaptador: learned" in caplog.text or "adaptador: gated" in caplog.text
    stored = state_of(harness).state
    import re

    words = {w for s in STEPS[:6] for w in re.findall(r"[^\W\d_]{6,}", s["document"]["organizer"]["text"])}
    structure = adapter_state.dumps(loader.adapter_engine().new_state("x"))
    for word in words - {w for w in words if w in structure}:
        assert word not in stored
        assert word not in caplog.text
    with harness.factory() as session:
        assert session.query(OrganizerFeedback).count() == 3
