from __future__ import annotations

from datetime import datetime
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, field_validator


class AuditLogItem(BaseModel):
    id: str
    created_at: datetime
    event_type: str
    user_id: str | None = None
    actor_username: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    details: Any = None

    @field_validator("details", mode="before")
    @classmethod
    def parse_details_json(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return v
        return v

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    items: list[AuditLogItem]
    total: int = 0
    limit: int = 50
    offset: int = 0
