from __future__ import annotations

import logging

from fastapi import APIRouter, status

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.friendship import (
    FriendBlockedItem,
    FriendItem,
    FriendRequestsResponse,
    FriendsSummaryResponse,
    FriendshipActionResponse,
    FriendshipStatusResponse,
)
from app.services.friendship_service import (
    accept_friend_request,
    block_user,
    cancel_friend_request,
    get_blocked_users,
    get_friend_requests,
    get_friends_summary,
    get_relation_status,
    get_user_friends,
    reject_friend_request,
    remove_friendship,
    send_friend_request,
    unblock_user,
)
from app.services.persistence import commit_changes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/friends", tags=["Amizades e Social"])


@router.post(
    "/request/{username}",
    response_model=FriendshipActionResponse,
    summary="Enviar solicitação de amizade para um usuário",
)
def send_request(
    username: str,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendshipActionResponse:
    friendship = send_friend_request(session, current_user, username)
    commit_changes(session)
    msg = (
        "Vocês agora são amigos!"
        if friendship.status == "accepted"
        else "Solicitação de amizade enviada com sucesso."
    )
    return FriendshipActionResponse(ok=True, message=msg, status=friendship.status)


@router.post(
    "/accept/{request_id}",
    response_model=FriendshipActionResponse,
    summary="Aceitar solicitação de amizade pendente",
)
def accept_request(
    request_id: int,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendshipActionResponse:
    friendship = accept_friend_request(session, current_user, request_id)
    commit_changes(session)
    return FriendshipActionResponse(
        ok=True,
        message="Solicitação de amizade aceita com sucesso.",
        status=friendship.status,
    )


@router.post(
    "/reject/{request_id}",
    response_model=FriendshipActionResponse,
    summary="Recusar solicitação de amizade pendente",
)
def reject_request(
    request_id: int,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendshipActionResponse:
    reject_friend_request(session, current_user, request_id)
    commit_changes(session)
    return FriendshipActionResponse(
        ok=True,
        message="Solicitação de amizade recusada.",
        status="none",
    )


@router.delete(
    "/cancel/{request_id}",
    response_model=FriendshipActionResponse,
    summary="Cancelar solicitação de amizade enviada",
)
def cancel_request(
    request_id: int,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendshipActionResponse:
    cancel_friend_request(session, current_user, request_id)
    commit_changes(session)
    return FriendshipActionResponse(
        ok=True,
        message="Solicitação de amizade cancelada.",
        status="none",
    )


@router.delete(
    "/{username}",
    response_model=FriendshipActionResponse,
    summary="Desfazer amizade ativa com um usuário",
)
def delete_friend(
    username: str,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendshipActionResponse:
    remove_friendship(session, current_user, username)
    commit_changes(session)
    return FriendshipActionResponse(
        ok=True,
        message="Vínculo de amizade desfeito.",
        status="none",
    )


@router.post(
    "/block/{username}",
    response_model=FriendshipActionResponse,
    summary="Bloquear usuário unilateralmente",
)
def block(
    username: str,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendshipActionResponse:
    friendship = block_user(session, current_user, username)
    commit_changes(session)
    return FriendshipActionResponse(
        ok=True,
        message="Usuário bloqueado com sucesso.",
        status=friendship.status,
    )


@router.post(
    "/unblock/{username}",
    response_model=FriendshipActionResponse,
    summary="Desbloquear usuário previamente bloqueado",
)
def unblock(
    username: str,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendshipActionResponse:
    unblock_user(session, current_user, username)
    commit_changes(session)
    return FriendshipActionResponse(
        ok=True,
        message="Usuário desbloqueado com sucesso.",
        status="none",
    )


@router.get(
    "",
    response_model=list[FriendItem],
    summary="Listar amigos aceitos do usuário conectado",
)
def list_friends(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> list[FriendItem]:
    return get_user_friends(session, current_user.id)


@router.get(
    "/requests",
    response_model=FriendRequestsResponse,
    summary="Listar solicitações pendentes recebidas e enviadas",
)
def list_requests(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendRequestsResponse:
    return get_friend_requests(session, current_user.id)


@router.get(
    "/blocked",
    response_model=list[FriendBlockedItem],
    summary="Listar usuários bloqueados pelo usuário conectado",
)
def list_blocked(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> list[FriendBlockedItem]:
    return get_blocked_users(session, current_user.id)


@router.get(
    "/summary",
    response_model=FriendsSummaryResponse,
    summary="Obter resumo e contadores de amizades e solicitações para a UI",
)
def get_summary(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendsSummaryResponse:
    return get_friends_summary(session, current_user.id)


@router.get(
    "/status/{username}",
    response_model=FriendshipStatusResponse,
    summary="Consultar o status da relação com um usuário específico",
)
def check_status(
    username: str,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> FriendshipStatusResponse:
    return get_relation_status(session, current_user.id, username)
