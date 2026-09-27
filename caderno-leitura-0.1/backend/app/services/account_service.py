from __future__ import annotations

import logging
from fastapi import HTTPException, status
from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.orm import Session

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.core.security import verify_password
from app.db.types import utc_now
from app.models.audit_log import AuditLog
from app.models.book import Book
from app.models.canvas_frame import CanvasFrame
from app.models.category import Category, book_categories
from app.models.chapter import Chapter
from app.models.external_identity import ExternalIdentity
from app.models.friendship import Friendship
from app.models.local_credential import LocalCredential
from app.models.notification import Notification
from app.models.resource_permission import ResourcePermission
from app.models.search_history import SearchHistory
from app.models.study import Study
from app.models.study_canvas_node import StudyCanvasNode
from app.models.study_relation import StudyRelation
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.user_profile import UserProfile
from app.models.user_session import UserSession
from app.services.audit_service import log_event
from app.services.google_auth_service import verify_google_id_token

logger = logging.getLogger(__name__)


def deactivate_account(session: Session, user: User, password: str | None = None) -> None:
    """
    Desativa temporariamente a conta do leitor.
    Exige confirmação de senha se o leitor tiver credencial local ativa.
    Revoga imediatamente todas as sessões ativas do usuário.
    """
    if user.id == DEFAULT_OWNER_ID or user.username == DEFAULT_OWNER_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A conta do proprietário canônico não pode ser desativada.",
        )

    if user.has_password:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A senha atual é obrigatória para desativar a conta.",
            )
        cred = session.scalar(select(LocalCredential).where(LocalCredential.user_id == user.id))
        if cred is None or not verify_password(cred.password_hash, password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha incorreta.",
            )

    user.status = "deactivated"
    user.deactivated_at = utc_now()

    # Revoga todas as sessões ativas
    session.execute(delete(UserSession).where(UserSession.user_id == user.id))
    log_event(
        session=session,
        event_type="account_deactivated",
        user_id=user.id,
        actor_username=user.username,
        details={"status": "deactivated"},
    )
    session.flush()
    logger.info("Conta de %s desativada com sucesso.", user.username)


def reactivate_account(
    session: Session,
    username_or_email: str,
    password: str | None = None,
    google_credential: str | None = None,
) -> User:
    """
    Reativa explicitamente uma conta desativada (Opção B).
    Valida credenciais (senha ou token Google) antes de restaurar o status para 'ativo'.
    """
    clean_id = username_or_email.strip().lower()
    clean_username = clean_id.lstrip("@")

    stmt = select(User).where(
        or_(
            func.lower(User.username) == clean_username,
            func.lower(User.email) == clean_id,
            User.username == username_or_email,
            User.email == username_or_email,
        )
    )
    user = session.scalar(stmt)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciais inválidas ou conta não encontrada.",
        )

    if user.status != "deactivated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A conta informada não está desativada.",
        )

    # Validação da forma de autenticação para reativação
    authenticated = False
    if password and user.has_password:
        cred = session.scalar(select(LocalCredential).where(LocalCredential.user_id == user.id))
        if cred is not None and verify_password(cred.password_hash, password):
            authenticated = True

    if not authenticated and google_credential:
        try:
            payload = verify_google_id_token(google_credential)
            # Verifica se sub ou email correspondem a este usuário
            ident = session.scalar(
                select(ExternalIdentity).where(
                    ExternalIdentity.user_id == user.id,
                    ExternalIdentity.provider == "google",
                    ExternalIdentity.provider_subject == payload.sub,
                )
            )
            if ident is not None or (user.email and payload.email and user.email.lower() == payload.email.lower()):
                authenticated = True
        except Exception:
            pass

    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciais incorretas para reativação.",
        )

    user.status = "ativo"
    user.deactivated_at = None
    user.failed_login_attempts = 0
    user.locked_until = None

    log_event(
        session=session,
        event_type="account_reactivated",
        user_id=user.id,
        actor_username=user.username,
        details={"status": "ativo"},
    )
    session.flush()
    logger.info("Conta de %s reativada com sucesso.", user.username)
    return user


def delete_account_permanently(
    session: Session,
    user: User,
    confirmation_text: str,
    password: str | None = None,
) -> None:
    """
    Exclui fisicamente a conta do usuário e todo o seu acervo em transação atômica (LGPD - Opção A).
    Preserva a integridade referencial executando a remoção estrita em cascata.
    """
    if user.id == DEFAULT_OWNER_ID or user.username == DEFAULT_OWNER_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O proprietário canônico do sistema não pode ser excluído.",
        )

    if confirmation_text.strip() != user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O texto de confirmação deve ser exatamente o seu nome de usuário.",
        )

    if user.has_password:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A senha atual é obrigatória para excluir a conta.",
            )
        cred = session.scalar(select(LocalCredential).where(LocalCredential.user_id == user.id))
        if cred is None or not verify_password(cred.password_hash, password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha incorreta.",
            )

    username_copy = user.username
    user_id_copy = user.id

    # 1. Registra evento de auditoria preservado antes da deleção do usuário
    log_event(
        session=session,
        event_type="account_deleted",
        user_id=None,
        actor_username=username_copy,
        details={"deleted_user_id": user_id_copy, "reason": "user_requested_deletion_lgpd"},
    )

    # 2. Desvincula user_id dos logs de auditoria existentes para integridade limpa
    session.execute(
        update(AuditLog)
        .where(AuditLog.user_id == user_id_copy)
        .values(user_id=None)
    )

    # 3. Exclusão física em cascata transacional
    # Sessões, credenciais e identidades externas
    session.execute(delete(UserSession).where(UserSession.user_id == user_id_copy))
    session.execute(delete(LocalCredential).where(LocalCredential.user_id == user_id_copy))
    session.execute(delete(ExternalIdentity).where(ExternalIdentity.user_id == user_id_copy))
    session.execute(delete(SearchHistory).where(SearchHistory.user_id == user_id_copy))
    session.execute(delete(Notification).where(Notification.user_id == user_id_copy))

    # Amizades (onde for participante)
    session.execute(
        delete(Friendship).where(
            or_(
                Friendship.user_id_a == user_id_copy,
                Friendship.user_id_b == user_id_copy,
                Friendship.action_user_id == user_id_copy,
            )
        )
    )

    # Permissões de compartilhamento
    session.execute(
        delete(ResourcePermission).where(
            ResourcePermission.granted_to_user_id == user_id_copy
        )
    )

    # Relações semânticas e canvas
    session.execute(delete(StudyRelation).where(StudyRelation.user_id == user_id_copy))
    session.execute(delete(StudyCanvasNode).where(StudyCanvasNode.user_id == user_id_copy))
    session.execute(delete(CanvasFrame).where(CanvasFrame.user_id == user_id_copy))

    # Estudos
    session.execute(delete(Study).where(Study.user_id == user_id_copy))

    # Capítulos, livros e categorias associadas
    user_book_ids = session.scalars(select(Book.id).where(Book.user_id == user_id_copy)).all()
    if user_book_ids:
        session.execute(delete(Chapter).where(Chapter.book_id.in_(user_book_ids)))
        session.execute(delete(book_categories).where(book_categories.c.book_id.in_(user_book_ids)))
    session.execute(delete(Book).where(Book.user_id == user_id_copy))

    # Categorias personalizadas
    session.execute(delete(Category).where(Category.user_id == user_id_copy))

    # Perfil e preferências
    session.execute(delete(UserProfile).where(UserProfile.user_id == user_id_copy))
    session.execute(delete(UserPreference).where(UserPreference.user_id == user_id_copy))

    # Finalmente, remove o registro do usuário
    session.expire_all()
    user_to_delete = session.get(User, user_id_copy)
    if user_to_delete:
        session.delete(user_to_delete)
    session.flush()
    logger.info("Conta e acervo de %s (%s) excluídos definitivamente (LGPD).", username_copy, user_id_copy)
