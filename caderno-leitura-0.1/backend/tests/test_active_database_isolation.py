"""Guarda da Constituição II.1: a suíte nunca resolve nem abre o banco ativo.

Nenhum teste aqui conecta ao banco ativo real; o bloqueio é exercitado com um
alvo falso em tmp_path, para que uma guarda quebrada não toque no acervo.
"""

from __future__ import annotations

import os
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient
import pytest

import conftest
from app.core.config import BACKEND_DIR, get_database_path
from app.db.session import create_sqlite_engine
from app.main import app


ACTIVE_DATABASE = BACKEND_DIR / "data" / "caderno.db"


@pytest.fixture
def fake_active_database(tmp_path, monkeypatch) -> Path:
    fake = tmp_path / "Pasta Ativa" / "ativo_falso.db"
    fake.parent.mkdir()
    monkeypatch.setattr(conftest, "_PROTECTED_DB_PATH", fake)
    yield fake
    conftest._ACTIVE_DB_ATTEMPTS.clear()


def test_database_path_is_not_active_database(session_database_dir):
    resolved = get_database_path()

    assert resolved != ACTIVE_DATABASE
    assert os.path.normcase(resolved) != os.path.normcase(ACTIVE_DATABASE.resolve())
    assert resolved.is_relative_to(session_database_dir.resolve())


def test_environment_points_to_session_temp_dir(session_database_dir):
    configured = Path(os.environ["CADERNO_DATABASE_PATH"])

    assert configured.is_absolute()
    assert configured.parent == session_database_dir


def test_sqlite_connect_is_guarded():
    assert sqlite3.connect is conftest._guarded_sqlite_connect
    assert sqlite3.dbapi2.connect is conftest._guarded_sqlite_connect


@pytest.mark.parametrize(
    ("make_target", "kwargs"),
    [
        (lambda fake: str(fake), {}),
        (lambda fake: fake, {}),
        (lambda fake: f"{fake.as_uri()}?mode=ro", {"uri": True}),
        (lambda fake: str(fake).swapcase(), {}),
        (lambda fake: str(fake) + "-wal", {}),
    ],
    ids=["str", "path", "uri", "maiusculas", "wal"],
)
def test_guard_blocks_protected_target_without_creating_it(fake_active_database, make_target, kwargs):
    with pytest.raises(RuntimeError, match="banco ativo"):
        sqlite3.connect(make_target(fake_active_database), **kwargs)

    assert conftest._ACTIVE_DB_ATTEMPTS
    assert not fake_active_database.exists()


def test_guard_blocks_sqlalchemy_engine(fake_active_database):
    with pytest.raises(RuntimeError, match="banco ativo"):
        create_sqlite_engine(fake_active_database).connect()

    assert not fake_active_database.exists()


def test_guard_allows_other_databases(tmp_path):
    with sqlite3.connect(tmp_path / "outro.db") as connection:
        assert connection.execute("SELECT 1").fetchone() == (1,)
    with sqlite3.connect(":memory:") as connection:
        assert connection.execute("SELECT 1").fetchone() == (1,)

    assert not conftest._ACTIVE_DB_ATTEMPTS


def test_lifespan_maintenance_runs_on_session_database(session_database_dir):
    assert get_session_override_absent()

    with TestClient(app):
        pass

    assert not conftest._ACTIVE_DB_ATTEMPTS
    assert (session_database_dir / "caderno.db").exists()


def get_session_override_absent() -> bool:
    from app.db.session import get_session

    return get_session not in app.dependency_overrides
