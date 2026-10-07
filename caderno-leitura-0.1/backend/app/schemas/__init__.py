"""Modelos de entrada e saida da API."""

from app.schemas.inbox_capture import (
    InboxCaptureCreate,
    InboxCapturePatch,
    InboxCaptureRead,
    InboxCountResponse,
    InboxLinkRequest,
    InboxPromoteRequest,
    InboxStatus,
)
from app.schemas.notification import (
    NotificationActorRead,
    NotificationBroadcastRequest,
    NotificationBroadcastResponse,
    NotificationEventType,
    NotificationItem,
    NotificationListResponse,
    NotificationPurgeResponse,
    NotificationReadAllResponse,
    UnreadCountResponse,
)

__all__ = [
    "InboxCaptureCreate",
    "InboxCapturePatch",
    "InboxCaptureRead",
    "InboxCountResponse",
    "InboxLinkRequest",
    "InboxPromoteRequest",
    "InboxStatus",
    "NotificationActorRead",
    "NotificationBroadcastRequest",
    "NotificationBroadcastResponse",
    "NotificationEventType",
    "NotificationItem",
    "NotificationListResponse",
    "NotificationPurgeResponse",
    "NotificationReadAllResponse",
    "UnreadCountResponse",
]
