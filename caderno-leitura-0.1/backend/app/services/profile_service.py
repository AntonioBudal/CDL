from __future__ import annotations

import logging
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.book import Book
from app.models.study import Study
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.profile import ProfileReadingStats, UserProfileUpdate, UserSearchItem

logger = logging.getLogger(__name__)


def get_or_create_profile(user: User, session: Session) -> UserProfile:
    """Garante que o leitor possua um registro UserProfile correspondente, criando se necessário."""
    profile = session.scalar(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    if profile is None:
        profile = UserProfile(
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=None,
            bio=None,
            profile_visibility="public",
            dashboard_visibility="private",
            is_discoverable=True,
            show_reading_stats=True,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        session.add(profile)
        session.flush()
        session.refresh(profile)
        logger.info("Perfil criado automaticamente para o usuário %s (%s)", user.username, user.id)
    return profile


def get_profile_by_username(username: str, session: Session) -> UserProfile | None:
    """Busca o perfil público pelo handle @username com comparação case-insensitive."""
    clean_username = username.strip().lower()
    return session.scalar(
        select(UserProfile).where(func.lower(UserProfile.username) == clean_username)
    )


def calculate_reading_stats(user_id: str, session: Session) -> ProfileReadingStats:
    """Calcula estatísticas quantitativas resumidas do leitor."""
    total_books = session.scalar(
        select(func.count(Book.id)).where(Book.user_id == user_id, Book.deleted_at.is_(None))
    ) or 0
    total_studies = session.scalar(
        select(func.count(Study.id)).where(Study.user_id == user_id, Study.deleted_at.is_(None))
    ) or 0
    return ProfileReadingStats(
        total_books=total_books,
        total_studies=total_studies,
        current_streak_days=0,
    )


def update_user_profile(user: User, update_data: UserProfileUpdate, session: Session) -> UserProfile:
    """Atualiza dados do perfil e sincroniza atomicamente username e display_name com User."""
    profile = get_or_create_profile(user, session)

    if update_data.username is not None:
        new_username = update_data.username.strip()
        # Se alterou o username, valida unicidade case-insensitive em users
        if new_username.lower() != user.username.lower():
            collision = session.scalar(
                select(User).where(
                    func.lower(User.username) == new_username.lower(),
                    User.id != user.id,
                )
            )
            if collision is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Nome de usuário indisponível.",
                )
        profile.username = new_username
        user.username = new_username

    if update_data.display_name is not None:
        clean_name = update_data.display_name.strip()
        profile.display_name = clean_name
        user.display_name = clean_name

    if update_data.bio is not None:
        profile.bio = update_data.bio.strip() if update_data.bio else None

    if update_data.profile_visibility is not None:
        profile.profile_visibility = update_data.profile_visibility.value

    if update_data.dashboard_visibility is not None:
        profile.dashboard_visibility = update_data.dashboard_visibility.value

    if update_data.is_discoverable is not None:
        profile.is_discoverable = update_data.is_discoverable

    if update_data.show_reading_stats is not None:
        profile.show_reading_stats = update_data.show_reading_stats

    profile.updated_at = utc_now()
    user.updated_at = utc_now()
    session.flush()
    session.refresh(profile)
    return profile


def search_discoverable_users(
    query: str | None,
    session: Session,
    limit: int = 20,
) -> list[UserSearchItem]:
    """Busca usuários ativos que sejam descobríveis e com perfil não privado."""
    stmt = (
        select(UserProfile)
        .join(User, User.id == UserProfile.user_id)
        .where(
            User.status == "ativo",
            UserProfile.is_discoverable == True,  # noqa: E712
            UserProfile.profile_visibility != "private",
        )
    )
    if query and query.strip():
        term = f"%{query.strip().lower()}%"
        stmt = stmt.where(
            func.lower(UserProfile.username).like(term)
            | func.lower(UserProfile.display_name).like(term)
        )

    stmt = stmt.order_by(UserProfile.display_name.asc()).limit(limit)
    profiles = session.scalars(stmt).all()
    return [
        UserSearchItem(
            username=p.username,
            display_name=p.display_name,
            avatar_url=p.avatar_url,
            bio=p.bio,
        )
        for p in profiles
    ]
