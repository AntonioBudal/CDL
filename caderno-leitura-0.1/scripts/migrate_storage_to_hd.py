"""Migração assistida do banco e dos backups para a raiz de armazenamento (HD de 1 TB), feature 090-A.

Uso (com o servidor parado), pela venv do backend:

    backend\\.venv\\Scripts\\python scripts\\migrate_storage_to_hd.py --target D:\\Leitorum --plan
    backend\\.venv\\Scripts\\python scripts\\migrate_storage_to_hd.py --target D:\\Leitorum --execute
    backend\\.venv\\Scripts\\python scripts\\migrate_storage_to_hd.py --verify
    backend\\.venv\\Scripts\\python scripts\\migrate_storage_to_hd.py --rollback-info

Garantias (contrato em specs/090-armazenamento-hd-cofre-cotas/contracts/migration-script.contract.md):

* o banco de origem só é aberto para leitura (``mode=ro``) e nunca é alterado nem apagado;
* a cópia usa a API de backup do SQLite e é conferida por ``integrity_check`` completo,
  ``foreign_key_check``, contagens por tabela, SHA-256 lógico das linhas e revisão Alembic;
* o caminho ativo só muda no fim (reescrita do ``.env``, com cópia do anterior) e é conferido num
  processo limpo; qualquer falha desfaz o que esta execução criou no destino e mantém o ``.env``;
* o relatório tem só números, caminhos e hashes, nunca conteúdo de estudos ou valores do ``.env``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core import server_lock  # noqa: E402
from app.core.storage import MARKER_NAME, StorageError, read_marker, verify_root, write_marker  # noqa: E402
from app.services.backups import calculate_file_sha256, copy_to_secondary, create_database_backup  # noqa: E402

GIB = 1024**3
PATH_KEYS = ("CADERNO_DATABASE_PATH", "CADERNO_COVERS_DIR", "CADERNO_AVATARS_DIR", "LEITORUM_STORAGE_ROOT")


class MigrationError(RuntimeError):
    def __init__(self, step: str, code: str, message: str) -> None:
        super().__init__(message)
        self.step = step
        self.code = code


@dataclass
class Context:
    target: Path
    source_db: Path
    source_backups: Path
    legacy_dirs: dict[str, Path]
    env_file: Path
    project_dir: Path = PROJECT_DIR
    lock_path: Path = server_lock.LOCK_PATH
    port: int = 8000
    replace_database_path: bool = False
    report: dict = field(default_factory=dict)


# --- utilidades -------------------------------------------------------------------------------


def now_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


def read_env(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines() if path.is_file() else []


def env_values(lines: list[str]) -> dict[str, str]:
    values = {}
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip().strip("'\"")
    return values


def head_revision() -> str:
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    return ScriptDirectory.from_config(Config(str(BACKEND_DIR / "alembic.ini"))).get_current_head()


def open_ro(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)


def db_revision(path: Path) -> str | None:
    conn = open_ro(path)
    try:
        row = conn.execute("SELECT version_num FROM alembic_version").fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()


def has_table(path: Path, name: str) -> bool:
    conn = open_ro(path)
    try:
        return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None
    finally:
        conn.close()


def tree_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    if not path.is_dir():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        return probe.connect_ex(("127.0.0.1", port)) == 0


def filesystem_name(path: Path) -> str | None:
    """Nome do sistema de arquivos da unidade (Windows); ``None`` se não for possível descobrir."""
    if os.name != "nt":
        return None
    import ctypes

    name = ctypes.create_unicode_buffer(64)
    ok = ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(path.anchor), None, 0, None, None, None, name, len(name)
    )
    return name.value if ok else None


def existing_ancestor(path: Path) -> Path:
    current = path
    while not current.exists() and current != current.parent:
        current = current.parent
    return current


# --- conferência lógica ------------------------------------------------------------------------


def user_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def _canonical(value) -> bytes:
    if value is None:
        return b"N"
    if isinstance(value, int):
        return b"I" + str(value).encode()
    if isinstance(value, float):
        return b"F" + value.hex().encode()
    if isinstance(value, bytes):
        return b"B" + value.hex().encode()
    return b"T" + str(value).encode("utf-8")


def table_digest(conn: sqlite3.Connection, table: str) -> tuple[int, str]:
    """Contagem e SHA-256 das linhas da tabela em ordem estável (rowid ou todas as colunas)."""
    quoted = '"' + table.replace('"', '""') + '"'
    columns = [r[1] for r in conn.execute(f"PRAGMA table_info({quoted})").fetchall()]
    try:
        cursor = conn.execute(f"SELECT * FROM {quoted} ORDER BY rowid")
    except sqlite3.OperationalError:  # WITHOUT ROWID
        order = ", ".join(str(i + 1) for i in range(len(columns)))
        cursor = conn.execute(f"SELECT * FROM {quoted} ORDER BY {order}")
    digest = hashlib.sha256()
    count = 0
    for row in cursor:
        count += 1
        for value in row:
            digest.update(_canonical(value))
            digest.update(b"\x1f")
        digest.update(b"\x1e")
    return count, digest.hexdigest()


def logical_snapshot(path: Path) -> dict[str, dict]:
    conn = open_ro(path)
    try:
        return {t: dict(zip(("rows", "sha256"), table_digest(conn, t), strict=True)) for t in user_tables(conn)}
    finally:
        conn.close()


def integrity_ok(path: Path) -> bool:
    conn = open_ro(path)
    try:
        result = conn.execute("PRAGMA integrity_check").fetchall()
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        return result == [("ok",)] and not fk
    finally:
        conn.close()


def copy_verified(source: Path, target: Path, created: list[Path]) -> str:
    """Copia byte a byte e confere o SHA-256; devolve o hash."""
    target.parent.mkdir(parents=True, exist_ok=True)
    expected = calculate_file_sha256(source)
    shutil.copyfile(source, target)
    created.append(target)
    if calculate_file_sha256(target) != expected:
        raise MigrationError("6", "copy_hash_mismatch", f"SHA-256 diferente na cópia de {source.name}")
    return expected


# --- etapas ------------------------------------------------------------------------------------


def preconditions(ctx: Context) -> dict:
    """Etapa 0: tudo que impede a migração; não grava nada."""
    problems = []
    info: dict = {}
    if server_lock.active_lock(ctx.lock_path) or port_in_use(ctx.port):
        problems.append(("server_running", "O Leitorum está em execução: pare o servidor antes de migrar."))
    target = ctx.target
    if not target.is_absolute():
        problems.append(("target_not_absolute", "O destino precisa ser um caminho absoluto, como D:\\Leitorum."))
    if str(target).startswith("\\\\"):
        problems.append(("target_network", "O destino não pode ser uma pasta de rede."))
    if target.is_absolute() and not Path(target.anchor).exists():
        problems.append(("target_drive_missing", "A unidade de destino não foi encontrada."))
    fs = filesystem_name(target) if target.is_absolute() and Path(target.anchor).exists() else None
    info["target_filesystem"] = fs
    if os.name == "nt" and fs is not None and fs.upper() != "NTFS":
        problems.append(("target_filesystem", f"A unidade de destino usa {fs}; é preciso NTFS."))
    if (target / "db" / "caderno.db").exists() or (target / MARKER_NAME).exists():
        problems.append(("target_not_empty", "O destino já tem um banco ou um marcador do Leitorum."))
    if target.is_absolute() and ctx.source_db.resolve().is_relative_to(target.resolve()):
        problems.append(("target_contains_source", "O banco de origem já está dentro do destino."))
    sizes = {
        "database": tree_size(ctx.source_db) + tree_size(ctx.source_db.with_name(ctx.source_db.name + "-wal")),
        "backups": tree_size(ctx.source_backups),
        "legacy": sum(tree_size(p) for p in ctx.legacy_dirs.values()),
    }
    needed = 3 * sum(sizes.values()) + 2 * GIB
    info["sizes_bytes"] = sizes
    info["needed_free_bytes"] = needed
    if target.is_absolute() and Path(target.anchor).exists():
        free = shutil.disk_usage(existing_ancestor(target)).free
        info["target_free_bytes"] = free
        if free < needed:
            problems.append(("target_no_space", "Espaço livre insuficiente no destino."))
    env = env_values(read_env(ctx.env_file))
    backend_env = env_values(read_env(BACKEND_DIR / ".env")) if ctx.env_file.parent == ctx.project_dir else {}
    if (env.get("CADERNO_DATABASE_PATH") or backend_env.get("CADERNO_DATABASE_PATH")) and not ctx.replace_database_path:
        problems.append(("database_path_in_env",
                         "O .env define CADERNO_DATABASE_PATH, que vence a raiz. Use --replace-database-path para trocá-lo."))
    if not ctx.source_db.is_file():
        problems.append(("source_missing", "O banco de origem não foi encontrado."))
    else:
        head = head_revision()
        revision = db_revision(ctx.source_db)
        info["source_revision"], info["head_revision"] = revision, head
        if revision != head or not has_table(ctx.source_db, "storage_settings"):
            problems.append(("source_not_upgraded",
                             "Atualize o banco (instalação normal, com snapshot automático) antes de migrar."))
    info["problems"] = [{"code": c, "message": m} for c, m in problems]
    return info


def switch_env(ctx: Context, stamp: str) -> Path | None:
    """Etapa 7: grava LEITORUM_STORAGE_ROOT no .env, guardando o anterior. Devolve o caminho do backup."""
    lines = read_env(ctx.env_file)
    backup = None
    if ctx.env_file.is_file():
        backup = ctx.env_file.with_name(f".env.bak-{stamp}")
        shutil.copyfile(ctx.env_file, backup)
    kept = []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line and not line.strip().startswith("#") else None
        if key == "LEITORUM_STORAGE_ROOT":
            continue
        if key == "CADERNO_DATABASE_PATH" and ctx.replace_database_path:
            kept.append("# CADERNO_DATABASE_PATH removido pela migração para o HD (ver .env.bak)")
            continue
        kept.append(line)
    kept.append(f"LEITORUM_STORAGE_ROOT={ctx.target}")
    newline = "\r\n" if ctx.env_file.is_file() and b"\r\n" in ctx.env_file.read_bytes() else "\n"
    ctx.env_file.write_text(newline.join(kept) + newline, encoding="utf-8", newline="")
    return backup


VERIFY_CODE = """
import json, sys
sys.path.insert(0, {backend!r})
from app.core.config import get_database_path, get_storage_root
from app.core.storage import verify_root
db = get_database_path()
root = get_storage_root()
print(json.dumps({{"database": str(db), "root": str(root), "storage_id": verify_root(root, db)}}))
"""


def verify_switch(ctx: Context) -> dict:
    """Confere, num processo limpo, que o .env novo resolve para o banco no destino."""
    env = {k: v for k, v in os.environ.items() if k not in PATH_KEYS}
    values = env_values(read_env(ctx.env_file))
    for key in PATH_KEYS:  # definidas explicitamente: o .env real do projeto não interfere
        env[key] = values.get(key, "")
    completed = subprocess.run(
        [sys.executable, "-c", VERIFY_CODE.format(backend=str(BACKEND_DIR))],
        capture_output=True, text=True, env=env, cwd=str(BACKEND_DIR), timeout=120,
    )
    if completed.returncode != 0:
        raise MigrationError("7", "switch_check_failed", "A conferência do novo caminho falhou num processo limpo.")
    return json.loads(completed.stdout.strip().splitlines()[-1])


def cleanup(created: list[Path]) -> None:
    for path in reversed(created):
        try:
            if path.is_file() or path.is_symlink():
                path.unlink()
            elif path.is_dir() and not any(path.iterdir()):
                path.rmdir()
        except OSError:
            pass
    for path in list(created):
        for suffix in ("-wal", "-shm"):
            Path(str(path) + suffix).unlink(missing_ok=True)


def execute(ctx: Context, progress: Callable[[str], None] = print) -> dict:
    info = preconditions(ctx)
    ctx.report.update(info)
    if info["problems"]:
        raise MigrationError("0", info["problems"][0]["code"], info["problems"][0]["message"])
    stamp = now_stamp()
    created: list[Path] = []
    source_hash_before = calculate_file_sha256(ctx.source_db)
    try:
        # 1. snapshot pré-migração verificado no disco de origem (+ segunda cópia, se configurada)
        progress("1/7 snapshot pré-migração")
        ctx.source_backups.mkdir(parents=True, exist_ok=True)
        snapshot = ctx.source_backups / f"caderno-pre-hd-{stamp}.db"
        create_database_backup(destination=snapshot, source=ctx.source_db)
        ctx.report["pre_migration_snapshot"] = {"path": str(snapshot), "sha256": calculate_file_sha256(snapshot),
                                                "secondary": str(copy_to_secondary(snapshot) or "")}
        # 2. raiz e marcador
        progress("2/7 marcador da raiz")
        for path in (ctx.target, ctx.target / "db", ctx.target / "backups"):
            if not path.exists():
                path.mkdir(parents=True)
                created.append(path)
        storage_id = write_marker(ctx.target)
        created.append(ctx.target / MARKER_NAME)
        ctx.report["storage_id"] = storage_id
        # 3. cópia pela API de backup
        progress("3/7 cópia do banco")
        temporary = ctx.target / "db" / "caderno.db.tmp"
        created.append(temporary)
        source = open_ro(ctx.source_db)
        try:
            destination = sqlite3.connect(temporary)
            try:
                source.backup(destination, pages=1024)
            finally:
                destination.close()
        finally:
            source.close()
        # 4. conferência
        progress("4/7 conferência")
        if not integrity_ok(temporary):
            raise MigrationError("4", "integrity_failed", "A cópia falhou no integrity_check ou no foreign_key_check.")
        before, after = logical_snapshot(ctx.source_db), logical_snapshot(temporary)
        if before != after:
            raise MigrationError("4", "logical_hash_mismatch", "As linhas da cópia diferem da origem.")
        if db_revision(temporary) != db_revision(ctx.source_db):
            raise MigrationError("4", "revision_mismatch", "A revisão Alembic da cópia difere da origem.")
        ctx.report["tables"] = after
        # 5. identidade na cópia e finalização
        progress("5/7 finalização do banco")
        conn = sqlite3.connect(temporary)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("INSERT INTO storage_settings (id, storage_id) VALUES (1, ?)", (storage_id,))
            conn.commit()
            if conn.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                raise MigrationError("5", "integrity_failed", "A cópia falhou no quick_check final.")
        finally:
            conn.close()
        final = ctx.target / "db" / "caderno.db"
        os.replace(temporary, final)
        created.append(final)
        # 6. backups e pastas legadas, conferidos por SHA-256
        progress("6/7 backups")
        copied = {}
        for item in sorted(ctx.source_backups.glob("*")):
            if item.is_file() and item.suffix.lower() in (".db", ".zip"):
                copied[f"backups/{item.name}"] = copy_verified(item, ctx.target / "backups" / item.name, created)
        for name, folder in ctx.legacy_dirs.items():
            for item in sorted(folder.rglob("*")):
                if item.is_file():
                    relative = item.relative_to(folder)
                    copied[f"{name}/{relative.as_posix()}"] = copy_verified(item, ctx.target / name / relative, created)
        ctx.report["copied_files"] = len(copied)
        # 7. troca do caminho ativo, conferida num processo limpo
        progress("7/7 troca do caminho ativo")
        if not verify_root(ctx.target, final) == storage_id:  # pragma: no cover - verify_root levanta antes
            raise MigrationError("7", "identity_mismatch", "Identidade da raiz diferente.")
        env_backup = switch_env(ctx, stamp)
        ctx.report["env_backup"] = str(env_backup) if env_backup else None
        try:
            checked = verify_switch(ctx)
            if Path(checked["database"]) != final or checked["storage_id"] != storage_id:
                raise MigrationError("7", "switch_check_failed", "O novo caminho não resolve para o banco migrado.")
        except Exception:
            if env_backup:
                shutil.copyfile(env_backup, ctx.env_file)
            else:
                ctx.env_file.unlink(missing_ok=True)
            raise
    except Exception as error:
        cleanup(created)
        if calculate_file_sha256(ctx.source_db) != source_hash_before:  # pragma: no cover - nunca deveria ocorrer
            ctx.report["source_changed"] = True
        if isinstance(error, (MigrationError, StorageError)):
            raise
        raise MigrationError("?", type(error).__name__, "Erro inesperado; nada foi trocado.") from error
    ctx.report["source_sha256_unchanged"] = calculate_file_sha256(ctx.source_db) == source_hash_before
    ctx.report["result"] = "ok"
    report_path = ctx.target / f"migration-report-{stamp}.json"
    report_path.write_text(json.dumps(ctx.report, ensure_ascii=False, indent=1), encoding="utf-8")
    return ctx.report


def verify_current() -> dict:
    from app.core.config import get_database_path, get_storage_root

    root, db = get_storage_root(), get_database_path()
    if root is None:
        raise MigrationError("verify", "no_root", "LEITORUM_STORAGE_ROOT não está configurado.")
    storage_id = verify_root(root, db)
    report = {"root": str(root), "database": str(db), "storage_id": storage_id,
              "integrity_ok": integrity_ok(db), "revision": db_revision(db), "head_revision": head_revision()}
    report["result"] = "ok" if report["integrity_ok"] and report["revision"] == report["head_revision"] else "falhou"
    return report


def rollback_info(ctx: Context) -> dict:
    backups = sorted(ctx.env_file.parent.glob(".env.bak-*"))
    return {
        "env_file": str(ctx.env_file),
        "env_backups": [str(p) for p in backups],
        "instructions": "Para voltar ao banco de origem (intacto), pare o servidor e copie o .env.bak mais recente "
                        "sobre o .env. Nada é apagado por este comando.",
    }


def build_context(args) -> Context:
    from app.core import config

    source_db = config.get_database_path()
    legacy = {}
    for name, getter_env in (("covers", "CADERNO_COVERS_DIR"), ("avatars", "CADERNO_AVATARS_DIR")):
        configured = os.environ.get(getter_env)
        folder = Path(configured) if configured else source_db.parent / name
        if folder.is_dir():
            legacy[name] = folder
    return Context(
        target=Path(args.target) if args.target else Path(),
        source_db=source_db,
        source_backups=source_db.parent / "backups",
        legacy_dirs=legacy,
        env_file=PROJECT_DIR / ".env",
        port=args.port,
        replace_database_path=args.replace_database_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migração do Leitorum para a raiz de armazenamento (HD)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--rollback-info", action="store_true")
    parser.add_argument("--target")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--replace-database-path", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if args.verify:
            result = verify_current()
        else:
            ctx = build_context(args)
            if args.rollback_info:
                result = rollback_info(ctx)
            elif not args.target:
                parser.error("--target é obrigatório em --plan e --execute")
            elif args.plan:
                result = {"mode": "plan", "source_database": str(ctx.source_db), "target": str(ctx.target),
                          **preconditions(ctx)}
            else:
                result = execute(ctx)
    except (MigrationError, StorageError, ValueError) as error:
        step = getattr(error, "step", "-")
        code = getattr(error, "code", type(error).__name__)
        print(json.dumps({"result": "falhou", "step": step, "code": code, "message": str(error)},
                         ensure_ascii=False, indent=1))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=1))
    if isinstance(result, dict) and result.get("problems"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
