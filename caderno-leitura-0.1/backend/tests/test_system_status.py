"""F0.10.03 — painel de Sistema: commit do build, revisão do banco, backups automáticos e integridade.

Tudo em tmp_path: banco, pasta de backups e um .git fictício. Nenhum caminho do servidor aparece nas respostas.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.core import build_info
from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.db.base import Base
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.user import User


def _make_client(tmp_path, monkeypatch, role: str) -> TestClient:
    db_path = tmp_path / "sistema.db"
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(db_path))
    monkeypatch.setenv("LEITORUM_STORAGE_ROOT", "")
    monkeypatch.setenv("LEITORUM_SECONDARY_BACKUP_DIR", "")
    monkeypatch.setenv("LEITORUM_BUILD_COMMIT", "abc1234def")
    monkeypatch.setenv("LEITORUM_AUTO_BACKUP_HOURS", "24")
    monkeypatch.setenv("LEITORUM_AUTO_BACKUP_KEEP", "14")
    build_info.get_build_commit.cache_clear()
    engine = create_sqlite_engine(db_path)  # o engine da aplicação: liga secure_delete como no servidor
    Base.metadata.create_all(bind=engine)
    local = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
    with local() as session:
        session.add(User(id=DEFAULT_OWNER_ID, username=DEFAULT_OWNER_USERNAME, display_name="Dona Fictícia", role=role, status="ativo"))
        session.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        session.execute(text("INSERT INTO alembic_version VALUES ('0033_organizer_feedback')"))
        session.commit()

    application = create_app()

    def override_get_session():
        session = local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    application.dependency_overrides[get_session] = override_get_session
    return TestClient(application)


@pytest.fixture
def admin_client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    with _make_client(tmp_path, monkeypatch, "admin") as client:
        yield client
    build_info.get_build_commit.cache_clear()


@pytest.fixture
def reader_client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    with _make_client(tmp_path, monkeypatch, "user") as client:
        yield client
    build_info.get_build_commit.cache_clear()


# --- commit do build ------------------------------------------------------------------------------------------------


def _fake_git(tmp_path: Path) -> Path:
    git = tmp_path / "repo" / ".git"
    (git / "refs" / "heads").mkdir(parents=True)
    return git


def test_commit_from_env_has_priority(monkeypatch, tmp_path):
    monkeypatch.setenv("LEITORUM_BUILD_COMMIT", "0123456789abcdef")
    assert build_info.read_build_commit(tmp_path) == "0123456"


def test_commit_from_loose_ref(monkeypatch, tmp_path):
    monkeypatch.delenv("LEITORUM_BUILD_COMMIT", raising=False)
    git = _fake_git(tmp_path)
    (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (git / "refs" / "heads" / "main").write_text("deadbeefcafe0000000000000000000000000000\n", encoding="utf-8")
    assert build_info.read_build_commit(git.parent) == "deadbee"


def test_commit_from_packed_refs(monkeypatch, tmp_path):
    monkeypatch.delenv("LEITORUM_BUILD_COMMIT", raising=False)
    git = _fake_git(tmp_path)
    (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (git / "packed-refs").write_text(
        "# pack-refs with: peeled fully-peeled sorted\n0badc0ffee000000000000000000000000000000 refs/heads/main\n",
        encoding="utf-8",
    )
    assert build_info.read_build_commit(git.parent) == "0badc0f"


def test_commit_from_detached_head(monkeypatch, tmp_path):
    monkeypatch.delenv("LEITORUM_BUILD_COMMIT", raising=False)
    git = _fake_git(tmp_path)
    (git / "HEAD").write_text("feedface00000000000000000000000000000000\n", encoding="utf-8")
    assert build_info.read_build_commit(git.parent) == "feedfac"


def test_commit_unknown_without_git(monkeypatch, tmp_path):
    monkeypatch.delenv("LEITORUM_BUILD_COMMIT", raising=False)
    assert build_info.read_build_commit(tmp_path / "sem-repo") is None


def test_expected_schema_revision_is_the_latest_migration():
    heads = build_info.get_expected_schema_revisions()
    assert heads and all(isinstance(h, str) for h in heads)
    migrations = Path(build_info.__file__).resolve().parents[2] / "migrations" / "versions"
    latest = sorted(p.stem for p in migrations.glob("[0-9]*.py"))[-1]
    assert latest in heads


# --- status ---------------------------------------------------------------------------------------------------------


def test_status_for_reader_has_no_backup_block(reader_client):
    data = reader_client.get("/api/system/status").json()
    assert data["commit"] == "abc1234"
    assert data["schema_revision"] == "0033_organizer_feedback"
    assert data["expected_schema_revisions"]
    assert data["secure_delete"] is True
    assert data["google_auth_enabled"] is False
    assert data["backups"] is None


def test_status_for_admin_reports_backups_without_paths(admin_client, tmp_path):
    backups = tmp_path / "backups"
    backups.mkdir(exist_ok=True)
    now = datetime.now(UTC)
    for hours in (2, 26, 50):
        stamp = (now - timedelta(hours=hours)).strftime("%Y%m%d-%H%M%S")
        (backups / f"caderno-auto-{stamp}.db").write_bytes(b"")

    response = admin_client.get("/api/system/status")
    data = response.json()["backups"]

    assert data["enabled"] is True and data["interval_hours"] == 24 and data["keep"] == 14
    assert data["count"] == 3 and data["overdue"] is False and data["secondary_configured"] is False
    assert data["last_at"] is not None
    assert str(tmp_path) not in response.text and "caderno-auto" not in response.text


def test_status_flags_overdue_backups(admin_client, tmp_path):
    backups = tmp_path / "backups"
    backups.mkdir(exist_ok=True)
    stamp = (datetime.now(UTC) - timedelta(hours=60)).strftime("%Y%m%d-%H%M%S")
    (backups / f"caderno-auto-{stamp}.db").write_bytes(b"")
    assert admin_client.get("/api/system/status").json()["backups"]["overdue"] is True


# --- integridade ----------------------------------------------------------------------------------------------------


def test_integrity_check_ok_for_admin(admin_client):
    data = admin_client.post("/api/system/integrity-check").json()
    assert data["ok"] is True and data["detail"] is None and data["checked_at"]


def test_integrity_check_reports_damaged_database(admin_client, tmp_path, monkeypatch):
    damaged = tmp_path / "danificado.db"
    damaged.write_bytes(b"isto nao e um banco sqlite " * 100)
    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(damaged))
    data = admin_client.post("/api/system/integrity-check").json()
    assert data["ok"] is False and data["detail"]
    assert str(tmp_path) not in (data["detail"] or "")


def test_integrity_check_is_admin_only(reader_client):
    assert reader_client.post("/api/system/integrity-check").status_code == 403
