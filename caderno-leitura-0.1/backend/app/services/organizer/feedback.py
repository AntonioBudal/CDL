"""Registro ``leitorum-feedback/1`` de um estudo recém-salvo (feature 091-B); só o banco local, nada de texto em log.

O documento é montado a partir do estudo gravado, não do cliente: as 4 seções salvas e o texto lido
(``source_response``) vêm do banco. Do navegador vem só o que o organizador sugeriu. A leitura nunca é alterada aqui
(a pós-correção automática continua desligada): as correções só ficam guardadas para curadoria futura.
"""

from __future__ import annotations

import json
from datetime import UTC, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.organizer_feedback import OrganizerFeedback
from app.models.study import Study
from app.schemas.organizer_feedback import FeedbackSuggestion, OrganizerFeedbackRequest
from app.services.organizer import feedback_signal as ds

SCHEMA = "leitorum-feedback/1"
MAX_BYTES = 256 * 1024
MAX_READ_LINES = 80  # uma página de caderno tem ~40 linhas; 400 levariam ~26 s de alinhamento
FRESH_FOR = timedelta(minutes=10)
AUTHOR = "leitor"


def _organizer_part(suggestion: FeedbackSuggestion, saved: dict[str, str]) -> dict:
    part = {
        "engine": suggestion.engine.model_dump(),
        "outcome": suggestion.outcome,
        "text": suggestion.text,
        "segments": [s.model_dump() for s in suggestion.segments],
    }
    if suggestion.lines:
        part["lines"] = [line.model_dump() for line in suggestion.lines]
    if suggestion.outcome == "saved":
        units = ds.align_units(suggestion.text, part["segments"], saved)
        part["saved_sections"] = saved
        part["units"] = [{"index": u.index, "outcome": u.outcome, "final": u.final, "ratio": u.ratio} for u in units]
        part["patch"] = ds.to_organizer_patch(units)
    return part


def _reading_part(source: str, saved: dict[str, str], timestamp: str) -> dict | None:
    lines = source.split("\n")
    if len(lines) > MAX_READ_LINES:
        return None
    edits = ds.align_reading(lines, saved)
    kinds = dict.fromkeys(("same", "ocr", "rewrite", "ambiguous"), 0)
    for edit in edits:
        kinds[edit.kind] += 1
    line_ids = [f"line-{k}" for k in range(len(lines))]
    return {
        "lines": len(edits),
        "kinds": kinds,
        "human_corrections": ds.to_ldf_corrections(line_ids, edits, AUTHOR, timestamp),
    }


def _encode(document: dict) -> bytes:
    return json.dumps(document, ensure_ascii=False, sort_keys=True).encode("utf-8")


def record_feedback(session: Session, study: Study, user_id: str, body: OrganizerFeedbackRequest) -> tuple[str, dict]:
    """Grava o registro do estudo, se couber; devolve o código e contagens para o log (nunca texto)."""
    created = study.created_at if study.created_at.tzinfo else study.created_at.replace(tzinfo=UTC)
    if utc_now() - created > FRESH_FOR:
        return "stale", {}
    if session.scalar(select(OrganizerFeedback.id).where(OrganizerFeedback.study_id == study.id)) is not None:
        return "exists", {}
    if body.origin == "digitize" and not study.source_response.strip():
        return "no_source", {}
    if body.origin == "import" and body.organizer is None:
        return "no_organizer", {}

    now = utc_now()
    timestamp = now.isoformat().replace("+00:00", "Z")
    saved = {s: getattr(study, s) or "" for s in ds.SECTIONS}
    document: dict = {"schema": SCHEMA, "created_at": timestamp, "origin": body.origin}
    if body.organizer is not None:
        document["organizer"] = _organizer_part(body.organizer, saved)
    if body.origin == "digitize":
        reading = _reading_part(study.source_response, saved, timestamp)
        if reading is not None:
            document["reading"] = reading
    payload = _encode(document)
    if len(payload) > MAX_BYTES and "reading" in document:
        del document["reading"]
        payload = _encode(document)
    if len(payload) > MAX_BYTES:
        return "too_large", {"bytes": len(payload)}

    session.add(
        OrganizerFeedback(
            user_id=user_id,
            study_id=study.id,
            schema=SCHEMA,
            origin=body.origin,
            reviewed=body.organizer is not None and body.organizer.outcome == "saved",
            artifact_sha256=body.organizer.engine.sha256 if body.organizer else "",
            payload=payload.decode("utf-8"),
            size_bytes=len(payload),
            created_at=now,
        )
    )
    session.flush()
    return "recorded", {
        "segments": len(body.organizer.segments) if body.organizer else 0,
        "corrections": len(document.get("reading", {}).get("human_corrections", [])),
        "bytes": len(payload),
    }
