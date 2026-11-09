"""F0.11.01 (spec 103): estado de leitura do livro. Só dados fictícios; bancos em tmp_path."""
from __future__ import annotations

import io
import json
import sqlite3
import zipfile
from datetime import date

from alembic import command
from alembic.config import Config
from fastapi import HTTPException
import pytest

from app.core.config import BACKEND_DIR
from app.models.book import Book
from app.routers.books import apply_reading_state_rules
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture reaproveitada)
    USER_ALICE_ID,
    sharing_harness,
)

def _create_book(client, **fields):
    res = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autora Fictícia", **fields})
    assert res.status_code == 201, res.text
    return res.json()


def _patch(client, book, **fields):
    return client.patch(f"/api/books/{book['id']}", json={"expected_version": book["version"], **fields})


# ---------- Migração ----------

def _alembic(db_path):
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db_path
    return cfg


def test_migration_0034_up_and_down_keeps_fictitious_data(tmp_path):
    db_path = tmp_path / "migracao.db"
    cfg = _alembic(db_path)
    command.upgrade(cfg, "0033_organizer_feedback")
    with sqlite3.connect(db_path) as conn:
        user_id = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        assert user_id is not None, "a migração inicial cria o dono padrão"
        conn.execute("INSERT INTO books (user_id, title, author) VALUES (?, 'Livro de Teste', 'Autora Fictícia')", user_id)
        conn.commit()

    command.upgrade(cfg, "0034_book_reading_state")
    with sqlite3.connect(db_path) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(books)")}
        assert {"reading_state", "reading_started_on", "reading_finished_on"} <= cols
        row = conn.execute("SELECT title, reading_state, reading_started_on FROM books").fetchone()
        assert row == ("Livro de Teste", None, None), "nenhum dado existente muda"
        indexes = {row[1] for row in conn.execute("PRAGMA index_list(books)")}
        assert "ix_books_user_reading_state" in indexes
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE books SET reading_state = 'inventado'")
        conn.execute("UPDATE books SET reading_state = 'lendo', reading_started_on = '2026-11-01'")
        conn.commit()

    command.downgrade(cfg, "0033_organizer_feedback")
    with sqlite3.connect(db_path) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(books)")}
        assert "reading_state" not in cols and "reading_finished_on" not in cols
        assert conn.execute("SELECT title FROM books").fetchone() == ("Livro de Teste",)
        assert conn.execute("PRAGMA quick_check").fetchone() == ("ok",)


def test_upgrade_to_0034_creates_validated_snapshot_first(tmp_path):
    """O snapshot pré-migração (maintenance.ensure_pre_upgrade_snapshot) cobre esta migração também."""
    db_path = tmp_path / "pasta com espaço" / "caderno.db"
    db_path.parent.mkdir()
    cfg = _alembic(db_path)
    command.upgrade(cfg, "0033_organizer_feedback")
    backups = db_path.parent / "backups"
    for old in backups.glob("caderno-pre-migracao-*.db"):
        old.unlink()
    command.upgrade(cfg, "head")
    snapshots = list(backups.glob("caderno-pre-migracao-*.db"))
    assert len(snapshots) == 1
    with sqlite3.connect(snapshots[0]) as conn:
        assert conn.execute("SELECT version_num FROM alembic_version").fetchone() == ("0033_organizer_feedback",)
        assert conn.execute("PRAGMA quick_check").fetchone() == ("ok",)


# ---------- Regras ----------

def _book_obj(state=None, started=None, finished=None):
    return Book(title="Livro de Teste", reading_state=state, reading_started_on=started, reading_finished_on=finished)


def test_rules_fill_dates_only_when_empty():
    today = date(2026, 11, 9)
    changes = {"reading_state": "lendo"}
    apply_reading_state_rules(_book_obj(), changes, today=today)
    assert changes["reading_started_on"] == today

    changes = {"reading_state": "lido"}
    apply_reading_state_rules(_book_obj("lendo", date(2026, 10, 1)), changes, today=today)
    assert changes["reading_finished_on"] == today
    assert "reading_started_on" not in changes

    changes = {"reading_state": "lendo"}
    apply_reading_state_rules(_book_obj(None, date(2026, 1, 2)), changes, today=today)
    assert "reading_started_on" not in changes, "data já preenchida não muda"

    changes = {"reading_state": "lido", "reading_finished_on": None}
    apply_reading_state_rules(_book_obj(), changes, today=today)
    assert changes["reading_finished_on"] is None, "o que o leitor enviou prevalece"


def test_rules_reject_finish_before_start():
    with pytest.raises(HTTPException) as exc:
        apply_reading_state_rules(
            _book_obj("lendo", date(2026, 11, 5)), {"reading_finished_on": date(2026, 11, 1)}, today=date(2026, 11, 9)
        )
    assert exc.value.status_code == 422


# ---------- API ----------

def test_patch_states_dates_and_validation(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book = _create_book(c)
    assert book["reading_state"] is None and book["reading_started_on"] is None

    res = _patch(c, book, reading_state="lendo")
    assert res.status_code == 200, res.text
    book = res.json()
    assert book["reading_state"] == "lendo"
    assert book["reading_started_on"] == date.today().isoformat()

    res = _patch(c, book, reading_state="lido", reading_finished_on="2000-01-01")
    assert res.status_code == 422
    assert "anterior" in res.json()["detail"]

    res = _patch(c, book, reading_state="abandonado", reading_started_on="2026-01-02", reading_finished_on="2026-02-03")
    assert res.status_code == 200
    book = res.json()
    assert (book["reading_state"], book["reading_started_on"], book["reading_finished_on"]) == (
        "abandonado", "2026-01-02", "2026-02-03")

    res = _patch(c, book, reading_state=None)
    assert res.status_code == 200
    assert res.json()["reading_state"] is None
    assert res.json()["reading_started_on"] == "2026-01-02", "voltar a nenhum mantém as datas"

    assert _patch(c, res.json(), reading_state="inventado").status_code == 422


def test_version_conflict_still_applies(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book = _create_book(c)
    assert _patch(c, book, reading_state="quero_ler").status_code == 200
    stale = c.patch(f"/api/books/{book['id']}", json={"expected_version": book["version"], "reading_state": "lendo"})
    assert stale.status_code == 409


def test_reading_state_hidden_from_other_readers(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book = _create_book(c)
    book = _patch(c, book, reading_state="lendo").json()
    assert c.put(f"/api/books/{book['id']}/visibility", json={"visibility": "friends"}).status_code == 200
    own = c.get(f"/api/books/{book['id']}").json()
    assert own["reading_state"] == "lendo"
    other = sharing_harness.client_bob.get(f"/api/books/{book['id']}")
    assert other.status_code == 200
    data = other.json()
    assert data["reading_state"] is None
    assert data["reading_started_on"] is None and data["reading_finished_on"] is None


def test_book_export_includes_state_only_for_owner(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book = _create_book(c)
    book = _patch(c, book, reading_state="lido", reading_started_on="2026-10-01", reading_finished_on="2026-11-02").json()
    c.put(f"/api/books/{book['id']}/visibility", json={"visibility": "friends"})

    md = c.get(f"/api/books/{book['id']}/export", params={"format": "markdown"}).text
    assert 'reading_state: "lido"' in md
    assert "**Leitura:** Lido, início 01/10/2026, fim 02/11/2026" in md
    txt = c.get(f"/api/books/{book['id']}/export", params={"format": "text"}).text
    assert "Leitura: Lido, início 01/10/2026, fim 02/11/2026" in txt

    other = sharing_harness.client_bob.get(f"/api/books/{book['id']}/export", params={"format": "markdown"})
    assert other.status_code == 200
    assert "reading_state" not in other.text and "Leitura:" not in other.text


def test_account_zip_json_has_reading_fields(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book = _create_book(c)
    _patch(c, book, reading_state="quero_ler")
    res = c.get("/api/account/export")
    assert res.status_code == 200
    with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
        data = json.loads(zf.read("dados_acervo.json"))
    exported = next(b for b in data["books"] if b["id"] == book["id"])
    assert exported["reading_state"] == "quero_ler"
    assert exported["reading_started_on"] is None and exported["reading_finished_on"] is None


def test_sync_includes_reading_fields(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book = _create_book(c)
    _patch(c, book, reading_state="lendo")
    res = c.get("/api/sync/changes")
    assert res.status_code == 200, res.text
    books = res.json()["updated"]["books"]
    assert next(b for b in books if b["id"] == book["id"])["reading_state"] == "lendo"
