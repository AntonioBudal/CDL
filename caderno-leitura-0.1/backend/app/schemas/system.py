from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class BackupStatus(BaseModel):
    """Backups automáticos (só para administrador); nunca traz caminhos de pasta."""

    enabled: bool
    interval_hours: float
    keep: int
    count: int
    last_at: datetime | None = None
    overdue: bool
    secondary_configured: bool


class SystemStatus(BaseModel):
    version: str
    commit: str | None = None
    schema_revision: str | None = None
    expected_schema_revisions: list[str]
    google_auth_enabled: bool
    secure_delete: bool
    backups: BackupStatus | None = None


class IntegrityResult(BaseModel):
    ok: bool
    detail: str | None = None
    checked_at: datetime
