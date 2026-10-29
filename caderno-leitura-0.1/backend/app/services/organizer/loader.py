"""Carga do artefato do organizador e operação de organização (features 089 e 091); sem acesso ao banco.

O artefato ``organizer-v2.json`` vem do EXP-025 (ADR-011): o v1 do EXP-023 congelado mais 4 pistas fixas de
referência, lidas do próprio artefato por ``engine_v2``. Tem o SHA-256 fixado aqui. É carregado uma vez por
processo, sob lock. Se estiver ausente ou não conferir, a função fica indisponível e o resto do backend
segue igual. Nunca registra o texto organizado em log.

Com o estado de um usuário (feature 091-C, só com o adaptador ligado e liberado por ``adapter_service``), a
sugestão vem do adaptador sobre o mesmo artefato; sem estado, é o v2 puro.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from app.services.organizer import adapter, engine, engine_v2

ARTIFACT = Path(__file__).resolve().parents[2] / "data" / "organizer" / "organizer-v2.json"
EXPECTED_SHA256 = "9f6530a32726d593142b7a2de3bce3efc1c0095abf3a91335364db6343978aee"
VERSION = "2"
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
                organizer = engine_v2.from_artifact(json.loads(body.decode("utf-8")))
                _state = {
                    "available": True,
                    "reason": None,
                    "organizer": organizer,
                    "adapter": adapter.AdapterV2(organizer, EXPECTED_SHA256),
                }
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


def adapter_engine() -> adapter.AdapterV2 | None:
    """O adaptador sobre o artefato carregado (feature 091-C), ou ``None`` se o organizador estiver indisponível."""
    state = _load()
    return state["adapter"] if state["available"] else None


def organize(
    text: str,
    lines: list[dict[str, Any]] | None = None,
    user_state: dict | None = None,
    adapter_count: int | None = None,
) -> dict[str, Any]:
    """Sugere a distribuição de ``text`` nas 4 seções; levanta ``OrganizeError`` nos limites do contrato.

    ``user_state`` (o estado do adaptador do usuário) só chega quando o adaptador está ligado e liberado; então
    ``adapter_count`` (estudos revisados) vai em ``engine.adapter``.
    """
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
    if user_state is None:
        units, _lines, vecs, xs = organizer.analyse(text, lines or None, options)
    else:
        units, vecs, xs = state["adapter"].analyse(user_state, text, lines, None)
    if len(units) > MAX_UNITS:
        raise OrganizeError(413, "too_large", "O texto tem trechos demais para organizar de uma vez (máximo de 400).")
    if user_state is None:
        result = organizer.decide(units, vecs, xs, options)
    else:
        probs = state["adapter"].probabilities(xs, state["adapter"].weights(user_state))
        result = organizer.decide(units, vecs, xs, options, probs=probs)
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
        "engine": {
            "name": "leitorum-organizer",
            "version": VERSION,
            "sha256": EXPECTED_SHA256,
            "adapter": adapter_count if user_state is not None else None,
        },
        "elapsed_ms": elapsed_ms,
        "warnings": [{"code": c, "message": WARNING_MESSAGES[c]} for c in codes],
    }
