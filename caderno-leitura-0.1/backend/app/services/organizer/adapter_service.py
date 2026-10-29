"""Estado do adaptador do organizador por usuário, no banco (feature 091-C).

- ``update_after_feedback``: depois de cada registro ``leitorum-feedback/1`` gravado, aplica o ``learn`` do adaptador
  ao estado do usuário (``organizer_user_state``), sob um lock por usuário e numa transação curta. Sempre, mesmo
  com o adaptador desligado: o estado e a guarda ficam prontos para um experimento futuro.
- ``user_state_for_suggestion``: o estado que a sugestão pode usar, ou ``None``. Só com
  ``LEITORUM_ORGANIZER_ADAPTER=on``, 30 ou mais registros revisados, o estado no artefato atual e a guarda favorável.
  Com a chave desligada (padrão), não lê o banco e a sugestão é o v2 puro.

O estado não guarda texto (só hashes, números e formas de linha abstratas). Logs só com códigos, contagens e tempos.
"""

from __future__ import annotations

import json
import threading
import time
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_organizer_adapter_enabled
from app.db.types import utc_now
from app.models.chapter import Chapter
from app.models.organizer_feedback import OrganizerFeedback, OrganizerUserState
from app.models.study import Study
from app.services.organizer import adapter_state, loader

ACTIVATE_AT = 30
MAX_STATE_BYTES = 1_000_000

_locks: defaultdict[str, threading.Lock] = defaultdict(threading.Lock)
_locks_guard = threading.Lock()


def _lock_for(user_id: str) -> threading.Lock:
    with _locks_guard:
        return _locks[user_id]


def reviewed_count(session: Session, user_id: str) -> int:
    return session.scalar(
        select(func.count()).select_from(OrganizerFeedback).where(
            OrganizerFeedback.user_id == user_id, OrganizerFeedback.reviewed.is_(True)
        )
    ) or 0


def _book_id(session: Session, study_id: int) -> str | None:
    book_id = session.scalar(select(Chapter.book_id).join(Study, Study.chapter_id == Chapter.id).where(Study.id == study_id))
    return str(book_id) if book_id is not None else None


def _fit(state: dict) -> tuple[str, bool]:
    """Serializa; acima do teto, tira os livros com menos peso até caber (o escopo do leitor fica)."""
    text = adapter_state.dumps(state)
    if len(text.encode("utf-8")) <= MAX_STATE_BYTES:
        return text, False
    o = state["organizer"]
    for book_id in sorted(o["books"], key=lambda b: (sum(o["books"][b]["counts"].values()), b)):
        del o["books"][book_id]
        o["ref_shapes"]["books"].pop(book_id, None)
        text = adapter_state.dumps(state)
        if len(text.encode("utf-8")) <= MAX_STATE_BYTES:
            break
    return text, True


def update_after_feedback(session: Session, row: OrganizerFeedback) -> tuple[str, int]:
    """Aprende com um registro recém-gravado; devolve o código e os ms. Grava o estado numa transação curta."""
    started = time.perf_counter()
    engine = loader.adapter_engine()
    if engine is None:
        return "unavailable", 0
    document = json.loads(row.payload)
    if not document.get("organizer"):
        return "no_organizer", 0
    with _lock_for(row.user_id):
        stored = session.get(OrganizerUserState, row.user_id)
        if stored is not None and stored.artifact_sha256 != engine.anchor_sha256:
            return "skipped_artifact", 0  # estado de outro artefato: fica até a reconstrução
        state = adapter_state.loads(stored.state) if stored is not None else engine.new_state(row.user_id)
        code = engine.learn(state, document, _book_id(session, row.study_id))
        text, pruned = _fit(state)
        if stored is None:
            stored = OrganizerUserState(user_id=row.user_id, artifact_sha256=engine.anchor_sha256, state=text)
            session.add(stored)
        stored.state = text
        stored.reviewed_count = state["reviewed"]
        stored.updated_at = utc_now()
        session.commit()
    if pruned:
        code = f"{code}+pruned_books"
    return code, round((time.perf_counter() - started) * 1000)


def user_state_for_suggestion(session: Session, user_id: str) -> tuple[dict | None, int | None]:
    """O estado que a sugestão pode usar e a contagem de revisados, ou ``(None, None)`` para o v2 puro."""
    if not get_organizer_adapter_enabled():
        return None, None
    engine = loader.adapter_engine()
    if engine is None:
        return None, None
    count = reviewed_count(session, user_id)
    if count < ACTIVATE_AT:
        return None, None
    stored = session.get(OrganizerUserState, user_id)
    if stored is None or stored.artifact_sha256 != engine.anchor_sha256:
        return None, None
    state = adapter_state.loads(stored.state)
    if not engine.guard_allows(state):
        return None, None
    return state, count


def rebuild(session: Session, user_id: str, *, execute: bool) -> dict:
    """Remonta o estado do usuário aplicando os registros em ordem de criação (FR-015); só contagens no relatório.

    Sem ``execute``, calcula e descarta (nada é gravado). Uso manual, com o serviço parado.
    """
    engine = loader.adapter_engine()
    if engine is None:
        return {"user_states": 0, "records": 0, "codes": {}, "bytes": 0, "written": False}
    state = engine.new_state(user_id)
    codes: dict[str, int] = {}
    rows = session.scalars(
        select(OrganizerFeedback)
        .where(OrganizerFeedback.user_id == user_id)
        .order_by(OrganizerFeedback.created_at, OrganizerFeedback.id)
    ).all()
    for row in rows:
        document = json.loads(row.payload)
        if not document.get("organizer"):
            code = "no_organizer"
        else:
            code = engine.learn(state, document, _book_id(session, row.study_id))
            # como na atualização incremental, que grava o estado (números com 5 casas) a cada registro
            state = adapter_state.loads(_fit(state)[0])
        codes[code] = codes.get(code, 0) + 1
    text, pruned = _fit(state)
    if execute:
        stored = session.get(OrganizerUserState, user_id)
        if stored is None:
            stored = OrganizerUserState(user_id=user_id, artifact_sha256=engine.anchor_sha256, state=text)
            session.add(stored)
        stored.artifact_sha256 = engine.anchor_sha256
        stored.state = text
        stored.reviewed_count = state["reviewed"]
        stored.updated_at = utc_now()
        session.commit()
    return {
        "user_states": 1,
        "records": len(rows),
        "codes": codes,
        "bytes": len(text.encode("utf-8")),
        "pruned_books": pruned,
        "written": execute,
    }
