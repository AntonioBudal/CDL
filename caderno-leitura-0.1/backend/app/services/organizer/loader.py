"""Carga do artefato do organizador e operação de organização (feature 089); sem acesso ao banco.

O artefato ``organizer-v1.json`` vem do EXP-023 e tem o SHA-256 fixado aqui. É carregado uma vez por
processo, sob lock. Se estiver ausente ou não conferir, a função fica indisponível e o resto do backend
segue igual. Nunca registra o texto organizado em log.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from app.services.organizer import engine

ARTIFACT = Path(__file__).resolve().parents[2] / "data" / "organizer" / "organizer-v1.json"
EXPECTED_SHA256 = "60d6538de49495e4bfc01e00f048d5f4c0d1e55a7a84d6df33de9fee99c40d28"
VERSION = "1"
MAX_CHARS = 50_000
MAX_UNITS = 400

logger = logging.getLogger("leitorum.organizer")

WARNING_MESSAGES = {
    "suggestion": "Distribuição automática: confira as seções antes de salvar.",
    "single_section": "A sugestão colocou todo o texto numa só seção.",
}

_lock = threading.Lock()
_state: dict[str, Any] | None = None


class OrganizeError(Exception):
    def __init__(self, status: int, code: str, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.code = code
        self.detail = detail


def _load() -> dict[str, Any]:
    global _state
    with _lock:
        if _state is not None:
            return _state
        path = ARTIFACT
        if not path.is_file():
            _state = {"available": False, "reason": "not_installed"}
        else:
            try:
                body = path.read_bytes()
                if hashlib.sha256(body).hexdigest() != EXPECTED_SHA256:
                    raise ValueError("SHA-256")
                model = engine.Model.from_json(json.loads(body.decode("utf-8")))
                _state = {"available": True, "reason": None, "organizer": engine.Organizer(model)}
            except (OSError, ValueError, KeyError, TypeError):
                _state = {"available": False, "reason": "integrity_failed"}
        if not _state["available"]:
            logger.warning("organizer: indisponível (%s)", _state["reason"])
        return _state


def reset_cache() -> None:
    global _state
    with _lock:
        _state = None


def status() -> dict[str, Any]:
    state = _load()
    return {"available": state["available"], "reason": state["reason"], "version": VERSION if state["available"] else None}


def organize(text: str, lines: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Sugere a distribuição de ``text`` nas 4 seções; levanta ``OrganizeError`` nos limites do contrato."""
    started = time.perf_counter()
    if not text.strip():
        raise OrganizeError(422, "empty_text", "Não há texto para organizar.")
    if len(text) > MAX_CHARS:
        raise OrganizeError(413, "too_large", "O texto é longo demais para organizar de uma vez (máximo de 50 000 caracteres).")
    state = _load()
    if not state["available"]:
        raise OrganizeError(503, "unavailable", "A organização automática não está disponível nesta instalação.")
    organizer: engine.Organizer = state["organizer"]
    options = engine.Options()
    units, _lines, vecs, xs = organizer.analyse(text, lines or None, options)
    if len(units) > MAX_UNITS:
        raise OrganizeError(413, "too_large", "O texto tem trechos demais para organizar de uma vez (máximo de 400).")
    result = organizer.decide(units, vecs, xs, options)
    segments = [
        {
            "index": s["index"],
            "start": s["start"],
            "end": s["end"],
            "text": text[s["start"]:s["end"]],
            "section": s["section"],
            "confidence": s["confidence"],
            "review": s["review"],
        }
        for s in result["segments"]
    ]
    codes = ["suggestion"]
    if len({s["section"] for s in segments}) == 1 and len(segments) > 1:
        codes.append("single_section")
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    logger.info("organizer: %d trechos, %d ms", len(segments), elapsed_ms)
    return {
        "sections": result["sections"],
        "segments": segments,
        "explicit_headings": result["explicit_headings"],
        "review_count": sum(s["review"] for s in segments),
        "engine": {"name": "leitorum-organizer", "version": VERSION, "sha256": EXPECTED_SHA256},
        "elapsed_ms": elapsed_ms,
        "warnings": [{"code": c, "message": WARNING_MESSAGES[c]} for c in codes],
    }
