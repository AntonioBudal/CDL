"""Feature 090-A: script de migração para o HD, validado inteiro em tmp_path (contrato de migração).

Origem: banco fictício migrado até a head, com livro, capítulo e estudo de teste, backups e capas falsas.
Em todas as falhas injetadas: nada é trocado, o .env fica igual, o destino é limpo e a origem fica
byte a byte igual.
"""

import hashlib
import importlib.util
import json
import os
import socket
import sys
import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core import config
from app.core.storage import MARKER_NAME
from app.db import session as db_session
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app

SCRIPT = config.BACKEND_DIR.parent / "scripts" / "migrate_storage_to_hd.py"
spec = importlib.util.spec_from_file_location("migrate_storage_to_hd", SCRIPT)
mig = importlib.util.module_from_spec(spec)
sys.modules["migrate_storage_to_hd"] = mig  # dataclasses exige o módulo registrado
spec.loader.exec_module(mig)

ENV_TEXT = "ALLOW_REGISTRATION=false\nREQUIRE_AUTH=false\n"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def tree(root: Path) -> dict[str, tuple[int, float]]:
    return {str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime) for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def env(monkeypatch):
    for name in ("CADERNO_DATABASE_PATH", "CADERNO_COVERS_DIR", "CADERNO_AVATARS_DIR",
                 "LEITORUM_STORAGE_ROOT", "LEITORUM_SECONDARY_BACKUP_DIR"):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.fixture
def origem(tmp_path):
    """Instalação de origem fictícia: banco migrado com dados de teste, backups e capas."""
    data = tmp_path / "origem" / "data"
    data.mkdir(parents=True)
    database = data / "caderno.db"
    alembic = Config(str(config.BACKEND_DIR / "alembic.ini"))
    alembic.attributes["database_path"] = database
    command.upgrade(alembic, "head")
    engine = create_sqlite_engine(database)
    app = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_session] = test_session
    client = TestClient(app)
    book = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autor de Teste"}).json()
    chapter = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    client.post("/api/studies", json={"chapter_id": chapter["id"], "title": "Estudo de teste", "location": "",
                                      "source_response": "", "summary": "Resumo fictício.", "explanation": "",
                                      "concepts": "", "references": "", "notes": ""})
    engine.dispose()
    (data / "backups").mkdir()
    (data / "backups" / "caderno-backup-teste.zip").write_bytes(b"pacote ficticio")
    (data / "backups" / "antigo.db").write_bytes(b"snapshot ficticio")
    (data / "backups" / "ignorar.txt").write_text("nao copiar")
    (data / "covers").mkdir()
    (data / "covers" / "capa-teste.webp").write_bytes(b"RIFFxxxxWEBPficticio")
    env_file = tmp_path / "origem" / ".env"
    env_file.write_text(ENV_TEXT, encoding="utf-8")
    return {"database": database, "data": data, "env_file": env_file, "tmp": tmp_path}


def context(origem, target: Path, **overrides) -> "mig.Context":
    data = origem["data"]
    ctx = mig.Context(
        target=target,
        source_db=origem["database"],
        source_backups=data / "backups",
        legacy_dirs={"covers": data / "covers"},
        env_file=origem["env_file"],
        project_dir=origem["env_file"].parent,
        lock_path=origem["tmp"] / "leitorum.lock",
        port=free_port(),
    )
    for key, value in overrides.items():
        setattr(ctx, key, value)
    return ctx


def assert_nothing_switched(origem, target, source_hash, env_hash):
    assert sha(origem["database"]) == source_hash
    assert sha(origem["env_file"]) == env_hash
    assert not (target / "db" / "caderno.db").exists()
    assert not (target / MARKER_NAME).exists()


# --- caminho feliz ---------------------------------------------------------------------------


def test_plan_writes_nothing(env, origem):
    target = origem["tmp"] / "hd" / "Leitorum"
    before = tree(origem["tmp"])
    info = mig.preconditions(context(origem, target))
    assert info["problems"] == []
    assert info["target_filesystem"] in (None, "NTFS")
    assert tree(origem["tmp"]) == before
    assert not target.exists()


def test_execute_copies_verifies_and_switches(env, origem):
    target = origem["tmp"] / "hd" / "Leitorum"
    source_hash = sha(origem["database"])
    report = mig.execute(context(origem, target), progress=lambda _m: None)
    assert report["result"] == "ok"
    assert report["source_sha256_unchanged"] is True
    assert sha(origem["database"]) == source_hash
    final = target / "db" / "caderno.db"
    assert final.is_file() and (target / MARKER_NAME).is_file()
    assert report["tables"] == mig.logical_snapshot(origem["database"])
    assert (target / "backups" / "caderno-backup-teste.zip").read_bytes() == b"pacote ficticio"
    assert any(p.name.startswith("caderno-pre-hd-") for p in (target / "backups").iterdir())
    assert not (target / "backups" / "ignorar.txt").exists()
    assert (target / "covers" / "capa-teste.webp").read_bytes() == b"RIFFxxxxWEBPficticio"
    env_text = origem["env_file"].read_text(encoding="utf-8")
    assert f"LEITORUM_STORAGE_ROOT={target}" in env_text and "ALLOW_REGISTRATION=false" in env_text
    assert Path(report["env_backup"]).read_text(encoding="utf-8") == ENV_TEXT
    assert list(target.glob("migration-report-*.json"))
    report_text = next(target.glob("migration-report-*.json")).read_text(encoding="utf-8")
    assert "Livro de Teste" not in report_text and "Resumo fictício" not in report_text
    # o app, apontado para a raiz nova, abre o banco migrado
    env.setenv("LEITORUM_STORAGE_ROOT", str(target))
    assert mig.verify_current()["result"] == "ok"
    client = TestClient(create_app())
    titles = [b["title"] for b in client.get("/api/books").json()]
    assert "Livro de Teste" in titles
    db_session._get_engine_for_path(final).dispose()
    # informação de rollback
    info = mig.rollback_info(context(origem, target))
    assert info["env_backups"] == [report["env_backup"]]


def test_replace_database_path_comments_the_old_line(env, origem):
    origem["env_file"].write_text(ENV_TEXT + "CADERNO_DATABASE_PATH=C:\\caminho\\ficticio.db\n", encoding="utf-8")
    target = origem["tmp"] / "hd" / "Leitorum"
    report = mig.execute(context(origem, target, replace_database_path=True), progress=lambda _m: None)
    assert report["result"] == "ok"
    text = origem["env_file"].read_text(encoding="utf-8")
    assert "\nCADERNO_DATABASE_PATH=" not in text and "# CADERNO_DATABASE_PATH removido" in text


# --- falhas injetadas (nada é trocado) --------------------------------------------------------


def run_failure(origem, target, ctx=None, expected_code=None):
    source_hash, env_hash = sha(origem["database"]), sha(origem["env_file"])
    with pytest.raises(mig.MigrationError) as error:
        mig.execute(ctx or context(origem, target), progress=lambda _m: None)
    if expected_code:
        assert error.value.code == expected_code
    assert_nothing_switched(origem, target, source_hash, env_hash)
    return error.value


def test_lock_present_stops_at_step_0(env, origem):
    lock = origem["tmp"] / "leitorum.lock"
    lock.write_text(json.dumps({"pid": os.getpid(), "port": 8000}), encoding="utf-8")
    target = origem["tmp"] / "hd" / "Leitorum"
    error = run_failure(origem, target, expected_code="server_running")
    assert error.step == "0" and not target.exists()


def test_port_in_use_stops_at_step_0(env, origem):
    target = origem["tmp"] / "hd" / "Leitorum"
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        ctx = context(origem, target, port=server.getsockname()[1])
        run_failure(origem, target, ctx, "server_running")


def test_existing_target_database_stops_at_step_0(env, origem):
    target = origem["tmp"] / "hd" / "Leitorum"
    (target / "db").mkdir(parents=True)
    (target / "db" / "caderno.db").write_bytes(b"outro banco")
    source_hash, env_hash = sha(origem["database"]), sha(origem["env_file"])
    with pytest.raises(mig.MigrationError) as error:
        mig.execute(context(origem, target), progress=lambda _m: None)
    assert error.value.code == "target_not_empty"
    assert (target / "db" / "caderno.db").read_bytes() == b"outro banco"
    assert sha(origem["database"]) == source_hash and sha(origem["env_file"]) == env_hash


def test_network_target_and_no_space_stop_at_step_0(env, origem, monkeypatch):
    info = mig.preconditions(context(origem, Path("\\\\servidor\\pasta\\Leitorum")))
    assert "target_network" in [p["code"] for p in info["problems"]]
    target = origem["tmp"] / "hd" / "Leitorum"
    monkeypatch.setattr(mig.shutil, "disk_usage", lambda _p: type("U", (), {"free": 1024})())
    run_failure(origem, target, expected_code="target_no_space")


def test_database_path_in_env_stops_at_step_0(env, origem):
    origem["env_file"].write_text(ENV_TEXT + "CADERNO_DATABASE_PATH=C:\\caminho\\ficticio.db\n", encoding="utf-8")
    run_failure(origem, origem["tmp"] / "hd" / "Leitorum", expected_code="database_path_in_env")


def test_source_not_upgraded_stops_at_step_0(env, origem):
    alembic = Config(str(config.BACKEND_DIR / "alembic.ini"))
    alembic.attributes["database_path"] = origem["database"]
    command.downgrade(alembic, "-1")
    run_failure(origem, origem["tmp"] / "hd" / "Leitorum", expected_code="source_not_upgraded")


def test_integrity_failure_cleans_target(env, origem, monkeypatch):
    monkeypatch.setattr(mig, "integrity_ok", lambda _p: False)
    target = origem["tmp"] / "hd" / "Leitorum"
    error = run_failure(origem, target, expected_code="integrity_failed")
    assert error.step == "4"
    assert not (target / "db" / "caderno.db.tmp").exists()


def test_logical_mismatch_cleans_target(env, origem, monkeypatch):
    real = mig.logical_snapshot
    calls = []

    def fake(path):
        calls.append(path)
        result = real(path)
        if len(calls) == 2:
            result["books"] = {"rows": 0, "sha256": "0" * 64}
        return result

    monkeypatch.setattr(mig, "logical_snapshot", fake)
    run_failure(origem, origem["tmp"] / "hd" / "Leitorum", expected_code="logical_hash_mismatch")


def test_backup_copy_hash_mismatch_keeps_env(env, origem, monkeypatch):
    real = mig.shutil.copyfile

    def corrupt(src, dst, *args, **kwargs):
        real(src, dst, *args, **kwargs)
        if str(dst).endswith(".zip"):
            Path(dst).write_bytes(b"corrompido")

    monkeypatch.setattr(mig.shutil, "copyfile", corrupt)
    error = run_failure(origem, origem["tmp"] / "hd" / "Leitorum", expected_code="copy_hash_mismatch")
    assert error.step == "6"


def test_switch_check_failure_restores_env(env, origem, monkeypatch):
    monkeypatch.setattr(mig, "verify_switch", lambda _ctx: {"database": "C:\\outro\\caderno.db", "storage_id": "x"})
    run_failure(origem, origem["tmp"] / "hd" / "Leitorum", expected_code="switch_check_failed")
