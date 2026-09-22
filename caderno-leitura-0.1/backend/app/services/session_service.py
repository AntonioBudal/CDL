from __future__ import annotations

from datetime import timedelta
import logging

from fastapi import Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import (
    SESSION_ACTIVITY_THROTTLE_SECONDS,
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    get_session_cookie_secure,
)
from app.core.security import generate_session_token, hash_session_token
from app.core.user_agent import parse_device_name
from app.db.types import utc_now
from app.models.user_session import UserSession
from app.schemas.auth import SessionItem

logger = logging.getLogger(__name__)


def create_session(
    session: Session,
    user_id: str,
    client_ip: str,
    user_agent: str,
) -> tuple[UserSession, str]:
    """Cria uma nova sessão no banco de dados e retorna a instância UserSession e o token opaco bruto."""
    raw_token = generate_session_token()
    token_hash = hash_session_token(raw_token)
    device_name = parse_device_name(user_agent)
    now = utc_now()
    expires_at = now + timedelta(seconds=SESSION_MAX_AGE_SECONDS)

    user_session = UserSession(
        user_id=user_id,
        session_token_hash=token_hash,
        device_name=device_name,
        ip_address=client_ip or "127.0.0.1",
        user_agent=user_agent or "",
        created_at=now,
        last_activity=now,
        expires_at=expires_at,
    )
    session.add(user_session)
    session.flush()
    return user_session, raw_token


def get_session_by_token(session: Session, raw_token: str) -> UserSession | None:
    """Busca a sessão pelo token bruto, valida expiração e renova last_activity com throttling."""
    if not raw_token or not raw_token.strip():
        return None

    token_hash = hash_session_token(raw_token.strip())
    user_session = session.scalar(
        select(UserSession).where(UserSession.session_token_hash == token_hash)
    )
    if user_session is None:
        return None

    now = utc_now()
    if user_session.expires_at <= now:
        logger.info("Sessão %s expirada em %s", user_session.id, user_session.expires_at)
        return None

    # Mecanismo de Janela Deslizante (Sliding Window) com throttle
    delta_seconds = (now - user_session.last_activity).total_seconds()
    if delta_seconds >= SESSION_ACTIVITY_THROTTLE_SECONDS:
        user_session.last_activity = now
        user_session.expires_at = now + timedelta(seconds=SESSION_MAX_AGE_SECONDS)
        session.flush()

    return user_session


def get_user_sessions(
    session: Session,
    user_id: str,
    current_session_id: str | None = None,
) -> list[SessionItem]:
    """Retorna todas as sessões ativas do usuário formatadas como SessionItem."""
    now = utc_now()
    stmt = (
        select(UserSession)
        .where(UserSession.user_id == user_id, UserSession.expires_at > now)
        .order_by(UserSession.last_activity.desc())
    )
    sessions = session.scalars(stmt).all()
    return [
        SessionItem(
            id=s.id,
            device_name=s.device_name,
            ip_address=s.ip_address,
            created_at=s.created_at,
            last_activity=s.last_activity,
            expires_at=s.expires_at,
            is_current=(s.id == current_session_id),
        )
        for s in sessions
    ]


def revoke_session(session: Session, user_id: str, session_id: str) -> bool:
    """Revoga uma sessão específica pertencente ao usuário. Retorna False se não pertencer ou não existir."""
    user_session = session.scalar(
        select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == user_id,
        )
    )
    if user_session is None:
        return False

    session.delete(user_session)
    session.flush()
    return True


def revoke_all_other_sessions(
    session: Session,
    user_id: str,
    current_session_id: str,
) -> int:
    """Revoga todas as demais sessões ativas do usuário exceto a sessão corrente."""
    stmt = (
        delete(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.id != current_session_id,
        )
    )
    result = session.execute(stmt)
    session.flush()
    return result.rowcount or 0


def delete_expired_sessions(session: Session) -> int:
    """Purga sessões expiradas no banco de dados."""
    now = utc_now()
    stmt = delete(UserSession).where(UserSession.expires_at <= now)
    result = session.execute(stmt)
    session.flush()
    return result.rowcount or 0


def resolve_cookie_secure(request: Request | None = None) -> bool:
    """Determina a flag Secure com base nas configurações ou no protocolo da requisição."""
    explicit = get_session_cookie_secure()
    if explicit is not None:
        return explicit
    if request is not None:
        proto = request.headers.get("x-forwarded-proto", "").lower()
        if proto == "https" or request.url.scheme == "https":
            return True
    return False


def set_session_cookie(
    response: Response,
    raw_token: str,
    request: Request | None = None,
) -> None:
    """Aplica o cookie seguro caderno_session na resposta HTTP."""
    secure = resolve_cookie_secure(request)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=raw_token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        path="/",
        secure=secure,
    )


def clear_session_cookie(
    response: Response,
    request: Request | None = None,
) -> None:
    """Instrui a remoção do cookie caderno_session no navegador."""
    secure = resolve_cookie_secure(request)
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
        secure=secure,
    )
