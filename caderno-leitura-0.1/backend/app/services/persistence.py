from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any, TypeVar

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.base import Base

from app.errors import ConcurrencyConflictError

logger = logging.getLogger(__name__)

Record = TypeVar("Record", bound=Base)


def get_or_404(session: Session, model: type[Record], record_id: int, label: str) -> Record:
    record = session.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{label} não encontrado.")
    return record


def get_user_resource_or_404(
    session: Session,
    model: type[Record],
    record_id: int | str,
    user_id: str,
    label: str,
    *,
    allow_global: bool = False,
) -> Record:
    """Retorna um recurso pelo ID garantindo que pertença estritamente ao user_id informado.

    Se o recurso não existir ou pertencer a outro usuário, retorna invariavelmente
    HTTP 404 Not Found (blindagem anti-IDOR sem vazamento de existência de recursos alheios).
    """
    record = session.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{label} não encontrado.")

    record_user_id = getattr(record, "user_id", None)
    if record_user_id is None and allow_global:
        return record

    if record_user_id != user_id:
        raise HTTPException(status_code=404, detail=f"{label} não encontrado.")

    return record


def checkpoint_after_purge(session: Session) -> None:
    """Depois de uma exclusão permanente já confirmada, leva o WAL para o banco e o trunca (F0.10.02).

    Com secure_delete, as páginas do banco já saem zeradas; o WAL, porém, guarda as versões antigas até o checkpoint.
    Leitores abertos podem impedir o TRUNCATE: a exclusão não falha por isso, e o resultado vai para o log.
    """
    # A conexão do engine fica sempre em transação (autocommit=False); a leitura aberta da própria sessão impediria
    # o TRUNCATE. Como em _configure_connection, o PRAGMA roda com autocommit ligado e o estado é restaurado.
    try:
        session.commit()
        raw = session.connection().connection.dbapi_connection
        previous = raw.autocommit
        raw.autocommit = True
        try:
            busy, log_frames, checkpointed = raw.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        finally:
            raw.autocommit = previous
    except Exception as error:  # noqa: BLE001 — a exclusão já foi confirmada; o checkpoint é só higiene
        logger.warning("Checkpoint do WAL após exclusão permanente falhou: %s", type(error).__name__)
        return
    if busy:
        logger.info("Checkpoint do WAL após exclusão ficou parcial (log=%s, gravados=%s).", log_frames, checkpointed)


def commit_changes(session: Session) -> None:
    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise


def check_optimistic_version(
    current_version: int,
    expected_version: int | None,
    entity_id: int,
    entity_type: str,
    server_updated_at: datetime | None,
    server_data: dict[str, Any],
    label: str = "Registro",
) -> None:
    """Valida controle otimista de concorrência baseado em versão incremental (OCC).

    Raises:
        ConcurrencyConflictError: Se a expected_version for divergente da versão atual no banco.
    """
    if expected_version is None:
        return

    if expected_version != current_version:
        raise ConcurrencyConflictError(
            entity_id=entity_id,
            entity_type=entity_type,
            server_version=current_version,
            server_updated_at=server_updated_at,
            server_data=server_data,
            detail=(
                f"Conflito de concorrência: este {label.lower()} foi modificado em outro dispositivo. "
                "Seus dados foram preservados no formulário."
            ),
        )


def check_optimistic_lock(
    current_updated_at: datetime | None,
    expected_updated_at: datetime | None,
    label: str = "Registro",
    entity_id: int | None = None,
    entity_type: str | None = None,
    server_version: int | None = None,
    server_data: dict[str, Any] | None = None,
) -> None:
    """Valida bloqueio de concorrência otimista.

    Raises:
        ConcurrencyConflictError ou HTTPException(409): Se o registro no banco foi alterado após o expected_updated_at.
    """
    if expected_updated_at is None or current_updated_at is None:
        return

    curr = current_updated_at if current_updated_at.tzinfo is not None else current_updated_at.replace(tzinfo=UTC)
    exp = expected_updated_at if expected_updated_at.tzinfo is not None else expected_updated_at.replace(tzinfo=UTC)

    if curr > exp + timedelta(seconds=1):
        if entity_id is not None and entity_type is not None and server_version is not None:
            raise ConcurrencyConflictError(
                entity_id=entity_id,
                entity_type=entity_type,
                server_version=server_version,
                server_updated_at=current_updated_at,
                server_data=server_data or {},
                detail=(
                    f"Conflito de concorrência: este {label.lower()} foi modificado em outro dispositivo. "
                    "Seus dados foram preservados no formulário."
                ),
            )
        raise HTTPException(
            status_code=409,
            detail=(
                f"Conflito de concorrência: este {label.lower()} foi modificado em outro dispositivo. "
                "Seus dados foram preservados no formulário."
            ),
        )
