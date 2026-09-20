from datetime import UTC, datetime, timedelta
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.base import Base

Record = TypeVar("Record", bound=Base)


def get_or_404(session: Session, model: type[Record], record_id: int, label: str) -> Record:
    record = session.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{label} não encontrado.")
    return record


def commit_changes(session: Session) -> None:
    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise


def check_optimistic_lock(
    current_updated_at: datetime | None,
    expected_updated_at: datetime | None,
    label: str = "Registro",
) -> None:
    """Valida bloqueio de concorrência otimista.

    Raises:
        HTTPException(409): Se o registro no banco foi alterado após o expected_updated_at.
    """
    if expected_updated_at is None or current_updated_at is None:
        return

    curr = current_updated_at if current_updated_at.tzinfo is not None else current_updated_at.replace(tzinfo=UTC)
    exp = expected_updated_at if expected_updated_at.tzinfo is not None else expected_updated_at.replace(tzinfo=UTC)

    if curr > exp + timedelta(seconds=1):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Conflito de concorrência: este {label.lower()} foi modificado em outro dispositivo. "
                "Seus dados foram preservados no formulário."
            ),
        )
