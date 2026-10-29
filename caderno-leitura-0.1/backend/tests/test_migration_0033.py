"""Feature 091-B (B004): migração 0033 sobe e desce em banco descartável; o registro sai junto com o estudo."""

from __future__ import annotations

import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config
import pytest

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID


def tables(db) -> set[str]:
    with closing(sqlite3.connect(db)) as conn:
        return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


@pytest.fixture
def migrated(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "head")
    return db, cfg


def insert_study(conn) -> int:
    book = conn.execute("INSERT INTO books (title, user_id) VALUES ('Livro de Teste', ?)", (DEFAULT_OWNER_ID,)).lastrowid
    chapter = conn.execute("INSERT INTO chapters (book_id, name) VALUES (?, 'Capítulo 1')", (book,)).lastrowid
    return conn.execute(
        "INSERT INTO studies (chapter_id, title, summary, user_id) VALUES (?, 'Estudo de Teste', 'Resumo fictício.', ?)",
        (chapter, DEFAULT_OWNER_ID),
    ).lastrowid


def insert_feedback(conn, study_id: int) -> None:
    conn.execute(
        "INSERT INTO organizer_feedback (user_id, study_id, schema, origin, payload, size_bytes) "
        "VALUES (?, ?, 'leitorum-feedback/1', 'digitize', '{}', 2)",
        (DEFAULT_OWNER_ID, study_id),
    )


def test_upgrade_creates_both_tables_and_downgrade_removes_them(migrated):
    db, cfg = migrated
    assert {"organizer_feedback", "organizer_user_state"} <= tables(db)
    with closing(sqlite3.connect(db)) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(organizer_feedback)")}
        indexes = {row[1] for row in conn.execute("PRAGMA index_list(organizer_feedback)")}
    assert columns == {
        "id", "user_id", "study_id", "schema", "origin", "reviewed", "artifact_sha256", "payload", "size_bytes", "created_at",
    }
    assert "ix_organizer_feedback_user_reviewed" in indexes
    command.downgrade(cfg, "0032_media_completed_seen")
    assert not {"organizer_feedback", "organizer_user_state"} & tables(db)
    command.upgrade(cfg, "head")
    assert {"organizer_feedback", "organizer_user_state"} <= tables(db)


def test_one_record_per_study_and_valid_origin(migrated):
    db, _cfg = migrated
    with closing(sqlite3.connect(db)) as conn:
        study = insert_study(conn)
        insert_feedback(conn, study)
        with pytest.raises(sqlite3.IntegrityError):
            insert_feedback(conn, study)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO organizer_feedback (user_id, study_id, schema, origin, payload, size_bytes) "
                "VALUES (?, ?, 'leitorum-feedback/1', 'outra', '{}', 2)",
                (DEFAULT_OWNER_ID, insert_study(conn)),
            )


def test_deleting_the_study_deletes_its_record(migrated):
    db, _cfg = migrated
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        study = insert_study(conn)
        insert_feedback(conn, study)
        conn.commit()
        conn.execute("DELETE FROM studies WHERE id = ?", (study,))
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM organizer_feedback").fetchone()[0] == 0
