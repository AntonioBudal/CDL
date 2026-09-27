from __future__ import annotations

import json
from typing import Any
from fastapi import Request
from sqlalchemy.orm import Session

from app.core.rate_limiter import get_client_ip
from app.models.audit_log import AuditLog

# Termos sensíveis que devem ser censurados proativamente (OWASP)
REDACTED_KEYS = {
    "password",
    "password_hash",
    "password_confirm",
    "new_password",
    "current_password",
    "token",
    "credential",
    "secret",
    "jwt",
    "code",
    "access_token",
    "refresh_token",
    "id_token",
    "google_credential",
    "authorization",
    "cookie",
    "api_key",
}


def sanitize_details(data: Any) -> Any:
    """
    Higieniza recursivamente dicionários e listas, mascarando segredos
    e credenciais para evitar vazamento em trilhas de auditoria.
    """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            key_lower = str(k).lower()
            if any(term in key_lower for term in REDACTED_KEYS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_details(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_details(item) for item in data]
    return data


def log_event(
    session: Session,
    event_type: str,
    user_id: str | None = None,
    actor_username: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: Any = None,
) -> AuditLog:
    """
    Registra um evento de segurança imutável na tabela audit_logs.
    Garante sanitização total dos dados fornecidos em details.
    """
    details_str: str | None = None
    if details is not None:
        if isinstance(details, (dict, list)):
            clean_details = sanitize_details(details)
            details_str = json.dumps(clean_details, ensure_ascii=False)
        elif isinstance(details, str):
            details_str = details
        else:
            details_str = str(details)

    log_entry = AuditLog(
        event_type=event_type,
        user_id=user_id,
        actor_username=actor_username,
        ip_address=ip_address,
        user_agent=user_agent[:512] if user_agent else None,
        details=details_str,
    )
    session.add(log_entry)
    session.flush()
    return log_entry


def log_security_event(
    session: Session,
    event_type: str,
    request: Request | None = None,
    user_id: str | None = None,
    actor_username: str | None = None,
    details: Any = None,
) -> AuditLog:
    """Helper conveniente para registrar auditoria a partir de uma Request HTTP do FastAPI."""
    ip_address = get_client_ip(request) if request else None
    user_agent = request.headers.get("user-agent") if request else None

    return log_event(
        session=session,
        event_type=event_type,
        user_id=user_id,
        actor_username=actor_username,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )
