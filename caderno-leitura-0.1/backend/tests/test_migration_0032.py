"""Feature 090-C (C031): migração 0032 sobe e desce em banco descartável, preservando as mídias da 0031."""

from __future__ import annotations

import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID


def columns(db) -> set[str]:
    with closing(sqlite3.connect(db)) as conn:
        return {row[1] for row in conn.execute("PRAGMA table_info(encrypted_media)")}


def test_upgrade_and_downgrade_keep_existing_media(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "0031_encrypted_media")
    assert "completed_seen_at" not in columns(db)

    with closing(sqlite3.connect(db)) as conn:  # o dono padrão é criado pelas próprias migrações
        conn.execute(
            "INSERT INTO encrypted_media (id, user_id, kind, status, byte_size, plain_size, width, height, "
            "content_type, format_version, key_epoch, sha256) VALUES "
            "('6f1c0000-0000-4000-8000-000000000000', ?, 'cover', 'active', 10, 8, 1, 1, 'image/webp', 1, 0, 'x')",
            (DEFAULT_OWNER_ID,),
        )
        conn.commit()

    command.upgrade(cfg, "head")
    assert "completed_seen_at" in columns(db)
    command.downgrade(cfg, "0031_encrypted_media")
    assert "completed_seen_at" not in columns(db)
    command.upgrade(cfg, "head")
    with closing(sqlite3.connect(db)) as conn:
        rows = conn.execute("SELECT id, byte_size, completed_seen_at FROM encrypted_media").fetchall()
    assert rows == [("6f1c0000-0000-4000-8000-000000000000", 10, None)]
