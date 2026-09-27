from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select, update, delete
from sqlalchemy.orm import Session, joinedload

from app.db.types import utc_now
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationActorRead, NotificationItem

logger = logging.getLogger(__name__)


def to_notification_item(notif: Notification) -> NotificationItem:
    """Converte o modelo SQLAlchemy Notification para o schema Pydantic NotificationItem."""
    actor_read: NotificationActorRead | None = None
    if notif.actor is not None:
        avatar_url = (
            notif.actor.profile.avatar_url
            if hasattr(notif.actor, "profile") and notif.actor.profile
            else None
        )
        actor_read = NotificationActorRead(
            id=notif.actor.id,
            username=notif.actor.username,
            display_name=notif.actor.display_name or notif.actor.username,
            avatar_url=avatar_url,
        )

    return NotificationItem(
        id=notif.id,
        user_id=notif.user_id,
        actor=actor_read,
        event_type=notif.event_type,  # type: ignore[arg-type]
        payload=notif.payload or {},
        read_at=notif.read_at,
        created_at=notif.created_at,
    )


def create_notification(
    session: Session,
    user_id: str,
    event_type: str,
    actor_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> Notification | None:
    """Cria uma nova notificação de forma desacoplada e resiliente.

    Trata falhas com captura defensiva para não interromper a transação da operação principal (FR-010).
    """
    try:
        notif = Notification(
            user_id=user_id,
            actor_id=actor_id,
            event_type=event_type,
            payload=payload or {},
            created_at=utc_now(),
        )
        session.add(notif)
        session.flush()
        return notif
    except Exception as exc:
        logger.error(
            "Falha ao registrar notificação para user_id=%s, event_type=%s: %s",
            user_id,
            event_type,
            exc,
            exc_info=True,
        )
        return None


def count_unread_notifications(session: Session, user_id: str) -> int:
    """Retorna a contagem exata de notificações pendentes de leitura de um usuário."""
    stmt = (
        select(func.count(Notification.id))
        .where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )
    )
    return session.scalar(stmt) or 0


def list_notifications(
    session: Session,
    user_id: str,
    unread_only: bool = False,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Notification], int, int]:
    """Retorna a lista paginada de notificações do usuário, o total de registros e o total de não lidas."""
    base_conditions = [Notification.user_id == user_id]
    if unread_only:
        base_conditions.append(Notification.read_at.is_(None))

    # Total de registros conforme o filtro aplicado
    count_stmt = select(func.count(Notification.id)).where(*base_conditions)
    total = session.scalar(count_stmt) or 0

    # Total de não lidos absoluto do usuário
    unread_count = count_unread_notifications(session, user_id)

    # Consulta dos itens com eager loading do ator e seu perfil
    query = (
        select(Notification)
        .options(
            joinedload(Notification.actor).joinedload(User.profile),
        )
        .where(*base_conditions)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list(session.scalars(query).all())

    return items, total, unread_count


def mark_as_read(session: Session, current_user: User, notification_id: str) -> Notification:
    """Marca uma notificação individual como lida com o timestamp UTC atual.

    Operação idempotente: se já estiver lida, preserva o timestamp original sem erro.
    """
    notif = session.scalar(
        select(Notification)
        .options(joinedload(Notification.actor).joinedload(User.profile))
        .where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    if notif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada.",
        )

    if notif.read_at is None:
        notif.read_at = utc_now()
        session.flush()

    return notif


def mark_all_as_read(session: Session, current_user: User) -> int:
    """Marca todas as notificações não lidas do usuário como lidas."""
    now = utc_now()
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.read_at.is_(None),
        )
        .values(read_at=now)
    )
    result = session.execute(stmt)
    session.flush()
    return result.rowcount or 0


def broadcast_system_alert(
    session: Session,
    current_admin: User,
    title: str,
    message: str,
    severity: str = "info",
    link: str | None = None,
) -> int:
    """Dispara um comunicado institucional (system_alert) individual para todos os usuários ativos."""
    active_user_ids = list(
        session.scalars(
            select(User.id).where(User.status == "ativo")
        ).all()
    )

    now = utc_now()
    payload = {
        "title": title.strip(),
        "message": message.strip(),
        "severity": severity,
        "link": link.strip() if link else None,
    }

    notifications = [
        Notification(
            user_id=uid,
            actor_id=current_admin.id,
            event_type="system_alert",
            payload=payload,
            created_at=now,
        )
        for uid in active_user_ids
    ]

    session.add_all(notifications)
    session.flush()
    logger.info(
        "Alerta institucional emitido por @%s para %d usuários ativos",
        current_admin.username,
        len(notifications),
    )
    return len(notifications)


def purge_expired_notifications(session: Session, retention_days: int = 60) -> int:
    """Remove notificações que já foram lidas e foram criadas há mais de retention_days dias."""
    cutoff = utc_now() - timedelta(days=retention_days)
    stmt = (
        delete(Notification)
        .where(
            Notification.read_at.is_not(None),
            Notification.created_at < cutoff,
        )
    )
    result = session.execute(stmt)
    session.flush()
    purged = result.rowcount or 0
    logger.info("Purga de notificações concluída: %d registros lidos removidos", purged)
    return purged
