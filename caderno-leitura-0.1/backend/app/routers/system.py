"""Painel de Sistema (F0.10.03): versão em execução, revisão do banco, backups e integridade.

Só metadados: nenhuma resposta traz conteúdo do acervo nem caminhos de arquivo do servidor.
"""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import __version__
from app.core.build_info import get_build_commit, get_expected_schema_revisions
from app.core.config import get_database_path, is_google_auth_enabled
from app.dependencies import AdminUser, CurrentUser, DatabaseSession
from app.schemas.system import BackupStatus, IntegrityResult, SystemStatus
from app.services.backups import verify_sqlite_integrity
from app.services.maintenance import auto_backup_status

router = APIRouter(prefix="/system", tags=["Sistema"])


def _schema_revision(session: DatabaseSession) -> str | None:
    try:
        return session.scalar(text("SELECT version_num FROM alembic_version LIMIT 1"))
    except SQLAlchemyError:
        session.rollback()
        return None


def _secure_delete_enabled(session: DatabaseSession) -> bool:
    try:
        return session.scalar(text("PRAGMA secure_delete")) == 1
    except SQLAlchemyError:
        session.rollback()
        return False


@router.get("/status", response_model=SystemStatus, summary="Versão, banco e proteções do servidor")
def get_system_status(session: DatabaseSession, current_user: CurrentUser, response: Response) -> SystemStatus:
    response.headers["Cache-Control"] = "no-store"
    backups = BackupStatus(**auto_backup_status()) if current_user.role == "admin" else None
    return SystemStatus(
        version=__version__,
        commit=get_build_commit(),
        schema_revision=_schema_revision(session),
        expected_schema_revisions=get_expected_schema_revisions(),
        google_auth_enabled=is_google_auth_enabled(),
        secure_delete=_secure_delete_enabled(session),
        backups=backups,
    )


@router.post("/integrity-check", response_model=IntegrityResult, summary="Verificar a integridade do banco")
def run_integrity_check(_admin: AdminUser, response: Response) -> IntegrityResult:
    """quick_check e foreign_key_check em modo somente leitura; a mensagem de falha não leva o caminho do banco."""
    response.headers["Cache-Control"] = "no-store"
    database = get_database_path()
    ok, message = verify_sqlite_integrity(database)
    detail = None
    if not ok:
        detail = (message or "Falha na verificação.").replace(str(database), "o banco").replace(str(database.resolve()), "o banco")
    return IntegrityResult(ok=ok, detail=detail, checked_at=datetime.now(UTC))
