from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import urllib.parse
import requests

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import (
    get_google_client_id,
    get_google_client_secret,
    get_google_redirect_uri,
    is_google_auth_enabled,
)


VALID_GOOGLE_ISSUERS = ("accounts.google.com", "https://accounts.google.com")
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


class GoogleAuthDisabledError(Exception):
    """Lançado quando o login com Google não está configurado no servidor."""
    pass


class InvalidGoogleTokenError(Exception):
    """Lançado quando o ID Token fornecido pelo Google é inválido, expirado ou forjado."""
    pass


@dataclass(frozen=True)
class GoogleTokenPayload:
    sub: str
    email: str | None
    email_verified: bool
    name: str | None


def verify_google_id_token(token: str) -> GoogleTokenPayload:
    """Valida criptograficamente o ID Token do Google Identity Services (GIS).

    Verifica a assinatura contra as chaves públicas (JWKS) do Google, a expiração,
    a audiência (aud) com base no GOOGLE_CLIENT_ID e o emissor oficial (iss).
    """
    if not is_google_auth_enabled():
        raise GoogleAuthDisabledError("Autenticação com Google não está habilitada neste servidor.")

    client_id = get_google_client_id()
    if not client_id:
        raise GoogleAuthDisabledError("GOOGLE_CLIENT_ID não configurado.")

    try:
        request = google_requests.Request()
        claims: dict[str, Any] = id_token.verify_oauth2_token(
            token,
            request,
            audience=client_id,
        )
    except Exception as exc:
        raise InvalidGoogleTokenError(f"Token do Google inválido ou expirado: {exc}") from exc

    issuer = claims.get("iss")
    if issuer not in VALID_GOOGLE_ISSUERS:
        raise InvalidGoogleTokenError(f"Emissor inválido no token Google: {issuer}")

    sub = claims.get("sub")
    if not sub or not isinstance(sub, str) or not sub.strip():
        raise InvalidGoogleTokenError("Claim 'sub' ausente ou inválido no token Google.")

    email = claims.get("email")
    if email and isinstance(email, str):
        email = email.strip().lower()
    else:
        email = None

    email_verified = bool(claims.get("email_verified", False))
    name = claims.get("name")
    if name and isinstance(name, str):
        name = name.strip()
    else:
        name = None

    return GoogleTokenPayload(
        sub=sub.strip(),
        email=email,
        email_verified=email_verified,
        name=name,
    )


def build_google_authorization_url(state: str) -> str:
    """Gera a URL de redirecionamento para autorização do usuário no Google OAuth 2.0."""
    if not is_google_auth_enabled():
        raise GoogleAuthDisabledError("Autenticação com Google não está habilitada neste servidor.")

    client_id = get_google_client_id()
    if not client_id:
        raise GoogleAuthDisabledError("GOOGLE_CLIENT_ID não configurado.")

    redirect_uri = get_google_redirect_uri()
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"


def exchange_google_code_for_token(code: str) -> GoogleTokenPayload:
    """Troca o authorization code retornado pelo Google pelo ID Token e o valida."""
    if not is_google_auth_enabled():
        raise GoogleAuthDisabledError("Autenticação com Google não está habilitada neste servidor.")

    client_id = get_google_client_id()
    client_secret = get_google_client_secret()
    redirect_uri = get_google_redirect_uri()

    if not client_id or not client_secret:
        raise GoogleAuthDisabledError("GOOGLE_CLIENT_ID ou GOOGLE_CLIENT_SECRET não configurado.")

    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    try:
        resp = requests.post(GOOGLE_TOKEN_ENDPOINT, data=payload, timeout=10)
    except Exception as exc:
        raise InvalidGoogleTokenError(f"Erro de comunicação com o Google OAuth: {exc}") from exc

    if resp.status_code != 200:
        raise InvalidGoogleTokenError(f"Falha na troca de código do Google ({resp.status_code}): {resp.text}")

    data = resp.json()
    id_token_str = data.get("id_token")
    if not id_token_str:
        raise InvalidGoogleTokenError("Google não retornou um id_token válido na resposta.")

    return verify_google_id_token(id_token_str)
