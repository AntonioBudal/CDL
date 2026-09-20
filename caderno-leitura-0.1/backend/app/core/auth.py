from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import (
    DEFAULT_OWNER_DISPLAY_NAME,
    DEFAULT_OWNER_ID,
    DEFAULT_OWNER_USERNAME,
)
from app.models.user import User

logger = logging.getLogger(__name__)


def is_valid_uuid(val: str) -> bool:
    """Verifica se a string informada é um UUID válido."""
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def get_user_by_id(session: Session, user_id: str) -> User | None:
    """Busca um usuário pelo seu identificador primário."""
    return session.scalar(select(User).where(User.id == user_id))


def get_user_by_username(session: Session, username: str) -> User | None:
    """Busca um usuário pelo seu username."""
    return session.scalar(select(User).where(User.username == username))


def get_or_create_default_owner(session: Session) -> User:
    """Retorna o usuário proprietário canônico ou o provisiona caso não exista."""
    owner = get_user_by_id(session, DEFAULT_OWNER_ID)
    if owner is None:
        owner = get_user_by_username(session, DEFAULT_OWNER_USERNAME)

    if owner is None:
        logger.info("Provisionando proprietário canônico padrão: %s", DEFAULT_OWNER_USERNAME)
        owner = User(
            id=DEFAULT_OWNER_ID,
            username=DEFAULT_OWNER_USERNAME,
            display_name=DEFAULT_OWNER_DISPLAY_NAME,
            status="ativo",
        )
        session.add(owner)
        session.flush()
    return owner
