from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.sharing import SharedBooksResponse, SharedStudiesResponse
from app.services.sharing_service import (
    get_shared_books_for_user,
    get_shared_studies_for_user,
)

router = APIRouter(prefix="/shared", tags=["Compartilhamento"])


@router.get("/studies", response_model=SharedStudiesResponse, summary="Listar estudos compartilhados com o usuário")
def list_shared_studies(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str | None = Query(default=None, description="Termo de busca por título ou autor"),
    author: str | None = Query(default=None, description="Filtrar por @username do autor"),
    limit: int = Query(default=50, ge=1, le=100, description="Limite máximo de itens"),
    offset: int = Query(default=0, ge=0, description="Deslocamento para paginação"),
):
    items, total = get_shared_studies_for_user(
        session=session,
        user_id=current_user.id,
        query=q,
        author=author,
        limit=limit,
        offset=offset,
    )
    return SharedStudiesResponse(items=items, total=total)


@router.get("/books", response_model=SharedBooksResponse, summary="Listar livros compartilhados com o usuário")
def list_shared_books(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str | None = Query(default=None, description="Termo de busca por título"),
    limit: int = Query(default=50, ge=1, le=100, description="Limite máximo de itens"),
    offset: int = Query(default=0, ge=0, description="Deslocamento para paginação"),
):
    items, total = get_shared_books_for_user(
        session=session,
        user_id=current_user.id,
        query=q,
        limit=limit,
        offset=offset,
    )
    return SharedBooksResponse(items=items, total=total)
