from __future__ import annotations

import logging
from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.types import utc_now
from app.models.book import Book
from app.models.study import Study
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.admin import AdminStatsSummary, AdminUserItem
from app.services.persistence import commit_changes
from app.services.session_service import revoke_user_all_sessions

logger = logging.getLogger(__name__)


def get_admin_stats(session: Session) -> AdminStatsSummary:
    """Calcula estatísticas agregadas globais da plataforma para a área administrativa."""
    total_users = session.scalar(select(func.count(User.id))) or 0
    active_users = session.scalar(select(func.count(User.id)).where(User.status == "ativo")) or 0
    suspended_users = session.scalar(select(func.count(User.id)).where(User.status == "suspenso")) or 0
    admin_users = (
        session.scalar(select(func.count(User.id)).where(User.role == "admin", User.status == "ativo")) or 0
    )
    total_studies = (
        session.scalar(select(func.count(Study.id)).where(Study.deleted_at.is_(None))) or 0
    )

    return AdminStatsSummary(
        total_users=total_users,
        active_users=active_users,
        suspended_users=suspended_users,
        admin_users=admin_users,
        total_studies=total_studies,
    )


def list_users(
    session: Session,
    q: str | None = None,
    status_filter: str = "all",
    role_filter: str = "all",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AdminUserItem], int]:
    """Retorna listagem paginada de contas com métricas agregadas e filtros."""
    limit = max(1, min(100, limit))
    offset = max(0, offset)

    stmt = select(User)

    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                User.username.ilike(term),
                User.display_name.ilike(term),
                User.email.ilike(term),
            )
        )

    if status_filter in ("ativo", "suspenso"):
        stmt = stmt.where(User.status == status_filter)

    if role_filter in ("user", "admin"):
        stmt = stmt.where(User.role == role_filter)

    # Contagem total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.scalar(count_stmt) or 0

    # Paginação e ordenação
    stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)
    users = session.scalars(stmt).all()

    now = utc_now()
    items: list[AdminUserItem] = []

    for u in users:
        # Contagem de estudos ativos
        studies_count = (
            session.scalar(
                select(func.count(Study.id)).where(Study.user_id == u.id, Study.deleted_at.is_(None))
            )
            or 0
        )

        # Contagem de livros
        books_count = session.scalar(select(func.count(Book.id)).where(Book.user_id == u.id)) or 0

        # Sessões ativas
        active_sessions_count = (
            session.scalar(
                select(func.count(UserSession.id)).where(
                    UserSession.user_id == u.id, UserSession.expires_at > now
                )
            )
            or 0
        )

        # Último acesso registrado nas sessões
        last_access = session.scalar(
            select(func.max(UserSession.last_activity)).where(UserSession.user_id == u.id)
        ) or u.updated_at

        # Provedor
        has_pwd = u.has_password
        has_goog = u.has_google
        if has_pwd and has_goog:
            provider = "ambos"
        elif has_goog:
            provider = "google"
        else:
            provider = "local"

        items.append(
            AdminUserItem(
                id=u.id,
                username=u.username,
                display_name=u.display_name,
                email=u.email,
                role=u.role if u.role in ("admin", "user") else "user",
                status=u.status if u.status in ("ativo", "suspenso") else "ativo",
                provider=provider,
                created_at=u.created_at,
                last_access=last_access,
                studies_count=studies_count,
                books_count=books_count,
                active_sessions_count=active_sessions_count,
            )
        )

    return items, total


def suspend_user(
    session: Session,
    target_user_id: str,
    current_user: User,
    reason: str | None = None,
) -> tuple[User, int]:
    """Suspende a conta indicada e revoga imediatamente todas as suas sessões ativas."""
    if target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode suspender sua própria conta de administrador.",
        )

    target_user = session.get(User, target_user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    if target_user.role == "admin":
        other_admins = session.scalar(
            select(func.count(User.id)).where(
                User.role == "admin",
                User.status == "ativo",
                User.id != target_user.id,
            )
        ) or 0
        if other_admins < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível suspender o único administrador ativo do sistema.",
            )

    target_user.status = "suspenso"
    sessions_revoked = revoke_user_all_sessions(session, target_user.id)
    commit_changes(session)
    logger.info(
        "Usuário %s suspenso pelo admin %s (sessões revogadas: %d). Motivo: %s",
        target_user.username,
        current_user.username,
        sessions_revoked,
        reason,
    )
    return target_user, sessions_revoked


def reactivate_user(
    session: Session,
    target_user_id: str,
    current_user: User,
) -> User:
    """Restaura o status da conta para 'ativo'."""
    target_user = session.get(User, target_user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    target_user.status = "ativo"
    commit_changes(session)
    logger.info("Usuário %s reativado pelo admin %s", target_user.username, current_user.username)
    return target_user


def update_user_role(
    session: Session,
    target_user_id: str,
    new_role: str,
    current_user: User,
) -> User:
    """Altera o papel de um usuário entre 'user' e 'admin' com salvaguarda anti-lockout."""
    if new_role not in ("admin", "user"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Papel inválido. Valores aceitos: 'user', 'admin'.",
        )

    target_user = session.get(User, target_user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    # Se estiver rebaixando de admin para user
    if target_user.role == "admin" and new_role == "user":
        other_active_admins = session.scalar(
            select(func.count(User.id)).where(
                User.role == "admin",
                User.status == "ativo",
                User.id != target_user.id,
            )
        ) or 0
        if other_active_admins < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível rebaixar o único administrador ativo do sistema.",
            )

    target_user.role = new_role
    commit_changes(session)
    logger.info(
        "Papel do usuário %s alterado para %s pelo admin %s",
        target_user.username,
        new_role,
        current_user.username,
    )
    return target_user


def revoke_all_sessions_for_user(
    session: Session,
    target_user_id: str,
    current_user: User,
) -> int:
    """Revoga forçadamente todas as sessões de um usuário sem alterar o status da conta."""
    target_user = session.get(User, target_user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    sessions_revoked = revoke_user_all_sessions(session, target_user.id)
    commit_changes(session)
    logger.info(
        "Sessões do usuário %s (%d sessões) revogadas pelo admin %s",
        target_user.username,
        sessions_revoked,
        current_user.username,
    )
    return sessions_revoked
