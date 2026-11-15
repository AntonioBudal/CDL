"""F0.12.02 (spec 115): migração 0040 sobe e desce em banco descartável."""
from __future__ import annotations

import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config

from app.core.config import BACKEND_DIR


def test_published_at_column(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "head")
    with closing(sqlite3.connect(db)) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(studies)")}
        indexes = {row[1] for row in conn.execute("PRAGMA index_list(studies)")}
    assert "published_at" in columns and "ix_studies_published_at" in indexes
    command.downgrade(cfg, "0039_synthesis_notebooks")
    with closing(sqlite3.connect(db)) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(studies)")}
    assert "published_at" not in columns
