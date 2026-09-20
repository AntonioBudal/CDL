from fastapi import APIRouter

from app.dependencies import CurrentUser
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.get("/me", response_model=UserRead, summary="Obter dados do usuário autenticado")
def get_me(current_user: CurrentUser) -> UserRead:
    """Retorna os dados do usuário autenticado no contexto da requisição atual."""
    return current_user
