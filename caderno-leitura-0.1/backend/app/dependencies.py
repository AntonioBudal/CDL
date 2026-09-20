from typing import Annotated

from fastapi import Depends, Header, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.core.auth import get_or_create_default_owner, get_user_by_id, is_valid_uuid
from app.db.session import get_session
from app.models.user import User
from app.schemas.common import SQLITE_MAX_INTEGER

DatabaseSession = Annotated[Session, Depends(get_session)]
Identifier = Annotated[int, Path(gt=0, le=SQLITE_MAX_INTEGER)]


def get_current_user(
    session: DatabaseSession,
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> User:
    """Resolve o usuário autenticado na requisição.

    - Se X-User-Id não for enviado, assume o proprietário canônico padrão
      garantindo retrocompatibilidade total com a interface atual e scripts locais.
    - Se X-User-Id for enviado, valida formato e existência no banco de dados.
    - Em caso de identificador inexistente ou inativo, retorna HTTP 401.
    """
    if not x_user_id:
        return get_or_create_default_owner(session)

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

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
