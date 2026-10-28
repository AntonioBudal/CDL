"""Feature 090-A: raiz única de armazenamento, falha segura, trava do servidor e segunda cópia de backup.

Tudo em tmp_path: a "raiz do HD" é uma pasta temporária. Nenhum teste toca o banco ativo nem o HD real.
"""

import os
import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest

from app.core import config, server_lock
from app.core.storage import StorageError, read_marker, verify_root, write_marker
from app.db import session as db_session
from app.main import create_app
from app.services.backups import calculate_file_sha256, copy_to_secondary
from app.services.maintenance import create_pre_upgrade_snapshot


@pytest.fixture
def env(monkeypatch):
    """Ambiente limpo: sem as variáveis de caminho que a suíte usa para isolar o banco."""
    for name in ("CADERNO_DATABASE_PATH", "CADERNO_COVERS_DIR", "CADERNO_AVATARS_DIR",
                 "LEITORUM_STORAGE_ROOT", "LEITORUM_SECONDARY_BACKUP_DIR"):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def migrated_root(root: Path) -> Path:
    """Raiz válida: marcador, banco migrado até a head e o mesmo storage_id no banco."""
    (root / "db").mkdir(parents=True)
    database = root / "db" / "caderno.db"
    alembic = Config(str(config.BACKEND_DIR / "alembic.ini"))
    alembic.attributes["database_path"] = database
    command.upgrade(alembic, "head")
    storage_id = write_marker(root)
    with sqlite3.connect(database) as conn:
        conn.execute("INSERT INTO storage_settings (id, storage_id) VALUES (1, ?)", (storage_id,))
    return database


def test_without_root_everything_is_as_before(env):
    assert config.get_storage_root() is None
    assert config.get_database_path() == config.BACKEND_DIR / "data" / "caderno.db"


def test_root_derives_paths_and_caderno_variables_win(env, tmp_path):
    root = tmp_path / "hd"
    env.setenv("LEITORUM_STORAGE_ROOT", str(root))
    assert config.get_database_path() == root / "db" / "caderno.db"
    env.setenv("CADERNO_DATABASE_PATH", str(tmp_path / "outro" / "caderno.db"))
    assert config.get_database_path() == (tmp_path / "outro" / "caderno.db").resolve()
    assert config.get_root_database_path() is None


def test_relative_root_is_rejected(env):
    env.setenv("LEITORUM_STORAGE_ROOT", "relativo/hd")
    with pytest.raises(ValueError):
        config.get_storage_root()


def test_missing_or_unmarked_root_creates_nothing(env, tmp_path):
    root = tmp_path / "hd-ausente"
    env.setenv("LEITORUM_STORAGE_ROOT", str(root))
    for getter in (config.get_backup_dir, config.get_covers_dir, config.get_avatars_dir):
        with pytest.raises(StorageError):
            getter()
    assert not root.exists()
    root.mkdir()
    with pytest.raises(StorageError):
        config.get_backup_dir()
    assert list(root.iterdir()) == []


def test_marked_root_creates_only_its_subfolders(env, tmp_path):
    root = tmp_path / "hd"
    root.mkdir()
    write_marker(root)
    env.setenv("LEITORUM_STORAGE_ROOT", str(root))
    assert config.get_backup_dir() == (root / "backups").resolve()
    assert config.get_covers_dir() == (root / "covers").resolve()
    assert config.get_avatars_dir() == (root / "avatars").resolve()
    env.setenv("CADERNO_COVERS_DIR", str(tmp_path / "capas"))
    assert config.get_covers_dir() == (tmp_path / "capas").resolve()


def test_marker_is_never_overwritten(tmp_path):
    first = write_marker(tmp_path)
    with pytest.raises(StorageError):
        write_marker(tmp_path)
    assert read_marker(tmp_path)["storage_id"] == first


def test_engine_requires_marker_and_same_identity(env, tmp_path):
    root = tmp_path / "hd"
    database = migrated_root(root)
    env.setenv("LEITORUM_STORAGE_ROOT", str(root))
    assert db_session._get_engine_for_path(database) is not None
    assert verify_root(root, database) == read_marker(root)["storage_id"]
    # outro disco com o mesmo caminho: marcador com outra identidade
    (root / ".leitorum-storage.json").unlink()
    write_marker(root)
    with pytest.raises(StorageError):
        verify_root(root, database)
    other = tmp_path / "hd2"
    other.mkdir()
    env.setenv("LEITORUM_STORAGE_ROOT", str(other))
    with pytest.raises(StorageError):
        db_session._get_engine_for_path(other / "db" / "caderno.db")
    assert list(other.iterdir()) == []


def test_engine_never_creates_the_database_folder_under_root(env, tmp_path):
    root = tmp_path / "hd"
    root.mkdir()
    env.setenv("LEITORUM_STORAGE_ROOT", str(root))
    db_session.create_sqlite_engine(root / "db" / "caderno.db").dispose()
    assert not (root / "db").exists()


def test_disk_disappearing_while_running_gives_503_and_creates_nothing(env, tmp_path):
    root = tmp_path / "hd"
    database = migrated_root(root)
    env.setenv("LEITORUM_STORAGE_ROOT", str(root))
    client = TestClient(create_app())
    assert client.get("/api/books").status_code == 200
    db_session._get_engine_for_path(database).dispose()
    moved = tmp_path / "hd-desconectado"
    root.rename(moved)
    response = client.get("/api/books")
    assert response.status_code == 503
    assert not root.exists()


def test_secondary_copy_with_checked_hash(env, tmp_path):
    secondary = tmp_path / "segunda"
    env.setenv("LEITORUM_SECONDARY_BACKUP_DIR", str(secondary))
    backup = tmp_path / "caderno-backup-teste.zip"
    backup.write_bytes(b"conteudo ficticio de backup")
    copied = copy_to_secondary(backup)
    assert copied == (secondary / backup.name).resolve()
    assert calculate_file_sha256(copied) == calculate_file_sha256(backup)


def test_secondary_copy_inside_root_is_refused(env, tmp_path):
    root = tmp_path / "hd"
    root.mkdir()
    env.setenv("LEITORUM_STORAGE_ROOT", str(root))
    env.setenv("LEITORUM_SECONDARY_BACKUP_DIR", str(root / "copia"))
    with pytest.raises(ValueError):
        config.get_secondary_backup_dir()
    backup = tmp_path / "b.db"
    backup.write_bytes(b"x")
    assert copy_to_secondary(backup) is None
    assert not (root / "copia").exists()


def test_pre_upgrade_snapshot_also_goes_to_secondary(env, tmp_path):
    database = tmp_path / "dados" / "caderno.db"
    database.parent.mkdir()
    with sqlite3.connect(database) as conn:
        conn.execute("CREATE TABLE livros (id INTEGER PRIMARY KEY, titulo TEXT)")
        conn.execute("INSERT INTO livros (titulo) VALUES ('Livro de Teste')")
    secondary = tmp_path / "segunda"
    env.setenv("LEITORUM_SECONDARY_BACKUP_DIR", str(secondary))
    snapshot = create_pre_upgrade_snapshot(database)
    assert (secondary / snapshot.name).is_file()


def test_server_lock_lifecycle(tmp_path):
    lock = tmp_path / "leitorum.lock"
    server_lock.acquire(8000, lock)
    assert server_lock.active_lock(lock)["pid"] == os.getpid()
    server_lock.release(lock)
    assert not lock.exists()


def test_stale_lock_is_ignored_and_live_lock_blocks(tmp_path):
    lock = tmp_path / "leitorum.lock"
    lock.write_text('{"pid": 999999, "port": 8000}', encoding="utf-8")
    assert server_lock.active_lock(lock) is None
    server_lock.acquire(8001, lock)
    lock.write_text(f'{{"pid": {os.getppid()}, "port": 8000}}', encoding="utf-8")
    assert server_lock.active_lock(lock) is not None
    with pytest.raises(RuntimeError):
        server_lock.acquire(8002, lock)


@pytest.mark.skipif(os.name != "nt", reason="caminhos do Windows não diferenciam maiúsculas")
def test_root_matching_ignores_letter_case_on_windows(env, tmp_path):
    root = tmp_path / "HD"
    root.mkdir()
    write_marker(root)
    env.setenv("LEITORUM_STORAGE_ROOT", str(root).upper())
    lower_db = Path(str(root / "db" / "caderno.db").lower())
    assert os.path.normcase(config.get_backup_dir(lower_db)) == os.path.normcase((root / "backups").resolve())
