"""Serviço de geração e validação de cópias e pacotes de backup do Caderno de Leitura."""
from contextlib import closing
from datetime import UTC, datetime
import hashlib
import json
import logging
from pathlib import Path
import sqlite3
from time import monotonic
import zipfile

from app.core.config import get_covers_dir, get_database_path
from app.schemas.backups import BackupCounts, BackupManifestSchema

logger = logging.getLogger(__name__)


def calculate_file_sha256(file_path: Path) -> str:
    """Calcula a soma de verificação SHA-256 de um arquivo local."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_sqlite_integrity(database_path: Path) -> tuple[bool, str | None]:
    """Verifica a integridade física e chaves estrangeiras de um banco SQLite.

    Returns:
        (True, None) se íntegro, ou (False, mensagem_de_erro) se corrompido/inválido.
    """
    path = Path(database_path).resolve()
    if not path.is_file():
        return False, f"Arquivo de banco não encontrado: {path}"

    if path.stat().st_size == 0:
        return False, "Arquivo de banco está vazio (tamanho 0)."

    source_uri = path.as_uri() + "?mode=ro"
    try:
        with closing(sqlite3.connect(source_uri, uri=True, timeout=2.0)) as conn:
            # 1. Integridade física da B-Tree
            quick = conn.execute("PRAGMA quick_check").fetchall()
            if quick != [("ok",)]:
                return False, f"Falha de integridade física: {quick}"

            # 2. Integridade referencial de chaves estrangeiras
            fk_check = conn.execute("PRAGMA foreign_key_check").fetchone()
            if fk_check is not None:
                return False, "O banco contém chaves estrangeiras órfãs."

        return True, None
    except Exception as exc:
        return False, f"Erro ao acessar banco para verificação: {exc}"


def get_database_metadata_and_counts(database_path: Path) -> tuple[str | None, dict[str, int]]:
    """Extrai revisão do Alembic e contagens agregadas sem ler dados privados."""
    path = Path(database_path).resolve()
    source_uri = path.as_uri() + "?mode=ro"

    counts = {"books": 0, "chapters": 0, "studies": 0}
    schema_revision = None

    with closing(sqlite3.connect(source_uri, uri=True, timeout=2.0)) as conn:
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

        counts["books"] = table_count("books")
        counts["chapters"] = table_count("chapters")
        counts["studies"] = table_count("studies")

    return schema_revision, counts


def create_database_backup(
    destination: Path,
    *,
    source: Path | None = None,
    timeout_seconds: float = 30.0,
) -> None:
    """Cria uma cópia consistente e validada do banco SQLite usando a Online Backup API.

    Args:
        destination: Caminho de destino para a cópia gerada.
        source: Caminho do banco de origem (se omitido, usa get_database_path()).
        timeout_seconds: Tempo limite máximo de espera em caso de contenção.

    Raises:
        FileNotFoundError: Se o banco de origem não existir.
        sqlite3.DatabaseError: Se o banco estiver vazio ou a cópia falhar na verificação.
        TimeoutError: Se o banco permanecer ocupado além do timeout estipulado.
    """
    source_path = (source or get_database_path()).resolve()

    if not source_path.is_file():
        raise FileNotFoundError(f"Banco de dados não encontrado: {source_path}")

    if source_path.stat().st_size == 0:
        raise sqlite3.DatabaseError("O arquivo do banco está vazio.")

    dest_path = Path(destination).resolve()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_existed_before = dest_path.exists()

    deadline = monotonic() + timeout_seconds

    def check_progress(status: int, _remaining: int, _total: int) -> None:
        if status != sqlite3.SQLITE_DONE and monotonic() >= deadline:
            raise TimeoutError("O banco permaneceu ocupado durante o backup.")

    source_uri = source_path.as_uri() + "?mode=ro"

    try:
        with closing(
            sqlite3.connect(
                source_uri,
                uri=True,
                timeout=1.0,
                autocommit=True,
            )
        ) as original:
            with closing(
                sqlite3.connect(
                    dest_path,
                    timeout=1.0,
                    autocommit=True,
                )
            ) as snapshot:
                original.backup(
                    snapshot,
                    pages=256,
                    progress=check_progress,
                    sleep=0.05,
                )

                # Configura a cópia no modo DELETE padrão para autossuficiência de arquivo único
                snapshot.execute("PRAGMA journal_mode=DELETE")

        # Verificação pós-cópia
        is_ok, error_msg = verify_sqlite_integrity(dest_path)
        if not is_ok:
            raise sqlite3.DatabaseError(error_msg or "Falha de integridade na cópia.")

    except Exception:
        if not dest_existed_before and dest_path.exists():
            try:
                dest_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def create_backup_bundle(
    destination: Path,
    *,
    source_db: Path | None = None,
    covers_dir: Path | None = None,
    app_version: str = "0.3.0",
) -> Path:
    """Gera um pacote universal compactado .zip contendo caderno.db, covers/ e manifest.json.

    Args:
        destination: Caminho de destino para o arquivo .zip gerado.
        source_db: Caminho da base SQLite de origem (se None, usa get_database_path()).
        covers_dir: Diretório de capas (se None, usa get_covers_dir()).
        app_version: Versão informada da aplicação.

    Returns:
        Caminho resolvido do arquivo .zip gerado.
    """
    dest_path = Path(destination).resolve()
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    db_path = (source_db or get_database_path()).resolve()
    covers_path = (covers_dir or get_covers_dir(db_path)).resolve()

    from tempfile import TemporaryDirectory
    with TemporaryDirectory(prefix="caderno-bundle-") as tmp_dir:
        tmp_p = Path(tmp_dir)
        temp_db = tmp_p / "caderno.db"

        # 1. Cria cópia consistente do banco via SQLite Backup API
        create_database_backup(destination=temp_db, source=db_path)

        # 2. Extrai metadados do banco
        schema_rev, counts = get_database_metadata_and_counts(temp_db)

        # 3. Mapeia arquivos e calcula hashes SHA-256
        file_hashes: dict[str, str] = {
            "caderno.db": calculate_file_sha256(temp_db),
        }

        # 4. Mapeia capas existentes
        cover_files: list[Path] = []
        if covers_path.is_dir():
            for cover in covers_path.iterdir():
                if cover.is_file() and not cover.name.startswith("."):
                    rel_name = f"covers/{cover.name}"
                    file_hashes[rel_name] = calculate_file_sha256(cover)
                    cover_files.append(cover)

        # 5. Monta e grava o manifest.json
        manifest = BackupManifestSchema(
            app_version=app_version,
            schema_version=schema_rev,
            created_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            generator="Caderno de Leitura Backup Engine",
            counts=BackupCounts(
                books=counts.get("books", 0),
                chapters=counts.get("chapters", 0),
                studies=counts.get("studies", 0),
                covers=len(cover_files),
            ),
            files=file_hashes,
        )

        temp_manifest = tmp_p / "manifest.json"
        temp_manifest.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

        # 6. Cria o arquivo ZIP comprimido
        with zipfile.ZipFile(dest_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(temp_manifest, arcname="manifest.json")
            zf.write(temp_db, arcname="caderno.db")
            for cover in cover_files:
                zf.write(cover, arcname=f"covers/{cover.name}")

    return dest_path
