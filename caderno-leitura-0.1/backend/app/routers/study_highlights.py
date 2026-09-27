from __future__ import annotations

from fastapi import APIRouter, Query, Response, status

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.study_highlight import (
    StudyHighlightCreate,
    StudyHighlightRead,
    StudyHighlightUpdate,
)
from app.services.study_highlight_service import (
    create_study_highlight,
    delete_study_highlight,
    list_study_highlights,
    update_study_highlight,
)

router = APIRouter(tags=["Destaques de Estudos"])


@router.get(
    "/studies/{study_id}/highlights",
    response_model=list[StudyHighlightRead],
    summary="Listar destaques e notas de um estudo",
)
def get_highlights(
    study_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
    section: str | None = Query(default=None, description="Filtrar por seção do estudo"),
):
    return list_study_highlights(
        session=session,
        study_id=study_id,
        user_id=current_user.id,
        section=section,
    )


@router.post(
    "/studies/{study_id}/highlights",
    response_model=StudyHighlightRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo destaque ou anotação no estudo",
)
def create_highlight(
    study_id: Identifier,
    payload: StudyHighlightCreate,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return create_study_highlight(
        session=session,
        study_id=study_id,
        user_id=current_user.id,
        payload=payload,
    )


@router.patch(
    "/studies/{study_id}/highlights/{highlight_id}",
    response_model=StudyHighlightRead,
    summary="Atualizar cor, tipo ou anotação de um destaque",
)
def update_highlight(
    study_id: Identifier,
    highlight_id: Identifier,
    payload: StudyHighlightUpdate,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return update_study_highlight(
        session=session,
        study_id=study_id,
        highlight_id=highlight_id,
        user_id=current_user.id,
        payload=payload,
    )


@router.delete(
    "/studies/{study_id}/highlights/{highlight_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir destaque ou anotação do estudo",
)
def delete_highlight(
    study_id: Identifier,
    highlight_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    delete_study_highlight(
        session=session,
        study_id=study_id,
        highlight_id=highlight_id,
        user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
