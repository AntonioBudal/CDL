from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.profile import (
    AvatarResponse,
    UserProfilePrivateRead,
    UserProfileUpdate,
)
from app.services.profile_service import (
    calculate_reading_stats,
    get_or_create_profile,
    update_user_profile,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["Perfil"])


def _build_private_profile_response(user, profile, session: Session) -> UserProfilePrivateRead:
    from app.models.external_identity import ExternalIdentity
    from sqlalchemy import select

    stats = calculate_reading_stats(user.id, session)
    has_google = False
    google_url = None
    try:
        ident = session.scalar(
            select(ExternalIdentity).where(
                ExternalIdentity.user_id == user.id,
                ExternalIdentity.provider == "google",
            )
        )
        if ident is not None:
            has_google = True
    except Exception:
        pass

    return UserProfilePrivateRead(
        user_id=profile.user_id,
        username=profile.username,
        display_name=profile.display_name,
        email=user.email,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        profile_visibility=profile.profile_visibility,
        dashboard_visibility=profile.dashboard_visibility,
        is_discoverable=profile.is_discoverable,
        show_reading_stats=profile.show_reading_stats,
        has_google_avatar=has_google,
        google_avatar_url=google_url,
        reading_stats=stats,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get(
    "/me",
    response_model=UserProfilePrivateRead,
    summary="Obter perfil completo e privado do usuário atual autenticado",
)
def get_my_profile(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> UserProfilePrivateRead:
    profile = get_or_create_profile(current_user, session)
    session.commit()
    return _build_private_profile_response(current_user, profile, session)


@router.put(
    "/me",
    response_model=UserProfilePrivateRead,
    summary="Atualizar dados de perfil e configurações de privacidade",
)
def update_my_profile(
    req: UserProfileUpdate,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> UserProfilePrivateRead:
    profile = update_user_profile(current_user, req, session)
    session.commit()
    return _build_private_profile_response(current_user, profile, session)


@router.post(
    "/avatar",
    response_model=AvatarResponse,
    summary="Upload e corte seguro de imagem para o avatar",
)
def upload_avatar(
    current_user: CurrentUser,
    session: DatabaseSession,
    file: UploadFile = File(...),
) -> AvatarResponse:
    from app.services.avatar_service import (
        delete_avatar_file,
        save_avatar_file,
        validate_and_crop_avatar,
    )
    data = file.file.read()
    cropped_bytes = validate_and_crop_avatar(data)
    profile = get_or_create_profile(current_user, session)
    delete_avatar_file(profile.avatar_url)
    new_url = save_avatar_file(current_user.id, cropped_bytes)
    profile.avatar_url = new_url
    session.commit()
    return AvatarResponse(avatar_url=new_url)


@router.delete(
    "/avatar",
    response_model=AvatarResponse,
    summary="Remover avatar customizado",
)
def remove_avatar(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> AvatarResponse:
    from app.services.avatar_service import delete_avatar_file

    profile = get_or_create_profile(current_user, session)
    delete_avatar_file(profile.avatar_url)
    profile.avatar_url = None
    session.commit()
    return AvatarResponse(avatar_url=None)


avatars_router = APIRouter(prefix="/avatars", tags=["Avatares"])


@avatars_router.get("/{filename}", summary="Servir arquivo de imagem de avatar processado")
def serve_avatar(filename: str):
    from app.core.config import get_avatars_dir

    avatars_dir = get_avatars_dir()
    filepath = avatars_dir / filename
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar não encontrado.")
    return Response(content=filepath.read_bytes(), media_type="image/webp")

