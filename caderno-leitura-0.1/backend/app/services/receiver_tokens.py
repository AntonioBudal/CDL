"""F0.11.09 (spec 111): token de recepção de destaques.

Token aleatório de 32 bytes com prefixo ``lt_``; o servidor guarda só o SHA-256 (alta entropia dispensa hash lento) e
o começo do token. Um por leitor: gerar outro substitui o anterior na hora.
"""
from __future__ import annotations

import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.receiver_token import ReceiverToken
from app.models.user import User
from app.schemas.receiver import ReceiverTokenStatus
from app.services.persistence import commit_changes

PREFIX = "lt_"
HINT_LENGTH = 7  # "lt_" + 4 caracteres


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _status(row: ReceiverToken | None) -> ReceiverTokenStatus:
    if row is None:
        return ReceiverTokenStatus(active=False)
    return ReceiverTokenStatus(
        active=True, hint=row.token_hint, created_at=row.created_at, last_used_at=row.last_used_at
    )


def token_status(session: Session, user_id: str) -> ReceiverTokenStatus:
    return _status(session.get(ReceiverToken, user_id))


def issue_token(session: Session, user_id: str) -> tuple[str, ReceiverTokenStatus]:
    raw = PREFIX + secrets.token_urlsafe(32)
    row = session.get(ReceiverToken, user_id)
    if row is None:
        row = ReceiverToken(user_id=user_id, token_hash=hash_token(raw), token_hint=raw[:HINT_LENGTH])
        session.add(row)
    else:
        row.token_hash = hash_token(raw)
        row.token_hint = raw[:HINT_LENGTH]
        row.created_at = utc_now()
        row.last_used_at = None
    commit_changes(session)
    session.refresh(row)
    return raw, _status(row)


def revoke_token(session: Session, user_id: str) -> None:
    row = session.get(ReceiverToken, user_id)
    if row is not None:
        session.delete(row)
        commit_changes(session)


def authenticate(session: Session, raw: str | None) -> User | None:
    """Usuário ativo dono do token, ou ``None``. Atualiza o último uso."""
    if not raw or not raw.startswith(PREFIX) or len(raw) > 200:
        return None
    digest = hash_token(raw)
    row = session.scalar(select(ReceiverToken).where(ReceiverToken.token_hash == digest))
    if row is None or not secrets.compare_digest(row.token_hash, digest):
        return None
    user = session.get(User, row.user_id)
    if user is None or user.status != "ativo":
        return None
    row.last_used_at = utc_now()
    commit_changes(session)
    return user


def parse_authorization(header: str | None) -> str | None:
    """``Token <x>`` (Readwise) ou ``Bearer <x>``."""
    if not header:
        return None
    scheme, _, value = header.strip().partition(" ")
    if scheme.lower() not in ("token", "bearer"):
        return None
    return value.strip() or None
