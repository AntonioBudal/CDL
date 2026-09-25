from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import joinedload

from app.core.auth import get_or_create_default_owner, get_user_by_id
from app.core.config import (
    DEFAULT_OWNER_ID,
    DEFAULT_OWNER_USERNAME,
    PASSWORD_MIN_LENGTH,
    SESSION_COOKIE_NAME,
    get_allow_registration,
    get_google_client_id,
    is_google_auth_enabled,
)
from app.core.security import hash_password, hash_session_token, needs_rehash, verify_password
from app.dependencies import CurrentUser, DatabaseSession
from app.models.local_credential import LocalCredential
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.auth import (
    AuthConfigResponse,
    AuthSuccessResponse,
    ExternalIdentityRead,
    GoogleAuthRequest,
    LoginRequest,
    LogoutAllResponse,
    LogoutResponse,
    RegisterRequest,
    SessionItem,
    SetupOwnerRequest,
)
from app.schemas.user import UserRead
from app.services.auth_service import (
    authenticate_google_user,
    link_google_identity,
    unlink_google_identity,
)
from app.services.profile_service import get_or_create_profile
from app.services.google_auth_service import (
    GoogleAuthDisabledError,
    InvalidGoogleTokenError,
    verify_google_id_token,
)
from app.services.session_service import (
    clear_session_cookie,
    create_session,
    get_user_sessions,
    revoke_all_other_sessions,
    revoke_session,
    set_session_cookie,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


@router.get("/config", response_model=AuthConfigResponse, summary="Obter configurações públicas de autenticação")
def get_auth_config(session: DatabaseSession) -> AuthConfigResponse:
    """Retorna flags de configuração pública da autenticação (auto-registro e necessidade de primeiro acesso)."""
    allow_reg = get_allow_registration()

    owner = get_user_by_id(session, DEFAULT_OWNER_ID)
    if owner is None:
        stmt = select(User).where(User.username == DEFAULT_OWNER_USERNAME)
        owner = session.scalar(stmt)

    if owner is None:
        owner_setup_required = True
    else:
        cred = session.scalar(
            select(LocalCredential).where(LocalCredential.user_id == owner.id)
        )
        owner_setup_required = cred is None

    return AuthConfigResponse(
        allow_registration=allow_reg,
        owner_setup_required=owner_setup_required,
        google_auth_enabled=is_google_auth_enabled(),
        google_client_id=get_google_client_id(),
    )


@router.get("/me", response_model=UserRead, summary="Obter dados do usuário autenticado")
def get_me(current_user: CurrentUser) -> UserRead:
    """Retorna os dados do usuário autenticado no contexto da requisição atual."""
    return current_user


@router.post(
    "/login",
    response_model=AuthSuccessResponse,
    summary="Autenticar usuário com credenciais locais",
)
def login(
    login_req: LoginRequest,
    request: Request,
    response: Response,
    session: DatabaseSession,
) -> AuthSuccessResponse:
    """Autentica o usuário validando nome de usuário/e-mail e senha com Argon2id.

    Emite cookie seguro HttpOnly 'caderno_session' com janela deslizante de 30 dias.
    """
    identifier = login_req.username_or_email.strip()
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas ou conta inativa.",
        )

    stmt = (
        select(User)
        .options(joinedload(User.credential))
        .where(
            or_(
                User.username == identifier,
                User.email == identifier,
            )
        )
    )
    user = session.scalar(stmt)

    if user is None or user.status != "ativo" or user.credential is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas ou conta inativa.",
        )

    if not verify_password(user.credential.password_hash, login_req.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas ou conta inativa.",
        )

    if needs_rehash(user.credential.password_hash):
        user.credential.password_hash = hash_password(login_req.password)
        session.flush()

    client_ip = _get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")

    user_session, raw_token = create_session(session, user.id, client_ip, user_agent)
    set_session_cookie(response, raw_token, request)

    return AuthSuccessResponse(user=user, session_id=user_session.id)


@router.post(
    "/setup-owner",
    response_model=AuthSuccessResponse,
    summary="Definir senha mestra inicial do proprietário canônico",
)
def setup_owner(
    req: SetupOwnerRequest,
    request: Request,
    response: Response,
    session: DatabaseSession,
) -> AuthSuccessResponse:
    """Configura a senha mestra inicial para o proprietário canônico legado."""
    owner = get_or_create_default_owner(session)

    existing_cred = session.scalar(
        select(LocalCredential).where(LocalCredential.user_id == owner.id)
    )
    if existing_cred is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O proprietário já possui senha mestra configurada.",
        )

    if len(req.password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A senha deve conter no mínimo {PASSWORD_MIN_LENGTH} caracteres.",
        )

    cred = LocalCredential(
        user_id=owner.id,
        password_hash=hash_password(req.password),
    )
    session.add(cred)
    session.flush()

    client_ip = _get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    user_session, raw_token = create_session(session, owner.id, client_ip, user_agent)
    set_session_cookie(response, raw_token, request)

    return AuthSuccessResponse(user=owner, session_id=user_session.id)


@router.post(
    "/register",
    response_model=AuthSuccessResponse,
    summary="Cadastrar novo usuário leitor independente",
)
def register(
    req: RegisterRequest,
    request: Request,
    response: Response,
    session: DatabaseSession,
) -> AuthSuccessResponse:
    """Registra uma nova conta com credenciais locais quando o auto-registro estiver habilitado."""
    if not get_allow_registration():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O cadastro de novos usuários está desativado neste servidor.",
        )

    username_clean = req.username.strip()
    display_name_clean = req.display_name.strip()
    email_clean = req.email.strip() if req.email and req.email.strip() else None

    if len(req.password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A senha deve conter no mínimo {PASSWORD_MIN_LENGTH} caracteres.",
        )

    existing_user = session.scalar(
        select(User).where(User.username == username_clean)
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de usuário já está em uso.",
        )

    if email_clean:
        existing_email = session.scalar(
            select(User).where(User.email == email_clean)
        )
        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já está em uso.",
            )

    new_user = User(
        username=username_clean,
        display_name=display_name_clean,
        email=email_clean,
        role="user",
        status="ativo",
    )
    session.add(new_user)
    session.flush()

    cred = LocalCredential(
        user_id=new_user.id,
        password_hash=hash_password(req.password),
    )
    session.add(cred)
    get_or_create_profile(new_user, session)
    session.flush()

    client_ip = _get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    user_session, raw_token = create_session(session, new_user.id, client_ip, user_agent)
    set_session_cookie(response, raw_token, request)

    return AuthSuccessResponse(user=new_user, session_id=user_session.id)


@router.get(
    "/sessions",
    response_model=list[SessionItem],
    summary="Listar sessões ativas do usuário conectado",
)
def list_sessions(
    current_user: CurrentUser,
    request: Request,
    session: DatabaseSession,
) -> list[SessionItem]:
    """Retorna todas as sessões ativas da conta autenticada, marcando qual é a atual."""
    current_session_id = getattr(request.state, "current_session_id", None)
    return get_user_sessions(session, current_user.id, current_session_id)


@router.delete(
    "/sessions/{session_id}",
    response_model=LogoutResponse,
    summary="Revogar sessão específica do usuário conectado",
)
def delete_session(
    session_id: str,
    current_user: CurrentUser,
    request: Request,
    response: Response,
    session: DatabaseSession,
) -> LogoutResponse:
    """Revoga uma sessão ativa. Se for a sessão atual, limpa também o cookie do navegador."""
    current_session_id = getattr(request.state, "current_session_id", None)
    revoked = revoke_session(session, current_user.id, session_id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada ou não pertence ao usuário.",
        )

    if current_session_id and current_session_id == session_id:
        clear_session_cookie(response, request)

    return LogoutResponse(ok=True)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Encerrar sessão atual (logout pontual)",
)
def logout(
    current_user: CurrentUser,
    request: Request,
    response: Response,
    session: DatabaseSession,
) -> LogoutResponse:
    """Encerra a sessão ativa do usuário atual e limpa o cookie HttpOnly."""
    current_session_id = getattr(request.state, "current_session_id", None)
    if current_session_id:
        revoke_session(session, current_user.id, current_session_id)
    else:
        raw_token = request.cookies.get(SESSION_COOKIE_NAME)
        if raw_token:
            token_hash = hash_session_token(raw_token.strip())
            session.execute(
                delete(UserSession).where(UserSession.session_token_hash == token_hash)
            )
            session.flush()

    clear_session_cookie(response, request)
    return LogoutResponse(ok=True)


@router.post(
    "/logout-all",
    response_model=LogoutAllResponse,
    summary="Revogar todas as outras sessões ativas do usuário",
)
def logout_all_other(
    current_user: CurrentUser,
    request: Request,
    session: DatabaseSession,
) -> LogoutAllResponse:
    """Revoga todas as sessões do usuário conectado, exceto a sessão ativa em uso."""
    current_session_id = getattr(request.state, "current_session_id", None)
    if current_session_id:
        count = revoke_all_other_sessions(session, current_user.id, current_session_id)
    else:
        stmt = delete(UserSession).where(UserSession.user_id == current_user.id)
        result = session.execute(stmt)
        session.flush()
        count = result.rowcount or 0

    return LogoutAllResponse(revoked_count=count)


@router.post(
    "/google",
    response_model=AuthSuccessResponse,
    summary="Autenticar usuário via Google Identity Services (GIS)",
)
def login_with_google(
    req: GoogleAuthRequest,
    request: Request,
    response: Response,
    session: DatabaseSession,
) -> AuthSuccessResponse:
    """Autentica ou provisiona leitor a partir do ID Token verificado do Google GIS."""
    try:
        payload = verify_google_id_token(req.credential)
    except GoogleAuthDisabledError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except InvalidGoogleTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    user = authenticate_google_user(session, payload)

    client_ip = _get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")

    user_session, raw_token = create_session(session, user.id, client_ip, user_agent)
    set_session_cookie(response, raw_token, request)

    return AuthSuccessResponse(user=user, session_id=user_session.id)


@router.post(
    "/google/link",
    response_model=ExternalIdentityRead,
    summary="Vincular conta Google ao usuário autenticado",
)
def link_google(
    req: GoogleAuthRequest,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> ExternalIdentityRead:
    """Vincula uma conta Google à conta do leitor autenticado."""
    try:
        payload = verify_google_id_token(req.credential)
    except GoogleAuthDisabledError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except InvalidGoogleTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    identity = link_google_identity(session, current_user, payload)
    return ExternalIdentityRead(
        id=identity.id,
        provider=identity.provider,
        email_at_link=identity.email_at_link,
        created_at=identity.created_at,
    )


@router.delete(
    "/google/unlink",
    summary="Desvincular conta Google do usuário autenticado",
)
def unlink_google(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> dict[str, bool]:
    """Desvincula a conta Google associada ao usuário autenticado com prevenção de lockout."""
    unlink_google_identity(session, current_user)
    return {"ok": True}

