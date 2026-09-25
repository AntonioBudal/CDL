from __future__ import annotations

import logging
import re
import uuid

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_allow_registration
from app.models.external_identity import ExternalIdentity
from app.models.local_credential import LocalCredential
from app.models.user import User
from app.services.google_auth_service import GoogleTokenPayload
from app.services.profile_service import get_or_create_profile

logger = logging.getLogger(__name__)


def _sanitize_username(hint: str) -> str:
    """Normaliza e sanitiza um texto para formar um identificador alfanumérico válido."""
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", hint).strip("._-").lower()
    if len(cleaned) < 3:
        cleaned = f"leitor_{cleaned}" if cleaned else "leitor"
    return cleaned[:40]


def generate_unique_username(session: Session, hint: str | None) -> str:
    """Gera um nome de usuário (@username) único e legível no banco de dados."""
    base = _sanitize_username(hint or "leitor")
    candidate = base

    # Tenta usar o base diretamente
    existing = session.scalar(select(User.id).where(User.username == candidate))
    if not existing:
        return candidate

    # Gera sufixo numérico/aleatório
    for i in range(1, 100):
        candidate = f"{base}_{i}"
        existing = session.scalar(select(User.id).where(User.username == candidate))
        if not existing:
            return candidate

    # Fallback aleatório
    return f"{base}_{uuid.uuid4().hex[:6]}"


def authenticate_google_user(session: Session, payload: GoogleTokenPayload) -> User:
    """Autentica ou provisiona usuário a partir de credencial verificada do Google.

    1. Se existir vínculo com provider_subject (claim 'sub'), retorna o usuário correspondente.
    2. Se não existir vínculo prévio, mas o e-mail for verificado (email_verified=True) e coincidir
       com usuário local existente, vincula a identidade automaticamente e retorna o usuário.
    3. Se o usuário for inédito:
       - Se auto-registro estiver desativado: lança HTTP 403 Forbidden.
       - Se auto-registro estiver ativo: cria novo usuário com @username único e vincula identidade.
    """
    # 1. Busca por vínculo estável de sub
    stmt = (
        select(ExternalIdentity)
        .options(joinedload(ExternalIdentity.user).joinedload(User.credential))
        .options(joinedload(ExternalIdentity.user).joinedload(User.external_identities))
        .where(
            ExternalIdentity.provider == "google",
            ExternalIdentity.provider_subject == payload.sub,
        )
    )
    identity = session.scalar(stmt)
    if identity is not None:
        user = identity.user
        if user.status != "ativo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta de usuário suspensa ou inativa.",
            )
        return user

    # 2. Tentativa de auto-vinculação por e-mail verificado
    if payload.email and payload.email_verified:
        existing_user = session.scalar(
            select(User)
            .options(joinedload(User.credential))
            .options(joinedload(User.external_identities))
            .where(User.email == payload.email)
        )
        if existing_user is not None:
            if existing_user.status != "ativo":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Conta de usuário suspensa ou inativa.",
                )
            # Cria vínculo na conta existente
            new_identity = ExternalIdentity(
                user_id=existing_user.id,
                provider="google",
                provider_subject=payload.sub,
                email_at_link=payload.email,
            )
            session.add(new_identity)
            session.flush()
            # Recarrega identidades externas para atualizar propriedades
            session.refresh(existing_user)
            logger.info(
                "Conta existente %s auto-vinculada ao Google (sub=%s)",
                existing_user.username,
                payload.sub,
            )
            return existing_user

    # 3. Primeiro acesso de conta inédita
    if not get_allow_registration():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Novos cadastros de leitores estão desativados pelo administrador.",
        )

    # Rejeita e-mail não verificado na criação automática de conta
    if payload.email and not payload.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O e-mail da conta Google deve estar confirmado/verificado pelo Google.",
        )

    hint = payload.email.split("@")[0] if payload.email else payload.name
    username = generate_unique_username(session, hint)
    display_name = payload.name or hint or "Leitor Google"

    new_user = User(
        username=username,
        display_name=display_name,
        email=payload.email,
        role="user",
        status="ativo",
    )
    session.add(new_user)
    session.flush()

    new_identity = ExternalIdentity(
        user_id=new_user.id,
        provider="google",
        provider_subject=payload.sub,
        email_at_link=payload.email,
    )
    session.add(new_identity)
    get_or_create_profile(new_user, session)
    session.flush()
    session.refresh(new_user)

    logger.info("Novo usuário criado via Google: %s (%s)", new_user.username, new_user.id)
    return new_user


def link_google_identity(session: Session, user: User, payload: GoogleTokenPayload) -> ExternalIdentity:
    """Vincula manualmente a conta Google a um usuário já autenticado no painel de Ajustes."""
    # Verifica se a identidade já está vinculada a algum usuário
    existing_identity = session.scalar(
        select(ExternalIdentity).where(
            ExternalIdentity.provider == "google",
            ExternalIdentity.provider_subject == payload.sub,
        )
    )
    if existing_identity is not None:
        if existing_identity.user_id == user.id:
            return existing_identity
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta conta Google já está vinculada a outro leitor do sistema.",
        )

    # Cria novo vínculo para o usuário logado
    identity = ExternalIdentity(
        user_id=user.id,
        provider="google",
        provider_subject=payload.sub,
        email_at_link=payload.email,
    )
    session.add(identity)
    session.flush()
    session.refresh(user)
    logger.info("Conta Google vinculada com sucesso ao usuário %s", user.username)
    return identity


def unlink_google_identity(session: Session, user: User) -> None:
    """Desvincula a conta Google do usuário com proteção estrita contra lockout."""
    # 1. Proteção contra Lockout: exige senha local ativa
    if not user.has_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você precisa definir uma senha local antes de desvincular sua conta Google para evitar perda de acesso.",
        )

    # 2. Busca e remove o registro de external_identity
    identity = session.scalar(
        select(ExternalIdentity).where(
            ExternalIdentity.user_id == user.id,
            ExternalIdentity.provider == "google",
        )
    )
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma conta Google vinculada a este perfil.",
        )

    session.delete(identity)
    session.flush()
    session.refresh(user)
    logger.info("Conta Google desvinculada do usuário %s", user.username)
