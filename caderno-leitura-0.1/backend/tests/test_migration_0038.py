"""F0.11.09 (spec 111): migração 0038 sobe e desce em banco descartável; o token sai junto com a conta."""
from __future__ import annotations

import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config
import pytest

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID


def test_receiver_tokens_table(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "head")
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "INSERT INTO receiver_tokens (user_id, token_hash, token_hint) VALUES (?, ?, 'lt_abcd')",
            (DEFAULT_OWNER_ID, "a" * 64),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO receiver_tokens (user_id, token_hash, token_hint) VALUES (?, ?, 'lt_abcd')",
                (DEFAULT_OWNER_ID, "b" * 64),
            )
        conn.commit()
        columns = {row[1] for row in conn.execute("PRAGMA table_info(receiver_tokens)")}
    assert columns == {"user_id", "token_hash", "token_hint", "created_at", "last_used_at"}
    command.downgrade(cfg, "0037_review_difficulty_concepts")
    with closing(sqlite3.connect(db)) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "receiver_tokens" not in tables
