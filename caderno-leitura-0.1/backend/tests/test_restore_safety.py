"""Testes automatizados de segurança, sandbox, Zip Slip e rollback na restauração (T015)."""
import io
import json
from pathlib import Path
import sqlite3
import zipfile
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.backups import (
    calculate_file_sha256,
    create_backup_bundle,
    verify_sqlite_integrity,
)
from app.services.restore_service import (
    restore_backup_package,
    safe_extract_zip,
)


def init_db(db_path: Path, title: str) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)")
        conn.execute("INSERT INTO alembic_version VALUES ('0005_trash_and_covers')")
        conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT)")
        conn.execute("CREATE TABLE chapters (id INTEGER PRIMARY KEY, book_id INTEGER, title TEXT)")
        conn.execute("CREATE TABLE studies (id INTEGER PRIMARY KEY, title TEXT)")
        conn.execute("INSERT INTO books VALUES (1, ?)", (title,))
        conn.commit()


def test_restore_backup_package_success_and_snapshot(tmp_path: Path):
    active_db = tmp_path / "active" / "caderno.db"
    init_db(active_db, "Livro Ativo Original")

    covers_active = tmp_path / "active" / "covers"
    covers_active.mkdir(parents=True, exist_ok=True)

    # Cria pacote de backup para restauração
    new_db = tmp_path / "new" / "caderno.db"
    init_db(new_db, "Livro Restaurado Novo")

    covers_new = tmp_path / "new" / "covers"
    covers_new.mkdir(parents=True, exist_ok=True)
    (covers_new / "nova-capa.jpg").write_bytes(b"image-bytes")

    pkg_zip = tmp_path / "pacote-para-restaurar.zip"
    create_backup_bundle(
        destination=pkg_zip,
        source_db=new_db,
        covers_dir=covers_new,
        app_version="0.3.0",
    )

    result = restore_backup_package(
        pkg_zip,
        target_db=active_db,
        target_covers=covers_active,
    )

    assert result.success is True
    assert result.covers_restored == 1
    assert "caderno-pre-restauracao-" in result.pre_restore_snapshot

    # Confere que o banco ativo agora tem o novo título
    with sqlite3.connect(active_db) as conn:
        row = conn.execute("SELECT title FROM books WHERE id=1").fetchone()
        assert row[0] == "Livro Restaurado Novo"

    # Confere que a capa foi restaurada
    assert (covers_active / "nova-capa.jpg").is_file()

    # Confere que o snapshot pré-restauração preservou o acervo original
    backup_dir = active_db.parent / "backups"
    snapshot_file = backup_dir / result.pre_restore_snapshot
    assert snapshot_file.is_file()
    with sqlite3.connect(snapshot_file) as conn:
        row = conn.execute("SELECT title FROM books WHERE id=1").fetchone()
        assert row[0] == "Livro Ativo Original"


def test_restore_zip_slip_rejection(tmp_path: Path):
    active_db = tmp_path / "active" / "caderno.db"
    init_db(active_db, "Livro Intacto")

    malicious_zip = tmp_path / "malicious.zip"
    with zipfile.ZipFile(malicious_zip, "w") as zf:
        zf.writestr("../../escape.txt", "conteudo perigoso")
        zf.writestr("caderno.db", "conteudo qualquer")

    with pytest.raises(ValueError, match="Zip Slip"):
        restore_backup_package(malicious_zip, target_db=active_db)

    # Verifica que o ativo não foi alterado
    with sqlite3.connect(active_db) as conn:
        row = conn.execute("SELECT title FROM books WHERE id=1").fetchone()
        assert row[0] == "Livro Intacto"


def test_restore_tampered_hash_rejection(tmp_path: Path):
    active_db = tmp_path / "active" / "caderno.db"
    init_db(active_db, "Livro Intacto")

    source_db = tmp_path / "sample" / "caderno.db"
    init_db(source_db, "Livro A")

    valid_zip = tmp_path / "valid.zip"
    create_backup_bundle(destination=valid_zip, source_db=source_db, covers_dir=tmp_path / "covers")

    # Cria pacote adulterado com 1 byte diferente no caderno.db
    tampered_zip = tmp_path / "tampered.zip"
    with zipfile.ZipFile(valid_zip, "r") as src_zf:
        with zipfile.ZipFile(tampered_zip, "w") as dst_zf:
            for item in src_zf.infolist():
                data = src_zf.read(item.filename)
                if item.filename == "caderno.db":
                    data = data + b"\x00"  # altera tamanho/hash
                dst_zf.writestr(item, data)

    with pytest.raises(ValueError, match="Soma de verificação SHA-256 divergente"):
        restore_backup_package(tampered_zip, target_db=active_db)

    # Verifica que o ativo não foi alterado
    with sqlite3.connect(active_db) as conn:
        row = conn.execute("SELECT title FROM books WHERE id=1").fetchone()
        assert row[0] == "Livro Intacto"


def test_api_restore_endpoint_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    active_db = tmp_path / "active" / "caderno.db"
    init_db(active_db, "Acervo Antes da API")
    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(active_db))
    monkeypatch.setenv("CADERNO_COVERS_DIR", str(tmp_path / "active" / "covers"))

    new_db = tmp_path / "new" / "caderno.db"
    init_db(new_db, "Acervo Pós API")
    pkg_zip = tmp_path / "backup.zip"
    create_backup_bundle(destination=pkg_zip, source_db=new_db)

    client = TestClient(app)
    with open(pkg_zip, "rb") as f:
        response = client.post(
            "/api/backup/restore",
            files={"file": ("backup.zip", f, "application/zip")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "caderno-pre-restauracao-" in data["pre_restore_snapshot"]

    with sqlite3.connect(active_db) as conn:
        row = conn.execute("SELECT title FROM books WHERE id=1").fetchone()
        assert row[0] == "Acervo Pós API"
