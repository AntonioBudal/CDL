from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.search import SearchHistoryResponse, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse, summary="Busca transversal de estudos e anotações")
def search_studies(
    q: Annotated[str, Query(min_length=2, description="Termo de busca com no mínimo 2 caracteres")],
    mode: Annotated[Literal["and", "or"], Query(description="Modo de combinação de termos")] = "and",
    book_id: Annotated[int | None, Query(description="Filtrar por livro específico")] = None,
    category_id: Annotated[str | None, Query(description="Filtrar por categoria temática")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Quantidade máxima de resultados")] = 20,
    session: Session = Depends(get_session),
) -> SearchResponse:
    return SearchService.search_studies(
        session=session,
        query=q,
        mode=mode,
        book_id=book_id,
        category_id=category_id,
        limit=limit,
    )


@router.get("/history", response_model=SearchHistoryResponse, summary="Listar buscas recentes")
def get_search_history(
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
    session: Session = Depends(get_session),
) -> SearchHistoryResponse:
    return SearchService.get_recent_searches(session=session, limit=limit)


@router.delete("/history/{history_id}", summary="Remover termo do histórico")
def delete_search_history_item(
    history_id: int,
    session: Session = Depends(get_session),
):
    deleted = SearchService.delete_search_query(session, history_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item do histórico não encontrado.",
        )
    return {"success": True, "message": "Item removido do histórico com sucesso."}


@router.delete("/history", summary="Limpar todo o histórico de buscas")
def clear_search_history(
    session: Session = Depends(get_session),
):
    count = SearchService.clear_all_searches(session)
    return {"success": True, "message": f"Histórico limpo com sucesso ({count} registros removidos)."}
