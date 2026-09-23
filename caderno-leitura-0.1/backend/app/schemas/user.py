from __future__ import annotations

from datetime import datetime

from app.schemas.common import OutputModel


class UserRead(OutputModel):
    id: str
    username: str
    email: str | None = None
    display_name: str
    role: str = "user"
    status: str
    created_at: datetime
    has_password: bool = False
    has_google: bool = False
