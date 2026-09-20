"""Schemas Pydantic para operações de backup, manifesto e restauração."""
from pydantic import BaseModel, Field


class BackupCounts(BaseModel):
    books: int = 0
    chapters: int = 0
    studies: int = 0
    covers: int = 0


class BackupManifestSchema(BaseModel):
    app_version: str
    schema_version: str | None = None
    created_at: str
    generator: str = "Caderno de Leitura Backup Engine"
    counts: BackupCounts = Field(default_factory=BackupCounts)
    files: dict[str, str] = Field(default_factory=dict)


class RestoreResultResponse(BaseModel):
    success: bool = True
    message: str
    backup_created_at: str | None = None
    pre_restore_snapshot: str
    schema_revision: str | None = None
    counts: dict[str, int] = Field(default_factory=dict)
    covers_restored: int = 0


class SnapshotInspectionResponse(BaseModel):
    snapshot_path: str
    created_at: str
    file_size_bytes: int
    schema_revision: str | None = None
    integrity_ok: bool
    counts: dict[str, int] = Field(default_factory=dict)
