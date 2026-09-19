from fastapi import APIRouter
from sqlalchemy import or_, select

from app.dependencies import DatabaseSession
from app.models.category import Category
from app.schemas.category import CategoryRead

router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.get("", response_model=list[CategoryRead], summary="Listar categorias da taxonomia")
def list_categories(
    session: DatabaseSession,
    q: str | None = None,
):
    query = select(Category)
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
