"""Serviço de restauração segura de backups com validação de sandbox, Zip Slip e rollback."""
from contextlib import closing
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
import shutil
import sqlite3
from tempfile import TemporaryDirectory
import zipfile

from app.core.config import get_covers_dir, get_database_path
from app.schemas.backups import BackupManifestSchema, RestoreResultResponse
from app.services.backups import (
    calculate_file_sha256,
    create_database_backup,
    get_database_metadata_and_counts,
    verify_sqlite_integrity,
)
from app.services.maintenance import create_pre_restore_snapshot

logger = logging.getLogger(__name__)


def safe_extract_zip(zip_path: Path, target_dir: Path) -> list[str]:
    """Extrai um arquivo ZIP com proteção estrita contra Zip Slip e arquivos não autorizados.

    Raises:
        ValueError: Se houver tentativa de escape de diretório ou arquivo malicioso.
    """
    target_resolved = target_dir.resolve()
    extracted_members: list[str] = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = Path(member.filename)

            # 1. Rejeita caminhos absolutos
            if member_path.is_absolute() or member.filename.startswith(("/", "\\")):
                raise ValueError(f"Caminho absoluto proibido no pacote de backup: {member.filename}")

            destination = (target_dir / member_path).resolve()

            # 2. Defesa contra Zip Slip / Path Traversal
            if not destination.is_relative_to(target_resolved):
                raise ValueError(f"Tentativa de escape de diretório (Zip Slip) detectada: {member.filename}")

            # 3. Lista de arquivos autorizados
            parts = member_path.parts
            if not parts:
                continue

            top_level = parts[0]
            if top_level not in ("caderno.db", "manifest.json", "covers"):
                raise ValueError(f"Arquivo não autorizado contido no backup: {member.filename}")

            zf.extract(member, target_dir)
            extracted_members.append(member.filename)

    return extracted_members


def validate_extracted_bundle(extracted_dir: Path) -> tuple[BackupManifestSchema | None, str | None]:
    """Valida manifesto, somas SHA-256 e integridade do banco SQLite na sandbox.

    Returns:
        (manifest, None) se válido, ou (None, erro_descritivo) se falhar.
    """
    manifest_file = extracted_dir / "manifest.json"
    manifest: BackupManifestSchema | None = None

    if manifest_file.is_file():
        try:
            content = manifest_file.read_text(encoding="utf-8")
            data = json.loads(content)
            manifest = BackupManifestSchema.model_validate(data)
        except Exception as exc:
            return None, f"Manifesto inválido ou corrompido: {exc}"

        # Valida somas SHA-256 de todos os arquivos do manifesto
        for rel_path, expected_hash in manifest.files.items():
            file_path = extracted_dir / rel_path
            if not file_path.is_file():
                return None, f"Arquivo listado no manifesto não encontrado no pacote: {rel_path}"

            actual_hash = calculate_file_sha256(file_path)
            if actual_hash.lower() != expected_hash.lower():
                return None, f"Soma de verificação SHA-256 divergente para '{rel_path}'."

    db_file = extracted_dir / "caderno.db"
    if not db_file.is_file():
        return None, "O pacote de backup não contém a base de dados 'caderno.db'."

    # Valida integridade física e chaves estrangeiras
    is_ok, error_msg = verify_sqlite_integrity(db_file)
    if not is_ok:
        return None, f"Base SQLite corrompida: {error_msg}"

    return manifest, None


def restore_backup_package(
    package_file: Path,
    *,
    target_db: Path | None = None,
    target_covers: Path | None = None,
) -> RestoreResultResponse:
    """Restaura o acervo a partir de um pacote .zip ou arquivo .db isolado.

    Executa:
    1. Validação em sandbox temporária descartável.
    2. Criação de snapshot de salvaguarda compulsório do acervo ativo.
    3. Substituição atômica de dados.
    4. Rollback automático caso ocorra erro.

    Raises:
        ValueError: Em caso de erro de validação ou arquivo inválido.
        RuntimeError: Em caso de falha durante a restauração (após acionar rollback).
    """
    pkg_path = Path(package_file).resolve()
    if not pkg_path.is_file():
        raise FileNotFoundError(f"Arquivo de pacote não encontrado: {pkg_path}")

    active_db = (target_db or get_database_path()).resolve()
    active_covers = (target_covers or get_covers_dir(active_db)).resolve()

    with TemporaryDirectory(prefix="caderno-restore-sandbox-") as sandbox:
        sandbox_p = Path(sandbox)

        is_zip = zipfile.is_zipfile(pkg_path)
        manifest: BackupManifestSchema | None = None

        if is_zip:
            # Extração segura e validação de Zip Slip
            safe_extract_zip(pkg_path, sandbox_p)
            manifest, error_msg = validate_extracted_bundle(sandbox_p)
            if error_msg:
                raise ValueError(error_msg)
            extracted_db = sandbox_p / "caderno.db"
            extracted_covers = sandbox_p / "covers"
        else:
            # Suporte a arquivo .db direto
            extracted_db = sandbox_p / "caderno.db"
            shutil.copy2(pkg_path, extracted_db)
            is_ok, error_msg = verify_sqlite_integrity(extracted_db)
            if not is_ok:
                raise ValueError(f"O arquivo enviado não é uma base SQLite válida: {error_msg}")
            extracted_covers = None

        # 2. Snapshot compulsório de salvaguarda do acervo ativo
        pre_snapshot = create_pre_restore_snapshot(active_db)
        snapshot_name = pre_snapshot.name if pre_snapshot else "sem-dados-previos"

        # 3. Substituição atômica com proteção de rollback
        covers_restored = 0
        try:
            # Substituição do banco de dados ativo via SQLite Online Backup
            # (Garante transações seguras sem conflito de locks)
            create_database_backup(destination=active_db, source=extracted_db)

            # Restauração das capas se presentes no pacote
            if extracted_covers and extracted_covers.is_dir():
                active_covers.mkdir(parents=True, exist_ok=True)
                for cover_file in extracted_covers.iterdir():
                    if cover_file.is_file():
                        shutil.copy2(cover_file, active_covers / cover_file.name)
                        covers_restored += 1

            # Metadados e contagens finais do acervo restaurado
            schema_rev, counts = get_database_metadata_and_counts(active_db)
            created_at_str = manifest.created_at if manifest else None

            return RestoreResultResponse(
                success=True,
                message="Acervo restaurado com sucesso! A base e as capas foram atualizadas.",
                backup_created_at=created_at_str,
                pre_restore_snapshot=snapshot_name,
                schema_revision=schema_rev,
                counts=counts,
                covers_restored=covers_restored,
            )

        except Exception as exc:
            logger.error("Falha durante a substituição dos dados. Acionando rollback: %s", exc)
            if pre_snapshot and pre_snapshot.is_file():
                try:
                    create_database_backup(destination=active_db, source=pre_snapshot)
                    logger.info("Rollback concluído: acervo revertido para %s", snapshot_name)
                except Exception as rollback_exc:
                    logger.critical("FALHA CRÍTICA NO ROLLBACK: %s", rollback_exc)
            raise RuntimeError(
                f"Falha na restauração. O acervo anterior foi restaurado via rollback: {exc}"
            ) from exc
