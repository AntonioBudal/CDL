"""Feature 091-B (B010): registro silencioso ``leitorum-feedback/1``. Banco descartável e textos fictícios."""

from __future__ import annotations

import logging
from datetime import timedelta

from app.db.types import utc_now
from app.models.study import Study
from app.services.organizer import feedback
from feedback_harness import OTHER, OWNER, READ, SAVED, TEXT, harness, suggestion  # noqa: F401


def test_digitized_without_organizing_records_only_reading(harness):
    study = harness.study()
    assert harness.send(study, {"origin": "digitize", "organizer": None}).status_code == 204
    [row] = harness.records()
    assert (row.origin, row.reviewed, row.artifact_sha256) == ("digitize", False, "")
    doc = harness.document(study)
    assert doc["schema"] == "leitorum-feedback/1" and "organizer" not in doc
    assert doc["reading"]["lines"] == 4
    assert doc["reading"]["kinds"] == {"same": 2, "ocr": 2, "rewrite": 0, "ambiguous": 0}
    fixed = {c["target"]["id"]: c["ops"][0]["value"] for c in doc["reading"]["human_corrections"]}
    assert fixed == {"line-0": "O capítulo trata da leitura ativa.", "line-2": "Isso importa porque fixa as ideias."}
    assert row.size_bytes == len(row.payload.encode("utf-8"))


def test_digitized_and_organized_records_both_parts(harness):
    study = harness.study()
    assert harness.send(study, {"origin": "digitize", "organizer": suggestion()}).status_code == 204
    [row] = harness.records()
    assert row.reviewed is True and row.artifact_sha256 == suggestion()["engine"]["sha256"]
    doc = harness.document(study)
    organizer = doc["organizer"]
    assert organizer["outcome"] == "saved" and organizer["saved_sections"] == SAVED
    assert [u["outcome"] for u in organizer["units"]] == ["kept", "moved", "kept", "kept"]
    assert organizer["patch"] == [{"op": "replace", "path": "/segments/1/section", "value": "concepts"}]
    assert organizer["text"] == TEXT and len(organizer["segments"]) == 4
    assert "reading" in doc


def test_imported_and_organized_records_only_organizer(harness):
    study = harness.study(source="Fichamento colado de teste.")
    assert harness.send(study, {"origin": "import", "organizer": suggestion()}).status_code == 204
    doc = harness.document(study)
    assert doc["origin"] == "import" and "reading" not in doc and "organizer" in doc


def test_reverted_organization_is_kept_as_signal_but_not_reviewed(harness):
    study = harness.study()
    harness.send(study, {"origin": "digitize", "organizer": suggestion(outcome="reverted")})
    [row] = harness.records()
    assert row.reviewed is False
    organizer = harness.document(study)["organizer"]
    assert organizer["outcome"] == "reverted"
    assert not {"saved_sections", "units", "patch"} & organizer.keys()


def test_rewritten_line_is_counted_without_text(harness):
    sections = {**SAVED, "explanation": "Quem lê com perguntas na cabeça transforma o jeito de estudar o texto todo."}
    study = harness.study(source="Isso irnporta porque fixa as ideias.", sections=sections)
    harness.send(study, {"origin": "digitize", "organizer": None})
    reading = harness.document(study)["reading"]
    assert reading["kinds"]["rewrite"] + reading["kinds"]["ambiguous"] == 1
    assert reading["human_corrections"] == []


def test_paths_that_do_not_record(harness, monkeypatch):
    other_study = harness.study(OTHER)
    assert harness.send(other_study, {"origin": "digitize"}).status_code == 404

    no_source = harness.study(source="")
    assert harness.send(no_source, {"origin": "digitize"}).status_code == 204

    import_without_organizer = harness.study()
    assert harness.send(import_without_organizer, {"origin": "import"}).status_code == 204

    assert harness.send(999_999, {"origin": "digitize"}).status_code == 404
    assert harness.records() == []

    first = harness.study()
    harness.send(first, {"origin": "digitize"})
    harness.send(first, {"origin": "digitize", "organizer": suggestion()})
    [row] = harness.records()
    assert row.reviewed is False  # o segundo envio não sobrescreve

    old = harness.study()
    later = utc_now() + timedelta(minutes=11)
    monkeypatch.setattr(feedback, "utc_now", lambda: later)
    assert harness.send(old, {"origin": "digitize"}).status_code == 204
    assert len(harness.records()) == 1


def test_trashed_study_gets_404(harness):
    study = harness.study()
    with harness.factory() as session:
        session.get(Study, study).deleted_at = utc_now()
        session.commit()
    assert harness.send(study, {"origin": "digitize"}).status_code == 404


def test_invalid_bodies_are_refused(harness):
    study = harness.study()
    bad_segment = suggestion()
    bad_segment["segments"][0]["end"] = len(TEXT) + 5
    too_long = suggestion(text="a" * 50_001)
    for body in (
        {"origin": "outra"},
        {"origin": "digitize", "organizer": bad_segment},
        {"origin": "digitize", "organizer": too_long},
        {"origin": "digitize", "extra": 1},
    ):
        assert harness.send(study, body).status_code == 422
    assert harness.records() == []


def test_size_cap_drops_reading_first_then_refuses(harness, monkeypatch):
    without_reading = harness.study()
    monkeypatch.setattr(feedback, "MAX_BYTES", 300)
    harness.send(without_reading, {"origin": "digitize"})
    doc = harness.document(without_reading)
    assert "reading" not in doc and doc["origin"] == "digitize"

    refused = harness.study()
    harness.send(refused, {"origin": "import", "organizer": suggestion()})
    assert [r.study_id for r in harness.records()] == [without_reading]


def test_long_reading_is_skipped(harness):
    study = harness.study(source="\n".join(f"Linha de teste {k}." for k in range(feedback.MAX_READ_LINES + 1)))
    harness.send(study, {"origin": "digitize"})
    assert "reading" not in harness.document(study)


def test_internal_failure_keeps_study_and_records_nothing(harness, monkeypatch):
    study = harness.study()

    def broken(*_args, **_kwargs):
        raise RuntimeError("falha forçada")

    monkeypatch.setattr(feedback, "record_feedback", broken)
    assert harness.send(study, {"origin": "digitize", "organizer": suggestion()}).status_code == 204
    assert harness.records() == []
    with harness.factory() as session:
        assert session.get(Study, study).summary == SAVED["summary"]


def test_logs_carry_no_text(harness, caplog):
    study = harness.study()
    with caplog.at_level(logging.DEBUG):
        harness.send(study, {"origin": "digitize", "organizer": suggestion()})
    assert "organizer-feedback: recorded" in caplog.text
    for piece in ("leitura", "Lúcia", "Estudo de Teste", "Livro de Teste", READ.split("\n")[0]):
        assert piece not in caplog.text
