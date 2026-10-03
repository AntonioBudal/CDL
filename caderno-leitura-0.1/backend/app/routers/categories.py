from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import func, select

from app.dependencies import CurrentUser, DatabaseSession
from app.models.category import Category, book_categories
from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryStats,
    CategorySuggestion,
)
from app.services.category_service import (
    get_categories_with_books_count,
    get_category_suggestions,
    get_or_create_canonical_category,
    get_taxonomy_stats,
)
from app.services.persistence import commit_changes

router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.get("", response_model=list[CategoryRead], summary="Listar categorias da taxonomia")
def list_categories(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str | None = None,
    canonical_only: bool = Query(default=False, description="Filtra apenas categorias canônicas"),
):
    """Retorna categorias com contagem de livros associados, ordenadas alfabeticamente."""
    return get_categories_with_books_count(
        session=session,
        user_id=current_user.id,
        q=q,
        canonical_only=canonical_only,
    )


@router.get("/suggest", response_model=CategorySuggestion, summary="Sugerir termos canônicos para autocompletar")
def suggest_categories(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str = Query(..., min_length=1, description="Termo digitado pelo usuário"),
):
    """Gera sugestões automáticas e determinísticas de categorias canônicas."""
    return get_category_suggestions(
        session=session,
        query_text=q,
        user_id=current_user.id,
    )


@router.get("/stats", response_model=CategoryStats, summary="Estatísticas e conformidade taxonômica")
def get_categories_stats(
    session: DatabaseSession,
    current_user: CurrentUser,
):
    """Retorna métricas agregadas do catálogo de categorias e vínculos de obras."""
    return get_taxonomy_stats(session=session)


@router.post("", response_model=CategoryRead, summary="Criar ou validar categoria canônica")
def create_category(
    payload: CategoryCreate,
    response: Response,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    """Cria nova categoria com normalização singular ou retorna categoria equivalente existente."""
    cat, created = get_or_create_canonical_category(
        session=session,
        name=payload.name,
        user_id=current_user.id,
        category_id=payload.id,
        parent_id=payload.parent_id,
    )

    if created:
        commit_changes(session)
        session.refresh(cat)
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK

    # Contagem de livros associados
    b_count = (
        session.scalar(
            select(func.count(book_categories.c.book_id)).where(
                book_categories.c.category_id == cat.id
            )
        )
        or 0
    )

    return CategoryRead(
        id=cat.id,
        name=cat.name,
        parent_id=cat.parent_id,
        path=cat.path,
        user_id=cat.user_id,
        is_canonical=cat.is_canonical,
        books_count=int(b_count),
        created_at=cat.created_at,
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir categoria personalizada")
def delete_category(
    category_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    if category.user_id is None or category.is_canonical:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Categorias padrão do sistema não podem ser excluídas.",
        )
    if category.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")

    # Verificar livros vinculados
    has_books = session.scalar(
        select(func.count(book_categories.c.book_id)).where(
            book_categories.c.category_id == category_id
        )
    )
    if has_books:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A categoria possui livros associados e não pode ser excluída sem desassociação prévia.",
        )

    session.delete(category)
    commit_changes(session)
