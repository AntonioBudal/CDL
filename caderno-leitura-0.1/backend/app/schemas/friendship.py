from __future__ import annotations

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict


class FriendUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None


class FriendItem(BaseModel):
    friendship_id: int
    user: FriendUserRead
    since: datetime


class FriendRequestItem(BaseModel):
    request_id: int
    user: FriendUserRead
    direction: Literal["sent", "received"]
    created_at: datetime


class FriendRequestsResponse(BaseModel):
    received: list[FriendRequestItem]
    sent: list[FriendRequestItem]


class FriendBlockedItem(BaseModel):
    friendship_id: int
    user: FriendUserRead
    blocked_at: datetime


class FriendsSummaryResponse(BaseModel):
    friends_count: int
    pending_received_count: int
    pending_sent_count: int


class FriendshipStatusResponse(BaseModel):
    relation_status: Literal[
        "none",
        "pending_sent",
        "pending_received",
        "friends",
        "blocked_by_me",
        "blocked_by_them",
    ]
    request_id: int | None = None
    since: datetime | None = None


class FriendshipActionResponse(BaseModel):
    ok: bool = True
    message: str
    status: Literal["none", "pending", "accepted", "blocked"]
