from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AdminUserItem(BaseModel):
    id: str
    username: str
    display_name: str
    email: str | None = None
    role: Literal["admin", "user"]
    status: Literal["ativo", "suspenso"]
    provider: Literal["local", "google", "ambos"]
    created_at: datetime
    last_access: datetime | None = None
    studies_count: int = 0
    books_count: int = 0
    active_sessions_count: int = 0


class AdminUsersResponse(BaseModel):
    items: list[AdminUserItem]
    total: int


class AdminStatsSummary(BaseModel):
    total_users: int = 0
    active_users: int = 0
    suspended_users: int = 0
    admin_users: int = 0
    total_studies: int = 0


class AdminSuspendRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class AdminSuspendResponse(BaseModel):
    id: str
    status: Literal["suspenso"]
    sessions_revoked: int
    message: str


class AdminReactivateResponse(BaseModel):
    id: str
    status: Literal["ativo"]
    message: str


class AdminRoleUpdateRequest(BaseModel):
    role: Literal["admin", "user"]


class AdminRoleUpdateResponse(BaseModel):
    id: str
    role: Literal["admin", "user"]
    message: str


class AdminRevokeSessionsResponse(BaseModel):
    id: str
    sessions_revoked: int
    message: str
