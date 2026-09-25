from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.dependencies import CurrentUser, DatabaseSession
from app.models.user import User
from app.schemas.profile import UserProfilePublicRead, UserSearchItem
from app.services.profile_service import (
    calculate_reading_stats,
    get_or_create_profile,
    get_profile_by_username,
    search_discoverable_users,
)

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get(
    "",
    response_model=list[UserSearchItem],
    summary="Buscar leitores descobríveis no sistema",
)
def search_users(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: Annotated[str | None, Query(description="Termo de busca por nome ou handle")] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> list[UserSearchItem]:
    return search_discoverable_users(q, session, limit=limit)


@router.get(
    "/{username}",
    response_model=UserProfilePublicRead,
    summary="Consultar perfil público de um leitor",
)
def get_user_public_profile(
    username: str,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> UserProfilePublicRead:
    profile = get_profile_by_username(username, session)
    if profile is None:
        # Fallback para usuário sem perfil provisionado
        user = session.scalar(
            select(User).where(func.lower(User.username) == username.strip().lower())
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        profile = get_or_create_profile(user, session)
        session.commit()

    is_owner = (profile.user_id == current_user.id)

    if is_owner:
        stats = calculate_reading_stats(profile.user_id, session) if profile.show_reading_stats else None
        return UserProfilePublicRead(
            username=profile.username,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            profile_visibility=profile.profile_visibility,
            is_private=False,
            reading_stats=stats,
            created_at=profile.created_at,
        )

    # Visitante externo: aplica regras de visibilidade
    if profile.profile_visibility in ("private", "friends"):
        # Sem vínculo de amizade ativo, renderiza cartão discreto restrito
        return UserProfilePublicRead(
            username=profile.username,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            bio=None,
            profile_visibility=profile.profile_visibility,
            is_private=True,
            reading_stats=None,
            created_at=profile.created_at,
        )

    # Perfil público
    stats = calculate_reading_stats(profile.user_id, session) if profile.show_reading_stats else None
    return UserProfilePublicRead(
        username=profile.username,
        display_name=profile.display_name,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        profile_visibility=profile.profile_visibility,
        is_private=False,
        reading_stats=stats,
        created_at=profile.created_at,
    )
