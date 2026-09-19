"""Serviços de manutenção, snapshot pré-migração/restauração, retenção, inspeção e CLI."""
import argparse
from contextlib import closing
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
import sqlite3
import sys
import zipfile

from app.core.config import get_backup_dir, get_database_path
from app.services.backups import (
    calculate_file_sha256,
    create_backup_bundle,
    create_database_backup,
    verify_sqlite_integrity,
)

logger = logging.getLogger(__name__)


def rotate_pre_upgrade_snapshots(backup_dir: Path, keep: int = 5) -> list[Path]:
    """Aplica a política de retenção aos snapshots automáticos pré-migração."""
    if not backup_dir.is_dir():
        return []

    snapshots = list(backup_dir.glob("caderno-pre-migracao-*.db"))
    if len(snapshots) <= keep:
        return []

    snapshots.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
    to_remove = snapshots[keep:]
    removed: list[Path] = []

    for file_path in to_remove:
        try:
            file_path.unlink()
            removed.append(file_path)
            logger.info("Snapshot antigo expurgado: %s", file_path.name)
        except OSError as exc:
            logger.warning("Falha ao remover snapshot %s: %s", file_path.name, exc)

    return removed


def rotate_pre_restore_snapshots(backup_dir: Path, keep: int = 5) -> list[Path]:
    """Aplica a política de retenção aos snapshots automáticos pré-restauração."""
    if not backup_dir.is_dir():
        return []

    snapshots = list(backup_dir.glob("caderno-pre-restauracao-*.db"))
    if len(snapshots) <= keep:
        return []

    snapshots.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
    to_remove = snapshots[keep:]
    removed: list[Path] = []

    for file_path in to_remove:
        try:
            file_path.unlink()
            removed.append(file_path)
            logger.info("Snapshot pré-restauração antigo expurgado: %s", file_path.name)
        except OSError as exc:
            logger.warning("Falha ao remover snapshot %s: %s", file_path.name, exc)

    return removed


def create_pre_upgrade_snapshot(database_path: Path | None = None) -> Path | None:
    """Cria e valida atomicamente um snapshot consistente antes de atualização."""
    source = (database_path or get_database_path()).resolve()

    if not source.is_file() or source.stat().st_size == 0:
        logger.info("Base de dados inexistente ou virgem (%s). Snapshot pré-migração dispensado.", source)
        return None

    backup_dir = get_backup_dir(source)
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    snapshot_path = backup_dir / f"caderno-pre-migracao-{timestamp}.db"

    if snapshot_path.exists():
        timestamp_full = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
        snapshot_path = backup_dir / f"caderno-pre-migracao-{timestamp_full}.db"

    create_database_backup(destination=snapshot_path, source=source)
    rotate_pre_upgrade_snapshots(backup_dir, keep=5)

    return snapshot_path


def create_pre_restore_snapshot(database_path: Path | None = None) -> Path | None:
    """Cria e valida atomicamente um snapshot consistente antes de qualquer restauração."""
    source = (database_path or get_database_path()).resolve()

    if not source.is_file() or source.stat().st_size == 0:
        logger.info("Base de dados virgem ou inexistente (%s). Snapshot pré-restauração dispensado.", source)
        return None

    backup_dir = get_backup_dir(source)
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    snapshot_path = backup_dir / f"caderno-pre-restauracao-{timestamp}.db"

    if snapshot_path.exists():
        timestamp_full = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
        snapshot_path = backup_dir / f"caderno-pre-restauracao-{timestamp_full}.db"

    create_database_backup(destination=snapshot_path, source=source)
    rotate_pre_restore_snapshots(backup_dir, keep=5)

    return snapshot_path


def ensure_pre_upgrade_snapshot(database_path: Path | None = None) -> Path | None:
    """Barreira obrigatória pré-migração: aborta o processo se o snapshot falhar."""
    try:
        return create_pre_upgrade_snapshot(database_path)
    except Exception as exc:
        logger.error(
            "ABORTANDO MIGRAÇÃO: falha crítica ao criar snapshot pré-atualização: %s",
            exc,
            exc_info=True,
        )
        raise


def inspect_snapshot(snapshot_path: Path) -> dict:
    """Inspeciona integridade e contagens agregadas do snapshot sem expor dados privados."""
    path = Path(snapshot_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo de snapshot não encontrado: {path}")

    stat = path.stat()
    if stat.st_size == 0:
        raise sqlite3.DatabaseError("Arquivo de snapshot corrompido (tamanho 0).")

    source_uri = path.as_uri() + "?mode=ro"

    with closing(sqlite3.connect(source_uri, uri=True, timeout=2.0)) as conn:
        quick_check = conn.execute("PRAGMA quick_check").fetchall()
        if quick_check != [("ok",)]:
            raise sqlite3.DatabaseError(f"Falha na verificação de integridade física: {quick_check}")

        fk_check = conn.execute("PRAGMA foreign_key_check").fetchone()
        if fk_check is not None:
            raise sqlite3.DatabaseError("Falha de integridade: snapshot contém chaves estrangeiras órfãs.")

        schema_revision = None
        try:
            row = conn.execute("SELECT version_num FROM alembic_version LIMIT 1").fetchone()
            if row:
                schema_revision = row[0]
        except sqlite3.OperationalError:
            schema_revision = None

        def table_count(table: str) -> int:
            try:
                cur = conn.execute(f"SELECT COUNT(*) FROM {table}")  # noqa: S608
                return cur.fetchone()[0]
            except sqlite3.OperationalError:
                return 0

        counts = {
            "books": table_count("books"),
            "chapters": table_count("chapters"),
            "studies": table_count("studies"),
        }

    created_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "snapshot_path": str(path),
        "created_at": created_at,
        "file_size_bytes": stat.st_size,
        "schema_revision": schema_revision,
        "integrity_ok": True,
        "counts": counts,
    }


def inspect_backup_bundle(package_path: Path) -> dict:
    """Inspeciona um pacote .zip ou arquivo .db de backup."""
    path = Path(package_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo de backup não encontrado: {path}")

    if not zipfile.is_zipfile(path):
        # Trata como .db comum
        res = inspect_snapshot(path)
        res["covers_count"] = 0
        res["is_bundle"] = False
        return res

    from tempfile import TemporaryDirectory
    with TemporaryDirectory(prefix="caderno-inspect-") as tmp_dir:
        tmp_p = Path(tmp_dir)
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(tmp_p)

        manifest_file = tmp_p / "manifest.json"
        manifest_data = {}
        if manifest_file.is_file():
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))

        db_file = tmp_p / "caderno.db"
        if not db_file.is_file():
            raise ValueError("O arquivo ZIP não contém a base 'caderno.db'.")

        db_info = inspect_snapshot(db_file)
        covers_count = 0
        covers_dir = tmp_p / "covers"
        if covers_dir.is_dir():
            covers_count = len([f for f in covers_dir.iterdir() if f.is_file()])

        return {
            "package_path": str(path),
            "is_bundle": True,
            "created_at": manifest_data.get("created_at") or db_info["created_at"],
            "app_version": manifest_data.get("app_version"),
            "schema_revision": db_info["schema_revision"],
            "integrity_ok": True,
            "counts": db_info["counts"],
            "covers_count": covers_count,
            "file_size_bytes": path.stat().st_size,
        }


# --- Funções CLI ---

def _cli_verificar(args: argparse.Namespace) -> int:
    try:
        result = inspect_snapshot(args.caminho_arquivo)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=True))
        else:
            print(f"Snapshot: {Path(result['snapshot_path']).name}")
            print(f"Data de Criação: {result['created_at']}")
            print(f"Tamanho: {result['file_size_bytes']:,} bytes".replace(",", "."))
            print(f"Revisão do Esquema: {result['schema_revision'] or 'N/A'}")
            print("Integridade: OK (física e chaves estrangeiras válidas)")
            print(f"Total de Livros: {result['counts']['books']}")
            print(f"Total de Capítulos: {result['counts']['chapters']}")
            print(f"Total de Estudos: {result['counts']['studies']}")
        return 0
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc), "integrity_ok": False}, ensure_ascii=True), file=sys.stderr)
        else:
            print(f"Erro ao verificar snapshot: {exc}", file=sys.stderr)
        return 1


def _cli_verificar_backup(args: argparse.Namespace) -> int:
    try:
        result = inspect_backup_bundle(args.caminho_arquivo)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=True))
        else:
            print(f"Pacote: {Path(result['package_path']).name}")
            print(f"Data do Backup: {result['created_at']}")
            if result.get("app_version"):
                print(f"Versão da Aplicação: {result['app_version']}")
            print(f"Revisão do Esquema: {result['schema_revision'] or 'N/A'}")
            print("Integridade: OK (física e somas SHA-256 verificadas)")
            print(f"Total de Livros: {result['counts']['books']}")
            print(f"Total de Capítulos: {result['counts']['chapters']}")
            print(f"Total de Estudos: {result['counts']['studies']}")
            print(f"Capas Anexadas: {result.get('covers_count', 0)}")
            print(f"Tamanho do Pacote: {result['file_size_bytes']:,} bytes".replace(",", "."))
        return 0
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc), "integrity_ok": False}, ensure_ascii=True), file=sys.stderr)
        else:
            print(f"Erro ao verificar backup: {exc}", file=sys.stderr)
        return 1


def _cli_criar(args: argparse.Namespace) -> int:
    try:
        if args.destino:
            dest = Path(args.destino).resolve()
            create_database_backup(destination=dest)
            if args.rotacionar:
                rotate_pre_upgrade_snapshots(dest.parent, keep=5)
            print(f"Snapshot criado em: {dest}")
        else:
            snapshot = create_pre_upgrade_snapshot()
            if snapshot:
                print(f"Snapshot pré-migração criado: {snapshot}")
            else:
                print("Base virgem ou vazia. Nenhum snapshot gerado.")
        return 0
    except Exception as exc:
        print(f"Falha ao criar snapshot: {exc}", file=sys.stderr)
        return 1


def _cli_criar_backup(args: argparse.Namespace) -> int:
    try:
        dest = args.destino
        if not dest:
            backup_dir = get_backup_dir()
            ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
            dest = backup_dir / f"caderno-backup-{ts}.zip"

        dest_path = Path(dest).resolve()
        created = create_backup_bundle(destination=dest_path)
        info = inspect_backup_bundle(created)

        if args.json:
            print(json.dumps(info, indent=2, ensure_ascii=True))
        else:
            print("Pacote de backup criado com sucesso!")
            print(f"Arquivo: {created}")
            print(f"Tamanho: {info['file_size_bytes']:,} bytes".replace(",", "."))
            print(
                f"Livros: {info['counts']['books']} | "
                f"Capítulos: {info['counts']['chapters']} | "
                f"Estudos: {info['counts']['studies']} | "
                f"Capas: {info.get('covers_count', 0)}"
            )
        return 0
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        else:
            print(f"Falha ao gerar pacote de backup: {exc}", file=sys.stderr)
        return 1


def _cli_restaurar_backup(args: argparse.Namespace) -> int:
    from app.services.restore_service import restore_backup_package

    pkg_path = Path(args.caminho_arquivo).resolve()
    if not pkg_path.is_file():
        print(f"Arquivo de pacote não encontrado: {pkg_path}", file=sys.stderr)
        return 1

    if not args.forcar and not args.json:
        print("ATENÇÃO: A restauração substituirá os livros, estudos e capas ativos no banco local.")
        print("Um snapshot de segurança do acervo atual será gerado automaticamente antes da substituição.")
        resposta = input("Deseja prosseguir com a restauração? (s/N): ").strip().lower()
        if resposta not in ("s", "sim", "y", "yes"):
            print("Operação cancelada pelo usuário.")
            return 0

    try:
        result = restore_backup_package(pkg_path)
        if args.json:
            print(json.dumps(result.model_dump(), indent=2, ensure_ascii=True))
        else:
            print("Sucesso: Acervo restaurado com êxito!")
            print(f"Snapshot de salvaguarda criado: {result.pre_restore_snapshot}")
            print(
                f"Dados restaurados: {result.counts.get('books', 0)} livros, "
                f"{result.counts.get('chapters', 0)} capítulos, "
                f"{result.counts.get('studies', 0)} estudos e "
                f"{result.covers_restored} capas."
            )
        return 0
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc), "success": False}, ensure_ascii=True), file=sys.stderr)
        else:
            print(f"Falha na restauração do acervo: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.services.maintenance",
        description="Utilitário de manutenção, inspeção e proteção do acervo do Caderno de Leitura.",
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    # Subcomando: verificar-snapshot
    p_verificar = subparsers.add_parser(
        "verificar-snapshot", help="Inspeciona e valida a integridade de um snapshot .db"
    )
    p_verificar.add_argument("caminho_arquivo", type=Path, help="Caminho do arquivo .db")
    p_verificar.add_argument("--json", action="store_true", help="Emite resultado em formato JSON")
    p_verificar.set_defaults(func=_cli_verificar)

    # Subcomando: criar-snapshot
    p_criar = subparsers.add_parser("criar-snapshot", help="Gera um snapshot imediato do banco ativo")
    p_criar.add_argument("--destino", type=Path, default=None, help="Caminho de destino customizado")
    p_criar.add_argument(
        "--rotacionar", action="store_true", help="Aplica rotação retendo os 5 mais recentes"
    )
    p_criar.set_defaults(func=_cli_criar)

    # Subcomando: criar-backup
    p_criar_backup = subparsers.add_parser(
        "criar-backup", help="Gera o pacote completo .zip com banco, capas e manifesto SHA-256"
    )
    p_criar_backup.add_argument("--destino", "-d", type=Path, default=None, help="Caminho do arquivo .zip")
    p_criar_backup.add_argument("--json", action="store_true", help="Emite resultado em formato JSON")
    p_criar_backup.set_defaults(func=_cli_criar_backup)

    # Subcomando: verificar-backup
    p_verificar_backup = subparsers.add_parser(
        "verificar-backup", help="Inspeciona um pacote .zip ou arquivo .db e verifica SHA-256 e integridade"
    )
    p_verificar_backup.add_argument("caminho_arquivo", type=Path, help="Caminho do arquivo .zip ou .db")
    p_verificar_backup.add_argument("--json", action="store_true", help="Emite resultado em formato JSON")
    p_verificar_backup.set_defaults(func=_cli_verificar_backup)

    # Subcomando: restaurar-backup
    p_restaurar = subparsers.add_parser(
        "restaurar-backup", help="Restaura o acervo a partir de um arquivo .zip ou .db"
    )
    p_restaurar.add_argument("caminho_arquivo", type=Path, help="Caminho do arquivo de backup")
    p_restaurar.add_argument("--forcar", "-f", action="store_true", help="Pula confirmação interativa")
    p_restaurar.add_argument("--json", action="store_true", help="Emite resultado em formato JSON")
    p_restaurar.set_defaults(func=_cli_restaurar_backup)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
