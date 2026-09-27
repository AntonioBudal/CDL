from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.notification import (
    NotificationItem,
    NotificationListResponse,
    NotificationReadAllResponse,
    UnreadCountResponse,
)
from app.services import notification_service
from app.services.persistence import commit_changes

router = APIRouter(prefix="/notifications", tags=["Notificações"])


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    session: DatabaseSession,
    current_user: CurrentUser,
    unread_only: Annotated[bool, Query(description="Filtrar apenas não lidas")] = False,
    limit: Annotated[int, Query(ge=1, le=100, description="Limite por página")] = 20,
    offset: Annotated[int, Query(ge=0, description="Deslocamento")] = 0,
) -> NotificationListResponse:
    """Retorna lista paginada de notificações do usuário com contagem geral de não lidas."""
    items, total, unread_count = notification_service.list_notifications(
        session=session,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    return NotificationListResponse(
        items=[notification_service.to_notification_item(item) for item in items],
        total=total,
        unread_count=unread_count,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    session: DatabaseSession,
    current_user: CurrentUser,
) -> UnreadCountResponse:
    """Endpoint leve para polling periódico (a cada 45s) de notificações pendentes."""
    count = notification_service.count_unread_notifications(
        session=session,
        user_id=current_user.id,
    )
    return UnreadCountResponse(unread_count=count)


@router.patch("/{notification_id}/read", response_model=NotificationItem)
def mark_notification_as_read(
    notification_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> NotificationItem:
    """Marca uma notificação individual como lida."""
    notif = notification_service.mark_as_read(
        session=session,
        current_user=current_user,
        notification_id=notification_id,
    )
    commit_changes(session)
    return notification_service.to_notification_item(notif)


@router.post("/read-all", response_model=NotificationReadAllResponse)
def mark_all_notifications_as_read(
    session: DatabaseSession,
    current_user: CurrentUser,
) -> NotificationReadAllResponse:
    """Marca todas as notificações pendentes do usuário atual como lidas."""
    marked_count = notification_service.mark_all_as_read(
        session=session,
        current_user=current_user,
    )
    commit_changes(session)
    return NotificationReadAllResponse(
        marked_count=marked_count,
        message=f"{marked_count} notificação(ões) marcada(s) como lida(s).",
    )
