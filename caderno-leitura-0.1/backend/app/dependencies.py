from typing import Annotated

from fastapi import Depends, Header, HTTPException, Path, Request, status
from sqlalchemy.orm import Session

from app.core.auth import get_or_create_default_owner, get_user_by_id, is_valid_uuid
from app.core.config import SESSION_COOKIE_NAME, is_auth_required
from app.db.session import get_session
from app.models.user import User
from app.schemas.common import SQLITE_MAX_INTEGER
from app.services.session_service import get_session_by_token

DatabaseSession = Annotated[Session, Depends(get_session)]
Identifier = Annotated[int, Path(gt=0, le=SQLITE_MAX_INTEGER)]


def get_current_user(
    request: Request,
    session: DatabaseSession,
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> User:
    """Resolve o usuário autenticado na requisição.

    1. Prioridade 1 (Web): Cookie HTTP `caderno_session` com validação de sessão e janela deslizante.
    2. Prioridade 2 (Testes/CLI): Cabeçalho `X-User-Id` com validação de formato UUID e status ativo.
    3. Requisição anônima:
       - Se `is_auth_required()` for True: Rejeita com HTTP 401 Unauthorized.
       - Se `is_auth_required()` for False: Retorna o proprietário canônico para compatibilidade legada.
    """
    # 1. Validação por Cookie de Sessão
    raw_token = request.cookies.get(SESSION_COOKIE_NAME)
    if raw_token:
        user_session = get_session_by_token(session, raw_token)
        if user_session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sessão inválida ou expirada.",
            )
        user = get_user_by_id(session, user_session.user_id)
        if user is None or user.status != "ativo":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado ou inativo.",
            )
        request.state.current_session_id = user_session.id
        return user

    # 2. Validação por Cabeçalho de Teste/Automação X-User-Id
    if x_user_id:
        user_id_clean = x_user_id.strip()
        if not is_valid_uuid(user_id_clean):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado ou inexistente.",
            )

        user = get_user_by_id(session, user_id_clean)
        if user is None or user.status != "ativo":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado ou inexistente.",
            )

        request.state.current_session_id = None
        return user

    # 3. Requisição Anônima
    if is_auth_required():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado. Faça login para acessar este recurso.",
        )

    # Fallback controlado para suites de testes legadas
    request.state.current_session_id = None
    return get_or_create_default_owner(session)


CurrentUser = Annotated[User, Depends(get_current_user)]
