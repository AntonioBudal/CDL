from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Query, status

from app.dependencies import AdminUser, DatabaseSession
from app.schemas.admin import (
    AdminReactivateResponse,
    AdminRevokeSessionsResponse,
    AdminRoleUpdateRequest,
    AdminRoleUpdateResponse,
    AdminStatsSummary,
    AdminSuspendRequest,
    AdminSuspendResponse,
    AdminUsersResponse,
)
from app.schemas.notification import (
    NotificationBroadcastRequest,
    NotificationBroadcastResponse,
    NotificationPurgeResponse,
)
from app.services import admin_service, notification_service
from app.services.persistence import commit_changes

router = APIRouter(prefix="/admin", tags=["Administração"])


@router.get("/users", response_model=AdminUsersResponse)
def get_admin_users(
    session: DatabaseSession,
    current_admin: AdminUser,
    q: Annotated[str | None, Query(description="Busca textual por username, nome ou e-mail")] = None,
    status: Annotated[str, Query(description="Filtro de status: all, ativo, suspenso")] = "all",
    role: Annotated[str, Query(description="Filtro de papel: all, user, admin")] = "all",
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AdminUsersResponse:
    """Retorna lista paginada de contas com métricas agregadas (exclusivo para administradores)."""
    items, total = admin_service.list_users(
        session=session,
        q=q,
        status_filter=status,
        role_filter=role,
        limit=limit,
        offset=offset,
    )
    return AdminUsersResponse(items=items, total=total)


@router.get("/stats", response_model=AdminStatsSummary)
def get_admin_stats(
    session: DatabaseSession,
    current_admin: AdminUser,
) -> AdminStatsSummary:
    """Retorna indicadores agregados do sistema para o painel administrativo."""
    return admin_service.get_admin_stats(session=session)


@router.post("/users/{user_id}/suspend", response_model=AdminSuspendResponse)
def suspend_user_endpoint(
    user_id: str,
    session: DatabaseSession,
    current_admin: AdminUser,
    payload: AdminSuspendRequest | None = None,
) -> AdminSuspendResponse:
    """Suspende a conta indicada e invalida imediatamente todas as suas sessões ativas."""
    reason = payload.reason if payload else None
    target_user, sessions_revoked = admin_service.suspend_user(
        session=session,
        target_user_id=user_id,
        current_user=current_admin,
        reason=reason,
    )
    return AdminSuspendResponse(
        id=target_user.id,
        status="suspenso",
        sessions_revoked=sessions_revoked,
        message=f"Conta de @{target_user.username} suspensa com sucesso. {sessions_revoked} sessão(ões) revogada(s).",
    )


@router.post("/users/{user_id}/reactivate", response_model=AdminReactivateResponse)
def reactivate_user_endpoint(
    user_id: str,
    session: DatabaseSession,
    current_admin: AdminUser,
) -> AdminReactivateResponse:
    """Restaura o status da conta para ativo, permitindo novos logins."""
    target_user = admin_service.reactivate_user(
        session=session,
        target_user_id=user_id,
        current_user=current_admin,
    )
    return AdminReactivateResponse(
        id=target_user.id,
        status="ativo",
        message=f"Conta de @{target_user.username} reativada com sucesso.",
    )


@router.put("/users/{user_id}/role", response_model=AdminRoleUpdateResponse)
def update_user_role_endpoint(
    user_id: str,
    payload: AdminRoleUpdateRequest,
    session: DatabaseSession,
    current_admin: AdminUser,
) -> AdminRoleUpdateResponse:
    """Altera o papel de um usuário entre user e admin com salvaguarda anti-lockout."""
    target_user = admin_service.update_user_role(
        session=session,
        target_user_id=user_id,
        new_role=payload.role,
        current_user=current_admin,
    )
    return AdminRoleUpdateResponse(
        id=target_user.id,
        role=target_user.role,  # type: ignore[arg-type]
        message=f"Papel de @{target_user.username} atualizado para {target_user.role} com sucesso.",
    )


@router.post("/users/{user_id}/sessions/revoke-all", response_model=AdminRevokeSessionsResponse)
def revoke_all_sessions_endpoint(
    user_id: str,
    session: DatabaseSession,
    current_admin: AdminUser,
) -> AdminRevokeSessionsResponse:
    """Encerra forçadamente todas as sessões ativas do usuário indicado."""
    sessions_revoked = admin_service.revoke_all_sessions_for_user(
        session=session,
        target_user_id=user_id,
        current_user=current_admin,
    )
    return AdminRevokeSessionsResponse(
        id=user_id,
        sessions_revoked=sessions_revoked,
        message=f"Todas as {sessions_revoked} sessão(ões) foram revogadas com sucesso.",
    )


@router.post(
    "/notifications/broadcast",
    response_model=NotificationBroadcastResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Disparar aviso administrativo em massa",
)
def broadcast_notification_endpoint(
    payload: NotificationBroadcastRequest,
    session: DatabaseSession,
    current_admin: AdminUser,
) -> NotificationBroadcastResponse:
    """Cria notificações institucionais (system_alert) individuais para todos os usuários ativos."""
    dispatched = notification_service.broadcast_system_alert(
        session=session,
        current_admin=current_admin,
        title=payload.title,
        message=payload.message,
        severity=payload.severity,
        link=payload.link,
    )
    commit_changes(session)
    return NotificationBroadcastResponse(
        dispatched_count=dispatched,
        message=f"Aviso emitido com sucesso para {dispatched} leitores ativos.",
    )


@router.post(
    "/notifications/purge",
    response_model=NotificationPurgeResponse,
    summary="Purgar notificações lidas antigas",
)
def purge_notifications_endpoint(
    session: DatabaseSession,
    current_admin: AdminUser,
    retention_days: Annotated[int, Query(ge=1, description="Período de retenção em dias para notificações já lidas")] = 60,
) -> NotificationPurgeResponse:
    """Remove notificações que já foram lidas criadas há mais de retention_days dias."""
    purged = notification_service.purge_expired_notifications(
        session=session,
        retention_days=retention_days,
    )
    commit_changes(session)
    return NotificationPurgeResponse(
        purged_count=purged,
        retention_days=retention_days,
        message=f"{purged} notificações lidas antigas foram purgadas com sucesso.",
    )
