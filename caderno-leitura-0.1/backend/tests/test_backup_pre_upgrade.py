"""Testes de isolamento, integridade e atomicidade do snapshot pré-atualização."""
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, get_backup_dir, get_database_path
from app.db.session import create_sqlite_engine
from app.models import Book, Chapter, Study
from app.services.backups import create_database_backup


@pytest.fixture
def synthetic_db(tmp_path):
    """Cria um banco SQLite temporário isolado com dados sintéticos."""
    db_dir = tmp_path / "acervo teste ação 100%"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "caderno.db"

    # Aplica migrações iniciais no banco temporário
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.attributes["database_path"] = db_path
    command.upgrade(alembic_cfg, "head")

    # Popula dados sintéticos (fictícios)
    engine = create_sqlite_engine(db_path)
    try:
        with Session(engine) as session:
            book = Book(title="Livro Sintético", author="Autor Teste")
            session.add(book)
            session.flush()

            chapter = Chapter(book=book, name="Capítulo 1", position=1)
            session.add(chapter)
            session.flush()

            study = Study(
                chapter=chapter,
                title="Estudo Sintético",
                location="p. 10",
                source_response="## Resumo Sintético\nTexto teste confidencial.",
                summary="Resumo privado confidencial.",
                explanation="Explicação privada confidencial.",
                concepts="Conceito A.",
                references="Referência fictícia.",
                notes="Minha anotação estritamente pessoal e confidencial.",
            )
            session.add(study)
            session.commit()
    finally:
        engine.dispose()

    return db_path, alembic_cfg


def test_backup_dir_resolution(tmp_path):
    """T001/T003: Valida a resolução do diretório de backup com base no banco."""
    custom_db = tmp_path / "custom" / "caderno.db"
    backup_dir = get_backup_dir(custom_db)
    assert backup_dir == (tmp_path / "custom" / "backups").resolve()
    assert backup_dir.is_dir()


def test_relative_database_path_rejected(monkeypatch):
    """T004/T012: Valida rejeição estrita de caminho relativo em CADERNO_DATABASE_PATH."""
    monkeypatch.setenv("CADERNO_DATABASE_PATH", "dados/caderno.db")
    with pytest.raises(ValueError, match="absoluto"):
        get_database_path()


def test_canonical_path_resolution_with_accents_and_spaces(tmp_path, monkeypatch):
    """T011: Valida resolução canônica em diretórios com espaços e acentos no Windows."""
    special_path = tmp_path / "Pasta com Acentuação e Espaço 100%" / "caderno.db"
    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(special_path))
    resolved = get_database_path()
    assert resolved == special_path.resolve()
    assert resolved.is_absolute()


def test_create_pre_upgrade_snapshot_success(synthetic_db):
    """T006: Valida criação atômica e verificação de integridade do snapshot pré-migração."""
    from app.services.maintenance import create_pre_upgrade_snapshot, inspect_snapshot

    db_path, _ = synthetic_db
    snapshot_path = create_pre_upgrade_snapshot(database_path=db_path)

    assert snapshot_path is not None
    assert snapshot_path.is_file()
    assert snapshot_path.parent == get_backup_dir(db_path)
    assert snapshot_path.name.startswith("caderno-pre-migracao-")
    assert snapshot_path.name.endswith(".db")

    # Verifica journal_mode DELETE na cópia autossuficiente
    with sqlite3.connect(snapshot_path) as conn:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode.lower() == "delete"

    # Inspeciona metadados
    diag = inspect_snapshot(snapshot_path)
    assert diag["integrity_ok"] is True
    assert diag["counts"]["books"] == 1
    assert diag["counts"]["chapters"] == 1
    assert diag["counts"]["studies"] == 1


def test_create_pre_upgrade_snapshot_virgin_db(tmp_path):
    """T006: Base virgem ou inexistente não gera snapshot (retorna None)."""
    from app.services.maintenance import create_pre_upgrade_snapshot

    virgin_db = tmp_path / "inexistente" / "caderno.db"
    assert create_pre_upgrade_snapshot(database_path=virgin_db) is None


def test_pre_upgrade_snapshot_abort_on_failure(synthetic_db, monkeypatch):
    """T007: Se a criação ou validação do snapshot falha, a operação é abortada sem tocar no banco."""
    from app.services import maintenance
    from app.services.maintenance import ensure_pre_upgrade_snapshot

    db_path, alembic_cfg = synthetic_db
    initial_mtime = db_path.stat().st_mtime
    initial_size = db_path.stat().st_size

    def broken_backup(*args, **kwargs):
        raise RuntimeError("Simulação de falha catastrófica no disco/backup")

    monkeypatch.setattr(maintenance, "create_database_backup", broken_backup)

    with pytest.raises(RuntimeError, match="Simulação de falha catastrófica"):
        ensure_pre_upgrade_snapshot(db_path)

    # O banco original deve permanecer rigorosamente inalterado
    assert db_path.stat().st_mtime == initial_mtime
    assert db_path.stat().st_size == initial_size


def test_rotate_pre_upgrade_snapshots(tmp_path):
    """T009: Rotação automática mantém os 5 snapshots mais recentes e não toca em backups manuais."""
    from app.services.maintenance import rotate_pre_upgrade_snapshots

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Cria 7 snapshots com timestamps sucessivos
    created_snapshots = []
    for day in range(1, 8):
        file_path = backup_dir / f"caderno-pre-migracao-2026090{day}-120000.db"
        file_path.write_text("conteudo simulado", encoding="utf-8")
        # Ajusta mtime artificialmente para garantir ordem temporal
        os.utime(file_path, (time.time() + day * 10, time.time() + day * 10))
        created_snapshots.append(file_path)

    # Cria backups manuais e arquivos estranhos que NÃO devem ser tocados
    manual_backup = backup_dir / "caderno-manual-20260901.db"
    manual_backup.write_text("backup manual", encoding="utf-8")
    extra_file = backup_dir / "notas.txt"
    extra_file.write_text("notas", encoding="utf-8")

    removed = rotate_pre_upgrade_snapshots(backup_dir, keep=5)

    assert len(removed) == 2
    # Os dois mais antigos devem ter sido removidos
    assert created_snapshots[0] in removed
    assert created_snapshots[1] in removed
    assert not created_snapshots[0].exists()
    assert not created_snapshots[1].exists()

    # Os 5 mais recentes permanecem
    for s in created_snapshots[2:]:
        assert s.exists()

    # Arquivos manuais preservados
    assert manual_backup.exists()
    assert extra_file.exists()


def test_inspect_snapshot_absolute_privacy(synthetic_db):
    """T014: Inspeciona snapshot garantindo privacidade absoluta (sem dados sensíveis)."""
    from app.services.maintenance import create_pre_upgrade_snapshot, inspect_snapshot

    db_path, _ = synthetic_db
    snapshot_path = create_pre_upgrade_snapshot(database_path=db_path)

    diag = inspect_snapshot(snapshot_path)

    # Serializa para texto completo e valida ausência de termos privados
    diag_str = json.dumps(diag, ensure_ascii=False)

    private_terms = [
        "confidencial",
        "pessoal",
        "Resumo privado",
        "Explicação privada",
        "Minha anotação",
        "Livro Sintético",
        "Autor Teste",
        "Estudo Sintético",
    ]
    for term in private_terms:
        assert term not in diag_str, f"Termo privado '{term}' vazou no relatório de diagnóstico!"

    assert diag["integrity_ok"] is True
    assert diag["counts"]["books"] == 1
    assert diag["counts"]["chapters"] == 1
    assert diag["counts"]["studies"] == 1
    assert "schema_revision" in diag


def test_cli_maintenance_commands(synthetic_db, tmp_path):
    """T015/T016: Testa utilitário CLI de verificação e criação de snapshot."""
    db_path, _ = synthetic_db
    from app.services.maintenance import create_pre_upgrade_snapshot
    snapshot_path = create_pre_upgrade_snapshot(database_path=db_path)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    # Teste CLI: verificar-snapshot com --json
    cmd_json = [
        sys.executable,
        "-m",
        "app.services.maintenance",
        "verificar-snapshot",
        str(snapshot_path),
        "--json",
    ]
    res_json = subprocess.run(
        cmd_json, env=env, capture_output=True, text=True, check=False, encoding="utf-8"
    )
    assert res_json.returncode == 0
    data = json.loads(res_json.stdout)
    assert data["integrity_ok"] is True
    assert data["counts"]["books"] == 1

    # Teste CLI: verificar-snapshot formato legível
    cmd_text = [
        sys.executable,
        "-m",
        "app.services.maintenance",
        "verificar-snapshot",
        str(snapshot_path),
    ]
    res_text = subprocess.run(
        cmd_text, env=env, capture_output=True, text=True, check=False, encoding="utf-8"
    )
    assert res_text.returncode == 0
    assert "Integridade: OK" in res_text.stdout
    assert "Total de Livros: 1" in res_text.stdout

    # Teste CLI com arquivo corrompido
    corrupt_file = tmp_path / "corrupto.db"
    corrupt_file.write_bytes(b"conteudo nao sqlite corrompido")
    res_corrupt = subprocess.run(
        [sys.executable, "-m", "app.services.maintenance", "verificar-snapshot", str(corrupt_file)],
        env=env, capture_output=True, text=True, check=False, encoding="utf-8"
    )
    assert res_corrupt.returncode != 0


def test_alembic_upgrade_automatically_creates_snapshot(synthetic_db):
    """T010: Prova que a execução de migração via Alembic dispara o snapshot automaticamente."""
    db_path, alembic_cfg = synthetic_db
    backup_dir = get_backup_dir(db_path)

    # Limpa backups prévios para aferição limpa
    for f in backup_dir.glob("caderno-pre-migracao-*.db"):
        f.unlink()

    # Re-executa upgrade head via Alembic
    command.upgrade(alembic_cfg, "head")

    snapshots = list(backup_dir.glob("caderno-pre-migracao-*.db"))
    assert len(snapshots) == 1
    assert snapshots[0].is_file()
    assert snapshots[0].stat().st_size > 0


def test_iniciar_rejects_relative_database_path(tmp_path):
    """T013: Verifica que iniciar.py rejeita caminho relativo com mensagem limpa e exit code 1."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    env["CADERNO_DATABASE_PATH"] = "relativo/caderno.db"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run(
        [sys.executable, str(BACKEND_DIR.parent / "iniciar.py"), "--port", "9999"],
        env=env,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
    )
    assert res.returncode == 1
    assert "Erro na configuração do banco de dados" in res.stderr


def test_alembic_upgrade_with_existing_referenced_rows(tmp_path):
    """Valida migração batch de tabelas que possuem relacionamentos de chave estrangeira existentes."""
    import sqlite3
    from alembic.config import Config
    from app.core.config import BACKEND_DIR

    db_path = tmp_path / "com_dados" / "caderno.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.attributes["database_path"] = db_path

    # Aplica apenas a migração inicial 0001
    command.upgrade(alembic_cfg, "0001_initial")

    # Insere dados com relacionamento livro -> capítulo
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("INSERT INTO books (id, title, author) VALUES (1, 'Livro Existente', 'Autor Antigo')")
    conn.execute("INSERT INTO chapters (id, book_id, name, position) VALUES (1, 1, 'Capítulo 1', 0)")
    conn.commit()
    conn.close()

    # Executa upgrade head (0002_add_metadata_concurrency)
    command.upgrade(alembic_cfg, "head")

    # Verifica que a migração aplicou com sucesso e os dados continuam íntegros
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, subtitle, year FROM books WHERE id = 1")
    row = cursor.fetchone()
    assert row[0] == 1
    assert row[1] == "Livro Existente"
    assert row[2] == ""
    assert row[3] is None

    cursor.execute("PRAGMA foreign_key_check")
    violations = cursor.fetchall()
    assert len(violations) == 0
    conn.close()


