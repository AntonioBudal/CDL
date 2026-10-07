"""Roteador para consulta de backlinks e busca de candidatos a menções entre estudos."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.study_mention import (
    BacklinksResponse,
    StudyCandidateOption,
)
from app.services.study_mention_service import (
    get_study_backlinks,
    search_study_candidates,
)

router = APIRouter(tags=["Menções e Backlinks entre Estudos"])


@router.get(
    "/studies/search-candidates",
    response_model=list[StudyCandidateOption],
    summary="Buscar estudos candidatos para menção no editor ou relações",
)
def search_candidates(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str | None = Query(default=None, description="Termo de busca textual para filtrar títulos de estudos"),
    query: str | None = Query(default=None, description="Termo de busca textual alternativo"),
    exclude_study_id: int | None = Query(default=None, gt=0, description="ID do estudo a ser excluído"),
    limit: int = Query(default=10, ge=1, le=50, description="Quantidade máxima de sugestões"),
):
    search_term = q if q is not None else (query or "")
    return search_study_candidates(
        session=session,
        user_id=current_user.id,
        query=search_term,
        exclude_study_id=exclude_study_id,
        limit=limit,
    )


@router.get(
    "/studies/{study_id}/backlinks",
    response_model=BacklinksResponse,
    summary="Listar estudos que mencionam o estudo indicado (backlinks reversos)",
)
def get_backlinks(
    study_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return get_study_backlinks(
        session=session,
        study_id=study_id,
        user_id=current_user.id,
    )
