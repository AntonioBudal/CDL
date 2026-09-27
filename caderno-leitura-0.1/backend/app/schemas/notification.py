from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

NotificationEventType = Literal[
    "friend_request",
    "friend_accepted",
    "study_shared",
    "system_alert",
]


class NotificationActorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    display_name: str
    avatar_url: str | None = None


class NotificationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    actor: NotificationActorRead | None = None
    event_type: NotificationEventType
    payload: dict[str, Any] = Field(default_factory=dict)
    read_at: datetime | None = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationItem]
    total: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class NotificationReadAllResponse(BaseModel):
    marked_count: int
    message: str


class NotificationBroadcastRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    message: str = Field(..., min_length=2, max_length=2000)
    severity: Literal["info", "warning", "critical"] = "info"
    link: str | None = Field(default=None, max_length=500)


class NotificationBroadcastResponse(BaseModel):
    dispatched_count: int
    message: str


class NotificationPurgeResponse(BaseModel):
    purged_count: int
    retention_days: int
    message: str
