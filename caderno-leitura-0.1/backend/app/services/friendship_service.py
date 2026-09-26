from __future__ import annotations

import logging
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.db.types import utc_now
from app.models.friendship import Friendship
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.friendship import (
    FriendBlockedItem,
    FriendItem,
    FriendRequestItem,
    FriendRequestsResponse,
    FriendsSummaryResponse,
    FriendshipStatusResponse,
    FriendUserRead,
)

logger = logging.getLogger(__name__)


def _extract_friend_user_read(user: User) -> FriendUserRead:
    """Extrai os dados públicos de um usuário incluindo perfil caso disponível."""
    avatar_url = user.profile.avatar_url if hasattr(user, "profile") and user.profile else None
    bio = user.profile.bio if hasattr(user, "profile") and user.profile else None
    return FriendUserRead(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=avatar_url,
        bio=bio,
    )


def is_blocked_between(session: Session, user_id_1: str, user_id_2: str) -> bool:
    """Verifica se há qualquer relação de bloqueio ativa entre dois usuários em qualquer direção."""
    if user_id_1 == user_id_2:
        return False
    u_a, u_b = Friendship.normalize_pair(user_id_1, user_id_2)
    friendship = session.scalar(
        select(Friendship).where(
            Friendship.user_id_a == u_a,
            Friendship.user_id_b == u_b,
            Friendship.status == "blocked",
        )
    )
    return friendship is not None


def is_blocked_by(session: Session, target_user_id: str, by_user_id: str) -> bool:
    """Verifica se o usuário `by_user_id` bloqueou o usuário `target_user_id`."""
    if target_user_id == by_user_id:
        return False
    u_a, u_b = Friendship.normalize_pair(target_user_id, by_user_id)
    friendship = session.scalar(
        select(Friendship).where(
            Friendship.user_id_a == u_a,
            Friendship.user_id_b == u_b,
            Friendship.status == "blocked",
            Friendship.action_user_id == by_user_id,
        )
    )
    return friendship is not None


def get_blocked_user_ids_bilateral(session: Session, user_id: str) -> set[str]:
    """Retorna os IDs de todos os usuários com bloqueio ativo bilateralmente."""
    stmt = select(Friendship).where(
        or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
        Friendship.status == "blocked",
    )
    friendships = session.scalars(stmt).all()
    blocked_ids: set[str] = set()
    for f in friendships:
        blocked_ids.add(f.user_id_b if f.user_id_a == user_id else f.user_id_a)
    return blocked_ids


def send_friend_request(session: Session, sender: User, target_username: str) -> Friendship:
    """Envia uma nova solicitação de amizade para o usuário informado por @username.

    Caso o destinatário já tenha enviado uma solicitação ao remetente (solicitações cruzadas),
    a conexão é automaticamente convertida para 'accepted' em transação atômica.
    """
    clean_username = target_username.strip().lower()
    target_user = session.scalar(
        select(User)
        .options(joinedload(User.profile))
        .where(func.lower(User.username) == clean_username)
    )
    if target_user is None or target_user.status != "ativo":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    if target_user.id == sender.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode enviar uma solicitação de amizade para si mesmo.",
        )

    u_a, u_b = Friendship.normalize_pair(sender.id, target_user.id)
    friendship = session.scalar(
        select(Friendship).where(
            Friendship.user_id_a == u_a,
            Friendship.user_id_b == u_b,
        )
    )

    if friendship is not None:
        if friendship.status == "blocked":
            if friendship.action_user_id == target_user.id:
                # Blindagem anti-enumeração: age como se o usuário não existisse
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você bloqueou este usuário. Desbloqueie-o antes de enviar uma solicitação.",
            )

        if friendship.status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vocês já são amigos.",
            )

        if friendship.status == "pending":
            if friendship.action_user_id == sender.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Você já enviou uma solicitação de amizade para este usuário.",
                )
            # Solicitação cruzada simultânea: o outro já havia solicitado, aceita automaticamente
            friendship.status = "accepted"
            friendship.action_user_id = sender.id
            friendship.updated_at = utc_now()
            session.flush()
            logger.info("Solicitações cruzadas entre %s e %s aceitas automaticamente", sender.username, target_user.username)
            return friendship

    now = utc_now()
    new_friendship = Friendship(
        user_id_a=u_a,
        user_id_b=u_b,
        status="pending",
        action_user_id=sender.id,
        created_at=now,
        updated_at=now,
    )
    session.add(new_friendship)
    session.flush()
    logger.info("Solicitação de amizade enviada de %s para %s", sender.username, target_user.username)
    return new_friendship


def accept_friend_request(session: Session, current_user: User, request_id: int) -> Friendship:
    """Aceita uma solicitação pendente recebida pelo usuário atual."""
    friendship = session.get(Friendship, request_id)
    if friendship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação de amizade não encontrada.",
        )

    if current_user.id not in (friendship.user_id_a, friendship.user_id_b):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada.",
        )

    if friendship.status == "accepted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta solicitação já foi aceita anteriormente.",
        )

    if friendship.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta solicitação não está mais pendente.",
        )

    if friendship.action_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode aceitar a solicitação que você mesmo enviou.",
        )

    friendship.status = "accepted"
    friendship.action_user_id = current_user.id
    friendship.updated_at = utc_now()
    session.flush()
    logger.info("Solicitação de amizade #%d aceita por %s", request_id, current_user.username)
    return friendship


def reject_friend_request(session: Session, current_user: User, request_id: int) -> None:
    """Recusa uma solicitação pendente recebida, removendo-a e restaurando o estado neutro."""
    friendship = session.get(Friendship, request_id)
    if friendship is None or current_user.id not in (friendship.user_id_a, friendship.user_id_b):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada.",
        )

    if friendship.action_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode recusar sua própria solicitação. Use cancelar.",
        )

    if friendship.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta solicitação não está pendente.",
        )

    session.delete(friendship)
    session.flush()
    logger.info("Solicitação de amizade #%d recusada por %s", request_id, current_user.username)


def cancel_friend_request(session: Session, current_user: User, request_id: int) -> None:
    """Cancela uma solicitação pendente enviada pelo usuário atual."""
    friendship = session.get(Friendship, request_id)
    if friendship is None or current_user.id not in (friendship.user_id_a, friendship.user_id_b):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada.",
        )

    if friendship.action_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode cancelar solicitações que você mesmo enviou.",
        )

    if friendship.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta solicitação não está pendente.",
        )

    session.delete(friendship)
    session.flush()
    logger.info("Solicitação de amizade #%d cancelada pelo remetente %s", request_id, current_user.username)


def remove_friendship(session: Session, current_user: User, target_username: str) -> None:
    """Desfaz um vínculo de amizade aceito ativo entre os usuários."""
    clean_username = target_username.strip().lower()
    target_user = session.scalar(
        select(User).where(func.lower(User.username) == clean_username)
    )
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    u_a, u_b = Friendship.normalize_pair(current_user.id, target_user.id)
    friendship = session.scalar(
        select(Friendship).where(
            Friendship.user_id_a == u_a,
            Friendship.user_id_b == u_b,
            Friendship.status == "accepted",
        )
    )
    if friendship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vínculo de amizade ativo não encontrado.",
        )

    session.delete(friendship)
    session.flush()
    logger.info("Amizade entre %s e %s desfeita", current_user.username, target_user.username)


def block_user(session: Session, current_user: User, target_username: str) -> Friendship:
    """Bloqueia um usuário a partir de qualquer estado prévio, dissolvendo amizades ou solicitações."""
    clean_username = target_username.strip().lower()
    target_user = session.scalar(
        select(User).where(func.lower(User.username) == clean_username)
    )
    if target_user is None or target_user.status != "ativo":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode bloquear a si mesmo.",
        )

    u_a, u_b = Friendship.normalize_pair(current_user.id, target_user.id)
    friendship = session.scalar(
        select(Friendship).where(
            Friendship.user_id_a == u_a,
            Friendship.user_id_b == u_b,
        )
    )

    now = utc_now()
    if friendship is not None:
        friendship.status = "blocked"
        friendship.action_user_id = current_user.id
        friendship.updated_at = now
        session.flush()
    else:
        friendship = Friendship(
            user_id_a=u_a,
            user_id_b=u_b,
            status="blocked",
            action_user_id=current_user.id,
            created_at=now,
            updated_at=now,
        )
        session.add(friendship)
        session.flush()

    logger.info("Usuário %s bloqueou %s", current_user.username, target_user.username)
    return friendship


def unblock_user(session: Session, current_user: User, target_username: str) -> None:
    """Desbloqueia um usuário previamente bloqueado pelo usuário atual."""
    clean_username = target_username.strip().lower()
    target_user = session.scalar(
        select(User).where(func.lower(User.username) == clean_username)
    )
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    u_a, u_b = Friendship.normalize_pair(current_user.id, target_user.id)
    friendship = session.scalar(
        select(Friendship).where(
            Friendship.user_id_a == u_a,
            Friendship.user_id_b == u_b,
            Friendship.status == "blocked",
        )
    )
    if friendship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum bloqueio ativo encontrado para este usuário.",
        )

    if friendship.action_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para remover o bloqueio aplicado por outro usuário.",
        )

    session.delete(friendship)
    session.flush()
    logger.info("Usuário %s desbloqueou %s", current_user.username, target_user.username)


def get_user_friends(session: Session, user_id: str) -> list[FriendItem]:
    """Retorna a lista de amigos aceitos ativos do usuário ordenados por atualização mais recente."""
    stmt = (
        select(Friendship)
        .options(
            joinedload(Friendship.user_a).joinedload(User.profile),
            joinedload(Friendship.user_b).joinedload(User.profile),
        )
        .where(
            or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
            Friendship.status == "accepted",
        )
        .order_by(Friendship.updated_at.desc())
    )
    friendships = session.scalars(stmt).all()
    results: list[FriendItem] = []
    for f in friendships:
        partner = f.user_b if f.user_id_a == user_id else f.user_a
        results.append(
            FriendItem(
                friendship_id=f.id,
                user=_extract_friend_user_read(partner),
                since=f.updated_at,
            )
        )
    return results


def get_friend_requests(session: Session, user_id: str) -> FriendRequestsResponse:
    """Retorna as solicitações pendentes separadas em recebidas e enviadas."""
    stmt = (
        select(Friendship)
        .options(
            joinedload(Friendship.user_a).joinedload(User.profile),
            joinedload(Friendship.user_b).joinedload(User.profile),
        )
        .where(
            or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
            Friendship.status == "pending",
        )
        .order_by(Friendship.created_at.desc())
    )
    friendships = session.scalars(stmt).all()
    received: list[FriendRequestItem] = []
    sent: list[FriendRequestItem] = []

    for f in friendships:
        if f.action_user_id == user_id:
            # Enviada por mim para o parceiro
            partner = f.user_b if f.user_id_a == user_id else f.user_a
            sent.append(
                FriendRequestItem(
                    request_id=f.id,
                    user=_extract_friend_user_read(partner),
                    direction="sent",
                    created_at=f.created_at,
                )
            )
        else:
            # Enviada pelo parceiro para mim
            partner = f.user_b if f.user_id_a == user_id else f.user_a
            received.append(
                FriendRequestItem(
                    request_id=f.id,
                    user=_extract_friend_user_read(partner),
                    direction="received",
                    created_at=f.created_at,
                )
            )

    return FriendRequestsResponse(received=received, sent=sent)


def get_blocked_users(session: Session, user_id: str) -> list[FriendBlockedItem]:
    """Retorna os usuários que foram bloqueados pelo usuário atual."""
    stmt = (
        select(Friendship)
        .options(
            joinedload(Friendship.user_a).joinedload(User.profile),
            joinedload(Friendship.user_b).joinedload(User.profile),
        )
        .where(
            Friendship.status == "blocked",
            Friendship.action_user_id == user_id,
        )
        .order_by(Friendship.updated_at.desc())
    )
    friendships = session.scalars(stmt).all()
    results: list[FriendBlockedItem] = []
    for f in friendships:
        blocked_user = f.user_b if f.user_id_a == user_id else f.user_a
        results.append(
            FriendBlockedItem(
                friendship_id=f.id,
                user=_extract_friend_user_read(blocked_user),
                blocked_at=f.updated_at,
            )
        )
    return results


def get_friends_summary(session: Session, user_id: str) -> FriendsSummaryResponse:
    """Retorna contadores consolidados de amizades e solicitações para crachás de navegação."""
    stmt_friends = select(func.count(Friendship.id)).where(
        or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
        Friendship.status == "accepted",
    )
    friends_count = session.scalar(stmt_friends) or 0

    stmt_received = select(func.count(Friendship.id)).where(
        or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
        Friendship.status == "pending",
        Friendship.action_user_id != user_id,
    )
    pending_received = session.scalar(stmt_received) or 0

    stmt_sent = select(func.count(Friendship.id)).where(
        or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
        Friendship.status == "pending",
        Friendship.action_user_id == user_id,
    )
    pending_sent = session.scalar(stmt_sent) or 0

    return FriendsSummaryResponse(
        friends_count=friends_count,
        pending_received_count=pending_received,
        pending_sent_count=pending_sent,
    )


def get_relation_status(
    session: Session,
    current_user_id: str,
    target_username: str,
) -> FriendshipStatusResponse:
    """Obtém o estado da relação sob a perspectiva do usuário atual."""
    clean_username = target_username.strip().lower()
    target_user = session.scalar(
        select(User).where(func.lower(User.username) == clean_username)
    )
    if target_user is None or target_user.id == current_user_id:
        return FriendshipStatusResponse(relation_status="none")

    u_a, u_b = Friendship.normalize_pair(current_user_id, target_user.id)
    friendship = session.scalar(
        select(Friendship).where(
            Friendship.user_id_a == u_a,
            Friendship.user_id_b == u_b,
        )
    )

    if friendship is None:
        return FriendshipStatusResponse(relation_status="none")

    if friendship.status == "accepted":
        return FriendshipStatusResponse(
            relation_status="friends",
            request_id=friendship.id,
            since=friendship.updated_at,
        )

    if friendship.status == "pending":
        rel = "pending_sent" if friendship.action_user_id == current_user_id else "pending_received"
        return FriendshipStatusResponse(
            relation_status=rel,
            request_id=friendship.id,
            since=friendship.created_at,
        )

    if friendship.status == "blocked":
        rel = "blocked_by_me" if friendship.action_user_id == current_user_id else "blocked_by_them"
        return FriendshipStatusResponse(
            relation_status=rel,
            request_id=friendship.id,
            since=friendship.updated_at,
        )

    return FriendshipStatusResponse(relation_status="none")
