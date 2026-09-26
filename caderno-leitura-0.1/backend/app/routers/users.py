from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.dependencies import CurrentUser, DatabaseSession
from app.models.user import User
from app.schemas.profile import UserProfilePublicRead, UserSearchItem
from app.services.friendship_service import (
    get_blocked_user_ids_bilateral,
    get_friends_summary,
    get_relation_status,
    is_blocked_between,
)
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
    blocked_ids = get_blocked_user_ids_bilateral(session, current_user.id)
    return search_discoverable_users(q, session, limit=limit, exclude_user_ids=blocked_ids)


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

    # Blindagem bilateral: se houver bloqueio entre as partes, simula 404 (anti-enumeração)
    if current_user.id != profile.user_id and is_blocked_between(session, current_user.id, profile.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    friends_summary = get_friends_summary(session, profile.user_id)
    friends_count = friends_summary.friends_count

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
            friends_count=friends_count,
            reading_stats=stats,
            created_at=profile.created_at,
        )

    # Verifica se há amizade ativa
    rel = get_relation_status(session, current_user.id, profile.username)
    is_friend = (rel.relation_status == "friends")

    # Visitante externo: aplica regras de visibilidade
    if profile.profile_visibility == "private" or (profile.profile_visibility == "friends" and not is_friend):
        # Perfil restrito para este visitante
        return UserProfilePublicRead(
            username=profile.username,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            bio=None,
            profile_visibility=profile.profile_visibility,
            is_private=True,
            friends_count=friends_count,
            reading_stats=None,
            created_at=profile.created_at,
        )

    # Perfil público ou liberado por amizade
    stats = calculate_reading_stats(profile.user_id, session) if profile.show_reading_stats else None
    return UserProfilePublicRead(
        username=profile.username,
        display_name=profile.display_name,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        profile_visibility=profile.profile_visibility,
        is_private=False,
        friends_count=friends_count,
        reading_stats=stats,
        created_at=profile.created_at,
    )
