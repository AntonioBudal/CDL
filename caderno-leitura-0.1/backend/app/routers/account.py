from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.rate_limiter import rate_limit_auth_endpoint
from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.account import (
    AccountLifecycleResponse,
    DeactivateAccountRequest,
    DeleteAccountRequest,
    ReactivateAccountRequest,
)
from app.schemas.auth import AuthSuccessResponse
from app.services import account_service, audit_service, export_service
from app.services.persistence import commit_changes
from app.services.session_service import clear_session_cookie, create_session, set_session_cookie

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/account", tags=["Ciclo de Vida da Conta"])


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


@router.post(
    "/deactivate",
    response_model=AccountLifecycleResponse,
    summary="Desativar temporariamente a conta do leitor",
)
def deactivate_account_endpoint(
    current_user: CurrentUser,
    response: Response,
    request: Request,
    session: DatabaseSession,
    payload: DeactivateAccountRequest | None = None,
) -> AccountLifecycleResponse:
    """Desativa temporariamente a conta do leitor e revoga todas as suas sessões ativas."""
    password = payload.password if payload else None
    account_service.deactivate_account(session, current_user, password)
    commit_changes(session)
    clear_session_cookie(response, request)

    return AccountLifecycleResponse(
        ok=True,
        message="Sua conta foi desativada com sucesso. Para voltar a usá-la, basta fazer login e confirmar a reativação.",
    )


@router.post(
    "/reactivate",
    response_model=AuthSuccessResponse,
    dependencies=[Depends(rate_limit_auth_endpoint)],
    summary="Confirmar reativação explícita de conta desativada",
)
def reactivate_account_endpoint(
    payload: ReactivateAccountRequest,
    request: Request,
    response: Response,
    session: DatabaseSession,
) -> AuthSuccessResponse:
    """Restaura o status da conta para 'ativo' após confirmação explícita do titular e inicia nova sessão."""
    user = account_service.reactivate_account(
        session=session,
        username_or_email=payload.username_or_email,
        password=payload.password,
        google_credential=payload.google_credential,
    )

    client_ip = _get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    user_session, raw_token = create_session(session, user.id, client_ip, user_agent)
    commit_changes(session)
    set_session_cookie(response, raw_token, request)

    return AuthSuccessResponse(user=user, session_id=user_session.id)


@router.delete(
    "",
    response_model=AccountLifecycleResponse,
    summary="Excluir definitivamente a conta e todo o acervo (LGPD)",
)
def delete_account_endpoint(
    current_user: CurrentUser,
    payload: DeleteAccountRequest,
    request: Request,
    response: Response,
    session: DatabaseSession,
) -> AccountLifecycleResponse:
    """Remove permanentemente em cascata física a conta, estudos, livros e preferências do usuário."""
    account_service.delete_account_permanently(
        session=session,
        user=current_user,
        confirmation_text=payload.confirmation_text,
        password=payload.password,
    )
    commit_changes(session)
    clear_session_cookie(response, request)

    return AccountLifecycleResponse(
        ok=True,
        message="Sua conta e todo o acervo de leitura foram permanentemente excluídos com sucesso.",
    )


@router.get(
    "/export",
    summary="Baixar pacote ZIP de portabilidade com todo o acervo (LGPD)",
)
def export_account_endpoint(
    current_user: CurrentUser,
    session: DatabaseSession,
    request: Request,
) -> Response:
    """Gera sob demanda o pacote ZIP com árvore de pastas em Markdown e dados_acervo.json."""
    zip_bytes, filename = export_service.generate_account_export_zip(session, current_user)

    audit_service.log_security_event(
        session,
        "account_exported",
        request=request,
        user_id=current_user.id,
        actor_username=current_user.username,
        details={"filename": filename, "size_bytes": len(zip_bytes)},
    )
    commit_changes(session)

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate",
        },
    )

