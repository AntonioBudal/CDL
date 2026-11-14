"""F0.11.11 (spec 113): migração 0039 sobe e desce em banco descartável."""
from __future__ import annotations

import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config
import pytest

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID


def test_synthesis_notebooks_table(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "head")
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("INSERT INTO synthesis_notebooks (user_id, title) VALUES (?, 'Síntese de Teste')", (DEFAULT_OWNER_ID,))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO synthesis_notebooks (user_id, title) VALUES (?, '   ')", (DEFAULT_OWNER_ID,))
        row = conn.execute("SELECT body, version, deleted_at FROM synthesis_notebooks").fetchone()
        conn.commit()
    assert row == ("", 1, None)
    command.downgrade(cfg, "0038_receiver_tokens")
    with closing(sqlite3.connect(db)) as conn:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "synthesis_notebooks" not in tables
