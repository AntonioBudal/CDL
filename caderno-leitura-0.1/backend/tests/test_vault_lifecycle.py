"""Feature 090-B (B019): cofre no backup, na restauração, na exportação, na exclusão da conta e na importação
dos arquivos legados. Tudo em tmp_path, com banco e imagens sintéticos."""

from __future__ import annotations

import base64
import importlib.util
import io
import json
import os
import socket
import sqlite3
import sys
import uuid
import zipfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from PIL import Image
from sqlalchemy.orm import Session

from app.core import config
from app.core.media_key import fingerprint
from app.db import session as db_session
from app.db.session import create_sqlite_engine
from app.models.book import Book
from app.models.encrypted_media import EncryptedMedia
from app.models.storage_settings import StorageSettings
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services import media_service
from app.services.account_service import delete_account_permanently
from app.services.backups import create_backup_bundle
from app.services.export_service import generate_account_export_zip
from app.services.restore_service import restore_backup_package
from app.services.vault import media_path

USER = "11111111-1111-1111-1111-111111111111"


def synthetic_webp(width: int = 640, height: int = 480, color=(30, 80, 130)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color).save(buffer, format="WEBP")
    return buffer.getvalue()


def migrated_db(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    alembic = Config(str(config.BACKEND_DIR / "alembic.ini"))
    alembic.attributes["database_path"] = path
    command.upgrade(alembic, "head")
    return path


@pytest.fixture
def acervo(tmp_path, monkeypatch, isolated_media_vault):
    """Banco de teste na head com um usuário, um livro e uma página no cofre."""
    for name in ("LEITORUM_STORAGE_ROOT", "LEITORUM_SECONDARY_BACKUP_DIR"):
        monkeypatch.delenv(name, raising=False)
    database = migrated_db(tmp_path / "acervo" / "caderno.db")
    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(database))
    engine = create_sqlite_engine(database)
    with Session(engine, expire_on_commit=False) as session:
        session.add(User(id=USER, username="leitor_teste", display_name="Leitor de Teste", role="user", status="ativo"))
        session.add(UserProfile(user_id=USER, username="leitor_teste", display_name="Leitor de Teste"))
        book = Book(user_id=USER, title="Livro de Teste")
        session.add(book)
        session.flush()
        page_webp = synthetic_webp()
        page = media_service.store(session, user_id=USER, kind="notebook_page", webp=page_webp)
        cover = media_service.store(session, user_id=USER, kind="cover", webp=synthetic_webp(200, 300), book_id=book.id)
        book.cover_image = cover.id
        session.commit()
        ids = {"page": page.id, "cover": cover.id, "book": book.id}
    yield {"db": database, "engine": engine, "vault": isolated_media_vault, "ids": ids, "page_webp": page_webp,
           "tmp": tmp_path}
    engine.dispose()


# --- backup -------------------------------------------------------------------------------------


def test_bundle_carries_encrypted_files_and_fingerprint_but_never_the_key(acervo):
    package = create_backup_bundle(acervo["tmp"] / "pacote.zip", source_db=acervo["db"],
                                   covers_dir=acervo["tmp"] / "sem-capas", vault_dir=acervo["vault"])
    key = base64.b64decode(os.environ["LEITORUM_MEDIA_MASTER_KEY"])

    with zipfile.ZipFile(package) as zf:
        names = zf.namelist()
        manifest = json.loads(zf.read("manifest.json"))
        blobs = b"".join(zf.read(name) for name in names)
    encs = sorted(name for name in names if name.startswith("vault/"))
    assert len(encs) == 4 and all(name.endswith(".enc") for name in encs)  # imagem + miniatura, duas mídias
    assert manifest["vault_files"] == 4
    assert all(name in manifest["files"] for name in encs)
    assert manifest["key_fingerprint"] == fingerprint(key)
    assert manifest["storage_id"]
    assert key not in blobs and os.environ["LEITORUM_MEDIA_MASTER_KEY"].encode() not in blobs
    assert acervo["page_webp"][:32] not in blobs


# --- restauração --------------------------------------------------------------------------------


def _target(tmp_path: Path) -> tuple[Path, Path, str]:
    target_db = migrated_db(tmp_path / "destino" / "caderno.db")
    storage_id = str(uuid.uuid4())
    with sqlite3.connect(target_db) as conn:
        conn.execute("INSERT INTO storage_settings (id, storage_id) VALUES (1, ?)", (storage_id,))
    target_vault = tmp_path / "destino" / "vault"
    target_vault.mkdir()
    return target_db, target_vault, storage_id


def test_restore_brings_encrypted_files_and_keeps_current_storage_identity(acervo):
    package = create_backup_bundle(acervo["tmp"] / "pacote.zip", source_db=acervo["db"],
                                   covers_dir=acervo["tmp"] / "sem-capas", vault_dir=acervo["vault"])
    target_db, target_vault, storage_id = _target(acervo["tmp"])

    result = restore_backup_package(package, target_db=target_db, target_covers=acervo["tmp"] / "destino" / "covers",
                                    target_vault=target_vault)

    assert result.media_restored == 4 and result.vault_warning is None
    for media_id in acervo["ids"]["page"], acervo["ids"]["cover"]:
        assert media_path(target_vault, uuid.UUID(media_id)).is_file()
    with sqlite3.connect(target_db) as conn:
        assert conn.execute("SELECT storage_id FROM storage_settings WHERE id = 1").fetchone()[0] == storage_id
        assert conn.execute("SELECT count(*) FROM encrypted_media").fetchone()[0] == 2


def test_restore_warns_when_package_was_encrypted_with_another_key(acervo, monkeypatch):
    package = create_backup_bundle(acervo["tmp"] / "pacote.zip", source_db=acervo["db"],
                                   covers_dir=acervo["tmp"] / "sem-capas", vault_dir=acervo["vault"])
    target_db, target_vault, _ = _target(acervo["tmp"])
    monkeypatch.setenv("LEITORUM_MEDIA_MASTER_KEY", base64.b64encode(os.urandom(32)).decode())

    result = restore_backup_package(package, target_db=target_db, target_covers=acervo["tmp"] / "destino" / "covers",
                                    target_vault=target_vault)
    assert result.media_restored == 4
    assert result.vault_warning and "outra chave" in result.vault_warning


def test_restore_rejects_tampered_encrypted_file(acervo):
    package = create_backup_bundle(acervo["tmp"] / "pacote.zip", source_db=acervo["db"],
                                   covers_dir=acervo["tmp"] / "sem-capas", vault_dir=acervo["vault"])
    tampered = acervo["tmp"] / "adulterado.zip"
    with zipfile.ZipFile(package) as source, zipfile.ZipFile(tampered, "w") as target:
        for item in source.infolist():
            data = source.read(item)
            if item.filename.startswith("vault/"):
                data = data[:-1] + bytes([data[-1] ^ 0xFF])
            target.writestr(item, data)
    target_db, target_vault, _ = _target(acervo["tmp"])

    with pytest.raises(ValueError):
        restore_backup_package(tampered, target_db=target_db, target_covers=acervo["tmp"] / "destino" / "covers",
                               target_vault=target_vault)
    assert list(target_vault.rglob("*.enc")) == []


# --- exportação e exclusão da conta -------------------------------------------------------------


def test_account_export_contains_decrypted_images(acervo):
    with Session(acervo["engine"], expire_on_commit=False) as session:
        user = session.get(User, USER)
        data, _ = generate_account_export_zip(session, user)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        assert f"imagens/paginas/{acervo['ids']['page']}.webp" in names
        assert f"imagens/capas/{acervo['ids']['cover']}.webp" in names
        assert zf.read(f"imagens/paginas/{acervo['ids']['page']}.webp") == acervo["page_webp"]


def test_account_export_skips_images_when_vault_is_locked(acervo, monkeypatch):
    monkeypatch.delenv("LEITORUM_MEDIA_MASTER_KEY")
    monkeypatch.setenv("LEITORUM_MEDIA_KEY_FILE", str(acervo["tmp"] / "sem-chave.key"))
    media_service.reset_cache()
    with Session(acervo["engine"], expire_on_commit=False) as session:
        data, _ = generate_account_export_zip(session, session.get(User, USER))
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        assert not any(name.startswith("imagens/") for name in zf.namelist())


def test_account_deletion_removes_encrypted_files_and_rows(acervo):
    with Session(acervo["engine"], expire_on_commit=False) as session:
        delete_account_permanently(session, session.get(User, USER), "leitor_teste")
        session.commit()
    assert list(acervo["vault"].rglob("*.enc")) == []
    with Session(acervo["engine"]) as session:
        assert session.query(EncryptedMedia).count() == 0
        assert session.get(User, USER) is None


# --- importação dos arquivos legados (scripts/migrate_storage_to_hd.py --vault-import) -------------

SCRIPT = config.BACKEND_DIR.parent / "scripts" / "migrate_storage_to_hd.py"


def _load_script():
    name = "migrate_storage_to_hd_cofre"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses exige o módulo registrado
    spec.loader.exec_module(module)
    return module


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def legado(tmp_path, monkeypatch, isolated_media_vault):
    """Instalação com capa e avatar ainda em claro (anteriores ao cofre)."""
    for name in ("LEITORUM_STORAGE_ROOT", "LEITORUM_SECONDARY_BACKUP_DIR"):
        monkeypatch.delenv(name, raising=False)
    database = migrated_db(tmp_path / "legado" / "caderno.db")
    covers, avatars = tmp_path / "legado" / "covers", tmp_path / "legado" / "avatars"
    covers.mkdir()
    avatars.mkdir()
    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(database))
    monkeypatch.setenv("CADERNO_COVERS_DIR", str(covers))
    monkeypatch.setenv("CADERNO_AVATARS_DIR", str(avatars))

    jpeg = io.BytesIO()
    exif = Image.Exif()
    exif[0x010F] = "CameraDeTeste"
    Image.new("RGB", (900, 1350), (90, 20, 20)).save(jpeg, format="JPEG", exif=exif)
    (covers / "capa_legada.jpg").write_bytes(jpeg.getvalue())
    (avatars / "avatar_legado.webp").write_bytes(synthetic_webp(300, 300))
    with sqlite3.connect(database) as conn:
        conn.execute("INSERT INTO users (id, username, display_name, role, status, created_at, updated_at) "
                     "VALUES (?, 'leitor_teste', 'Leitor de Teste', 'user', 'ativo', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                     (USER,))
        conn.execute("INSERT INTO user_profiles (user_id, username, display_name, avatar_url, profile_visibility, "
                     "dashboard_visibility, is_discoverable, show_reading_stats, created_at, updated_at) VALUES "
                     "(?, 'leitor_teste', 'Leitor de Teste', '/api/avatars/avatar_legado.webp', 'public', 'private', "
                     "1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", (USER,))
        for title in ("Livro de Teste", "Livro de Teste 2"):
            conn.execute("INSERT INTO books (user_id, title, cover_image, visibility, created_at, updated_at) "
                         "VALUES (?, ?, 'capa_legada.jpg', 'private', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                         (USER, title))
        conn.execute("INSERT INTO books (user_id, title, cover_image, visibility, created_at, updated_at) "
                     "VALUES (?, 'Livro sem arquivo', 'capa_sumida.webp', 'private', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                     (USER,))
    yield {"db": database, "covers": covers, "avatars": avatars, "vault": isolated_media_vault,
           "lock": tmp_path / "leitorum.lock"}
    db_session._get_engine_for_path(database.resolve()).dispose()


def test_vault_import_plan_only_counts(legado):
    mig = _load_script()
    before = (legado["db"].read_bytes(), sorted(p.name for p in legado["covers"].iterdir()))
    report = mig.vault_import(plan=True, lock_path=legado["lock"], port=_free_port())

    assert report["legacy_references"] == 3  # capa compartilhada conta uma vez, capa sumida, avatar
    assert report["files_found"] == 2 and report["files_missing"] == 1
    assert report["vault_state"] == "ready"
    assert list(legado["vault"].rglob("*.enc")) == []
    assert (legado["db"].read_bytes(), sorted(p.name for p in legado["covers"].iterdir())) == before


def test_vault_import_encrypts_updates_references_and_keeps_originals(legado):
    mig = _load_script()
    report = mig.vault_import(plan=False, lock_path=legado["lock"], port=_free_port())

    assert report["result"] == "ok" and report["imported"] == 2
    assert report["pre_import_snapshot"].startswith("caderno-pre-cofre-")
    assert (legado["db"].parent / "backups" / report["pre_import_snapshot"]).is_file()
    assert (legado["covers"] / "capa_legada.jpg").is_file()  # originais nunca apagados
    assert (legado["avatars"] / "avatar_legado.webp").is_file()

    with sqlite3.connect(legado["db"]) as conn:
        covers = {row[0] for row in conn.execute("SELECT cover_image FROM books WHERE title LIKE 'Livro de Teste%'")}
        avatar = conn.execute("SELECT avatar_url FROM user_profiles WHERE user_id = ?", (USER,)).fetchone()[0]
        missing = conn.execute("SELECT cover_image FROM books WHERE title = 'Livro sem arquivo'").fetchone()[0]
    assert len(covers) == 1 and media_service.UUID_RE.match(next(iter(covers)))
    assert avatar.startswith("/api/avatars/") and media_service.UUID_RE.match(avatar.rsplit("/", 1)[-1])
    assert missing == "capa_sumida.webp"  # sem arquivo, a referência fica como estava

    engine = create_sqlite_engine(legado["db"])
    try:
        with Session(engine) as session:
            media_service.reset_cache()
            cover_row = session.get(EncryptedMedia, next(iter(covers)))
            plain = media_service.read(session, cover_row)
            with Image.open(io.BytesIO(plain)) as image:
                assert image.format == "WEBP" and image.size == (800, 1200)
                assert not image.info.get("exif")
            assert b"CameraDeTeste" not in plain
            assert session.get(StorageSettings, 1).media_key_fingerprint
    finally:
        engine.dispose()

    again = mig.vault_import(plan=False, lock_path=legado["lock"], port=_free_port())
    assert again["imported"] == 0  # idempotente


def test_vault_import_refuses_while_server_runs(legado):
    mig = _load_script()
    with socket.socket() as busy:
        busy.bind(("127.0.0.1", 0))
        busy.listen()
        with pytest.raises(mig.MigrationError):
            mig.vault_import(plan=False, lock_path=legado["lock"], port=busy.getsockname()[1])
    assert list(legado["vault"].rglob("*.enc")) == []


def test_vault_import_refuses_when_vault_is_locked(legado, monkeypatch):
    mig = _load_script()
    monkeypatch.delenv("LEITORUM_MEDIA_MASTER_KEY")
    monkeypatch.setenv("LEITORUM_MEDIA_KEY_FILE", str(legado["db"].parent / "sem-chave.key"))
    media_service.reset_cache()
    before = legado["db"].read_bytes()
    with pytest.raises(media_service.VaultLocked):
        mig.vault_import(plan=False, lock_path=legado["lock"], port=_free_port())
    assert legado["db"].read_bytes() == before
