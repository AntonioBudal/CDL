"""Testes automatizados isolados para geração e integridade de pacote ZIP de backup (T008)."""
from pathlib import Path
import sqlite3
import zipfile
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_covers_dir
from app.main import app
from app.services.backups import (
    calculate_file_sha256,
    create_backup_bundle,
    create_database_backup,
    verify_sqlite_integrity,
)


def init_sample_database(db_path: Path) -> None:
    """Cria um banco SQLite sintético para testes isolados."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)")
        conn.execute("INSERT INTO alembic_version VALUES ('0005_trash_and_covers')")
        conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT)")
        conn.execute("CREATE TABLE chapters (id INTEGER PRIMARY KEY, book_id INTEGER, title TEXT)")
        conn.execute("CREATE TABLE studies (id INTEGER PRIMARY KEY, title TEXT)")
        conn.execute("INSERT INTO books VALUES (1, 'Livro Sintético 1'), (2, 'Livro Sintético 2')")
        conn.execute("INSERT INTO chapters VALUES (1, 1, 'Capítulo 1')")
        conn.execute("INSERT INTO studies VALUES (1, 'Estudo 1'), (2, 'Estudo 2')")
        conn.commit()


def test_create_backup_bundle_success(tmp_path: Path):
    source_db = tmp_path / "source.db"
    init_sample_database(source_db)

    covers_dir = tmp_path / "covers"
    covers_dir.mkdir(parents=True, exist_ok=True)
    sample_cover = covers_dir / "capa-teste.jpg"
    sample_cover.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

    bundle_dest = tmp_path / "caderno-backup-teste.zip"
    created = create_backup_bundle(
        destination=bundle_dest,
        source_db=source_db,
        covers_dir=covers_dir,
        app_version="0.3.0",
    )

    assert created.is_file()
    assert zipfile.is_zipfile(created)

    # Inspeciona o conteúdo interno do ZIP
    with zipfile.ZipFile(created, "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist
        assert "caderno.db" in namelist
        assert "covers/capa-teste.jpg" in namelist

        # Valida hashes do manifesto
        extract_dir = tmp_path / "unpacked"
        zf.extractall(extract_dir)

        manifest_file = extract_dir / "manifest.json"
        import json
        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))

        assert manifest_data["app_version"] == "0.3.0"
        assert manifest_data["schema_version"] == "0005_trash_and_covers"
        assert manifest_data["counts"]["books"] == 2
        assert manifest_data["counts"]["chapters"] == 1
        assert manifest_data["counts"]["studies"] == 2
        assert manifest_data["counts"]["covers"] == 1

        for file_rel, expected_hash in manifest_data["files"].items():
            extracted_file = extract_dir / file_rel
            assert extracted_file.is_file()
            assert calculate_file_sha256(extracted_file) == expected_hash

        # Valida integridade física do banco descompactado
        is_ok, err = verify_sqlite_integrity(extract_dir / "caderno.db")
        assert is_ok is True
        assert err is None


def test_api_backup_bundle_endpoint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source_db = tmp_path / "active.db"
    init_sample_database(source_db)

    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(source_db))
    monkeypatch.setenv("CADERNO_COVERS_DIR", str(tmp_path / "covers"))

    client = TestClient(app)
    response = client.get("/api/backup/bundle")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "caderno-backup-" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0

    downloaded_zip = tmp_path / "downloaded.zip"
    downloaded_zip.write_bytes(response.content)
    assert zipfile.is_zipfile(downloaded_zip)
