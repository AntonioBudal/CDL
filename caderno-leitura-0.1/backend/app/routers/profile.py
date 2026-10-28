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
    from app.services import media_service
    from app.services.avatar_service import validate_and_crop_avatar

    data = file.file.read()
    cropped_bytes = media_service.strip_webp(validate_and_crop_avatar(data))
    profile = get_or_create_profile(current_user, session)
    old_url = profile.avatar_url
    # Feature 090-B: o avatar vai cifrado para o cofre; a URL continua na mesma rota de sempre.
    row = media_service.store(session, user_id=current_user.id, kind="avatar", webp=cropped_bytes)
    new_url = f"/api/avatars/{row.id}"
    profile.avatar_url = new_url
    _discard_old_avatar(session, current_user.id, old_url)
    session.commit()
    return AvatarResponse(avatar_url=new_url)


def _discard_old_avatar(session: Session, user_id: str, old_url: str | None) -> None:
    """Apaga o avatar anterior: do cofre (duas fases) ou o arquivo legado em claro."""
    from app.services import media_service
    from app.services.avatar_service import delete_avatar_file

    if not old_url or not old_url.startswith("/api/avatars/"):
        return
    old = media_service.by_reference(session, old_url)
    if old is not None:
        if old.kind == "avatar" and old.user_id == user_id:
            media_service.delete(session, old)
        return
    delete_avatar_file(old_url)


@router.delete(
    "/avatar",
    response_model=AvatarResponse,
    summary="Remover avatar customizado",
)
def remove_avatar(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> AvatarResponse:
    profile = get_or_create_profile(current_user, session)
    old_url = profile.avatar_url
    profile.avatar_url = None
    _discard_old_avatar(session, current_user.id, old_url)
    session.commit()
    return AvatarResponse(avatar_url=None)


avatars_router = APIRouter(prefix="/avatars", tags=["Avatares"])


@avatars_router.get("/{filename}", summary="Servir o avatar (cofre cifrado ou arquivo legado)")
def serve_avatar(filename: str, current_user: CurrentUser, session: DatabaseSession):
    """Exige sessão (feature 090-B). Avatar visível a quem está logado e não tem bloqueio com o dono."""
    import re

    from app.core.config import get_avatars_dir
    from app.models.user_profile import UserProfile
    from app.routers.media import IMAGE_HEADERS, media_response
    from app.services import media_service
    from app.services.friendship_service import is_blocked_between

    not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar não encontrado.")
    row = media_service.by_reference(session, filename)
    if row is not None:
        if row.kind != "avatar" or not media_service.can_view(session, current_user.id, row):
            raise not_found
        return media_response(session, row)
    if not re.fullmatch(r"[A-Za-z0-9_\-]+\.webp", filename):
        raise not_found
    profile = session.query(UserProfile).filter(UserProfile.avatar_url == f"/api/avatars/{filename}").first()
    if profile is None or (
        profile.user_id != current_user.id and is_blocked_between(session, current_user.id, profile.user_id)
    ):
        raise not_found
    filepath = get_avatars_dir() / filename
    if not filepath.is_file():
        raise not_found
    return Response(content=filepath.read_bytes(), media_type="image/webp", headers=IMAGE_HEADERS)

