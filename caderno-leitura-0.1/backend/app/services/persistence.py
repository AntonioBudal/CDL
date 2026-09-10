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
