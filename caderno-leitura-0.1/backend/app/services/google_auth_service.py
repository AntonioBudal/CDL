from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import get_google_client_id, is_google_auth_enabled


VALID_GOOGLE_ISSUERS = ("accounts.google.com", "https://accounts.google.com")


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
