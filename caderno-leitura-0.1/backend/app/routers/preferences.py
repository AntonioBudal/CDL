from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.preferences import UserPreferenceRead, UserPreferenceUpdate
from app.services.preferences_service import (
    get_or_create_user_preferences,
    update_user_preferences,
)

router = APIRouter(prefix="/preferences", tags=["Preferências"])


@router.get(
    "",
    response_model=UserPreferenceRead,
    summary="Obter preferências de leitura do usuário",
)
def get_preferences_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
) -> UserPreferenceRead:
    pref = get_or_create_user_preferences(session, current_user.id)
    return UserPreferenceRead.model_validate(pref)


@router.put(
    "",
    response_model=UserPreferenceRead,
    summary="Atualizar preferências de leitura do usuário",
)
def update_preferences_endpoint(
    payload: UserPreferenceUpdate,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> UserPreferenceRead:
    pref = update_user_preferences(session, current_user.id, payload)
    return UserPreferenceRead.model_validate(pref)
