"""F0.11.08 (spec 110): migração 0037 em banco descartável, com dados fictícios."""
from __future__ import annotations

import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config
import pytest

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID


@pytest.fixture
def at_0036(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "0036_book_isbn_publisher")
    return db, cfg


def test_upgrade_fills_weight_and_creates_table(at_0036):
    db, cfg = at_0036
    with closing(sqlite3.connect(db)) as conn:
        book = conn.execute("INSERT INTO books (title, user_id) VALUES ('Livro de Teste', ?)", (DEFAULT_OWNER_ID,)).lastrowid
        chapter = conn.execute("INSERT INTO chapters (book_id, name) VALUES (?, 'Capítulo 1')", (book,)).lastrowid
        study = conn.execute(
            "INSERT INTO studies (chapter_id, title, summary, user_id) VALUES (?, 'Estudo de Teste', 'Resumo.', ?)",
            (chapter, DEFAULT_OWNER_ID),
        ).lastrowid
        for rating in ("hard", "medium", "easy", None):
            conn.execute(
                "INSERT INTO study_highlights (study_id, user_id, section, selected_text, kind, last_rating) "
                "VALUES (?, ?, 'summary', 'trecho', 'question', ?)",
                (study, DEFAULT_OWNER_ID, rating),
            )
        conn.commit()
    command.upgrade(cfg, "head")
    with closing(sqlite3.connect(db)) as conn:
        weights = [row[0] for row in conn.execute("SELECT difficulty_weight FROM study_highlights ORDER BY id")]
        assert weights == [0.75, 0.5, 0.25, None]
        conn.execute("INSERT INTO concept_reviews (user_id, concept_key) VALUES (?, 'mimese')", (DEFAULT_OWNER_ID,))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO concept_reviews (user_id, concept_key) VALUES (?, 'mimese')", (DEFAULT_OWNER_ID,))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO concept_reviews (user_id, concept_key, last_rating) VALUES (?, 'catarse', 'urgente')",
                (DEFAULT_OWNER_ID,),
            )
        conn.commit()
    command.downgrade(cfg, "0036_book_isbn_publisher")
    with closing(sqlite3.connect(db)) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(study_highlights)")}
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "difficulty_weight" not in columns and "concept_reviews" not in tables
