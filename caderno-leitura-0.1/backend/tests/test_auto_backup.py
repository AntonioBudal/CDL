"""Feature 090-A, camada de proteção 2: backup automático diário com segunda cópia e retenção (tmp_path)."""

from datetime import UTC, datetime, timedelta
import sqlite3

import pytest

from app.services.maintenance import AUTO_BACKUP_PREFIX, run_auto_backup_if_due

T0 = datetime(2026, 10, 27, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    for name in ("CADERNO_DATABASE_PATH", "LEITORUM_STORAGE_ROOT", "LEITORUM_SECONDARY_BACKUP_DIR",
                 "LEITORUM_AUTO_BACKUP_HOURS", "LEITORUM_AUTO_BACKUP_KEEP"):
        monkeypatch.delenv(name, raising=False)
    database = tmp_path / "dados" / "caderno.db"
    database.parent.mkdir()
    with sqlite3.connect(database) as conn:
        conn.execute("CREATE TABLE livros (id INTEGER PRIMARY KEY, titulo TEXT)")
        conn.execute("INSERT INTO livros (titulo) VALUES ('Livro de Teste')")
    secondary = tmp_path / "segunda"
    monkeypatch.setenv("LEITORUM_SECONDARY_BACKUP_DIR", str(secondary))
    return database, database.parent / "backups", secondary, monkeypatch


def autos(folder):
    return sorted(p.name for p in folder.glob(f"{AUTO_BACKUP_PREFIX}*.db")) if folder.is_dir() else []


def test_creates_first_backup_and_secondary_copy(setup):
    database, backups, secondary, _ = setup
    path = run_auto_backup_if_due(T0, database_path=database)
    assert path.name == "caderno-auto-20261027-120000.db"
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT titulo FROM livros").fetchone() == ("Livro de Teste",)
    assert autos(secondary) == [path.name]


def test_nothing_before_interval(setup):
    database, backups, _, _ = setup
    run_auto_backup_if_due(T0, database_path=database)
    assert run_auto_backup_if_due(T0 + timedelta(hours=23), database_path=database) is None
    assert run_auto_backup_if_due(T0 + timedelta(hours=24), database_path=database) is not None
    assert len(autos(backups)) == 2


def test_rotation_keeps_only_automatic_and_recent(setup):
    database, backups, secondary, env = setup
    env.setenv("LEITORUM_AUTO_BACKUP_KEEP", "3")
    backups.mkdir()
    (backups / "caderno-pre-migracao-20261001-000000.db").write_bytes(b"snapshot ficticio")
    (backups / "caderno-backup-20261001.zip").write_bytes(b"pacote ficticio")
    for day in range(5):
        run_auto_backup_if_due(T0 + timedelta(days=day), database_path=database)
    assert autos(backups) == [f"caderno-auto-202610{d}-120000.db" for d in (29, 30, 31)]
    assert autos(secondary) == autos(backups)
    assert (backups / "caderno-pre-migracao-20261001-000000.db").exists()
    assert (backups / "caderno-backup-20261001.zip").exists()


def test_zero_disables(setup):
    database, backups, _, env = setup
    env.setenv("LEITORUM_AUTO_BACKUP_HOURS", "0")
    assert run_auto_backup_if_due(T0, database_path=database) is None
    assert autos(backups) == []


def test_missing_database_does_nothing(setup, tmp_path):
    assert run_auto_backup_if_due(T0, database_path=tmp_path / "nao-existe.db") is None
