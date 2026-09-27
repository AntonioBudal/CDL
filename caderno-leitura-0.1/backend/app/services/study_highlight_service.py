"""Serviço para gestão de destaques e anotações contextuais de estudos."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import select

from app.models.study import Study
from app.models.study_highlight import StudyHighlight
from app.schemas.study_highlight import StudyHighlightCreate, StudyHighlightUpdate
from app.services.persistence import commit_changes, get_user_resource_or_404
from app.services.sharing_service import can_read_study

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _check_study_access(session: Session, study_id: int, user_id: str, *, for_mutation: bool = False) -> Study:
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado ou está na lixeira.")

    if study.user_id == user_id:
        return study

    if can_read_study(session, user_id, study):
        if for_mutation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso somente leitura. Apenas o proprietário pode alterar este estudo.",
            )
        return study

    raise HTTPException(status_code=404, detail="Estudo não encontrado.")


def list_study_highlights(
    session: Session,
    study_id: int,
    user_id: str,
    section: str | None = None,
) -> list[StudyHighlight]:
    _check_study_access(session, study_id, user_id, for_mutation=False)

    stmt = select(StudyHighlight).where(
        StudyHighlight.study_id == study_id,
        StudyHighlight.user_id == user_id,
    )
    if section:
        stmt = stmt.where(StudyHighlight.section == section)

    stmt = stmt.order_by(StudyHighlight.start_offset.asc(), StudyHighlight.id.asc())
    return list(session.scalars(stmt).all())


def create_study_highlight(
    session: Session,
    study_id: int,
    user_id: str,
    payload: StudyHighlightCreate,
) -> StudyHighlight:
    _check_study_access(session, study_id, user_id, for_mutation=True)

    if payload.end_offset < payload.start_offset:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O offset de término (end_offset) deve ser maior ou igual ao offset de início (start_offset).",
        )

    highlight = StudyHighlight(
        study_id=study_id,
        user_id=user_id,
        section=payload.section,
        start_offset=payload.start_offset,
        end_offset=payload.end_offset,
        selected_text=payload.selected_text,
        prefix=payload.prefix,
        suffix=payload.suffix,
        color=payload.color,
        kind=payload.kind,
        note=payload.note,
    )
    session.add(highlight)
    commit_changes(session)
    session.refresh(highlight)
    return highlight


def update_study_highlight(
    session: Session,
    study_id: int,
    highlight_id: int,
    user_id: str,
    payload: StudyHighlightUpdate,
) -> StudyHighlight:
    _check_study_access(session, study_id, user_id, for_mutation=True)
    highlight = get_user_resource_or_404(session, StudyHighlight, highlight_id, user_id, "Destaque")
    if highlight.study_id != study_id:
        raise HTTPException(status_code=404, detail="Destaque não pertence a este estudo.")

    if payload.color is not None:
        highlight.color = payload.color
    if payload.kind is not None:
        highlight.kind = payload.kind
    if payload.note is not None:
        highlight.note = payload.note

    commit_changes(session)
    session.refresh(highlight)
    return highlight


def delete_study_highlight(
    session: Session,
    study_id: int,
    highlight_id: int,
    user_id: str,
) -> None:
    _check_study_access(session, study_id, user_id, for_mutation=True)
    highlight = get_user_resource_or_404(session, StudyHighlight, highlight_id, user_id, "Destaque")
    if highlight.study_id != study_id:
        raise HTTPException(status_code=404, detail="Destaque não pertence a este estudo.")

    session.delete(highlight)
    commit_changes(session)
