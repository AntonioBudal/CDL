import re

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.dependencies import CurrentUser, DatabaseSession
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead
from app.services.persistence import commit_changes

router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.get("", response_model=list[CategoryRead], summary="Listar categorias da taxonomia")
def list_categories(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str | None = None,
):
    """Retorna categorias visíveis: categorias padrão do sistema (user_id IS NULL)

    ou categorias personalizadas do usuário autenticado.
    """
    query = select(Category).where(
        or_(
            Category.user_id.is_(None),
            Category.user_id == current_user.id,
        )
    )
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Category.name.ilike(term),
                Category.path.ilike(term),
                Category.id.ilike(term),
            )
        )
    query = query.order_by(Category.path)
    return session.scalars(query).all()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, summary="Criar categoria personalizada")
def create_category(
    payload: CategoryCreate,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    """Cria uma nova categoria associada ao acervo pessoal do usuário ativo."""
    raw_id = payload.id.strip() if payload.id else re.sub(r"[^a-zA-Z0-9_\-]", "-", payload.name.lower()).strip("-")
    if not raw_id:
        raise HTTPException(status_code=400, detail="Identificador de categoria inválido.")

    if session.get(Category, raw_id) is not None:
        raise HTTPException(status_code=409, detail="Já existe uma categoria com este identificador.")

    path = payload.name
    if payload.parent_id:
        parent = session.get(Category, payload.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Categoria pai informada não existe.")
        # Se categoria pai é privada, deve pertencer ao usuário
        if parent.user_id is not None and parent.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Categoria pai informada não encontrada.")
        path = f"{parent.path} / {payload.name}"

    cat = Category(
        id=raw_id,
        name=payload.name,
        parent_id=payload.parent_id,
        path=path,
        user_id=current_user.id,
    )
    session.add(cat)
    commit_changes(session)
    session.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir categoria personalizada")
def delete_category(
    category_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    if category.user_id is None:
        raise HTTPException(status_code=403, detail="Categorias padrão do sistema não podem ser excluídas.")
    if category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")

    session.delete(category)
    commit_changes(session)
