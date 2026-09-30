from __future__ import annotations

import os
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.support_setting import SupportSetting
from app.models.user import User
from app.schemas.support_setting import (
    SupportAdminResponse,
    SupportConfigUpdate,
    SupportPublicResponse,
)
from app.services.audit_service import log_security_event


def _bool_from_env(key: str, default: bool = False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes", "sim")


def _get_env_fallback() -> dict:
    """Carrega parâmetros das variáveis de ambiente com defaults seguros."""
    pix_enabled = _bool_from_env("SUPPORT_PIX_ENABLED", False)
    pix_key = os.environ.get("SUPPORT_PIX_KEY")
    pix_recipient = os.environ.get("SUPPORT_PIX_RECIPIENT")
    pix_qr = os.environ.get("SUPPORT_PIX_QR_CODE_URL")

    alt_enabled = _bool_from_env("SUPPORT_ALTERNATIVE_ENABLED", False)
    alt_label = os.environ.get("SUPPORT_ALTERNATIVE_LABEL") or "Google Pay / Link Externo"
    alt_url = os.environ.get("SUPPORT_ALTERNATIVE_URL")
    custom_msg = os.environ.get("SUPPORT_CUSTOM_MESSAGE")

    has_any = bool((pix_enabled and pix_key) or (alt_enabled and alt_url))

    has_env = bool(pix_key or alt_url or "SUPPORT_PIX_ENABLED" in os.environ or "SUPPORT_ALTERNATIVE_ENABLED" in os.environ)

    return {
        "pix_enabled": pix_enabled,
        "pix_key": pix_key,
        "pix_recipient_name": pix_recipient,
        "pix_qr_code_url": pix_qr,
        "alternative_enabled": alt_enabled,
        "alternative_label": alt_label,
        "alternative_url": alt_url,
        "custom_message": custom_msg,
        "has_any_method_active": has_any,
        "has_env": has_env,
    }


def get_public_support_info(session: Session) -> SupportPublicResponse:
    """Retorna dados de apoio públicos e sanitizados para /apoie."""
    setting = session.execute(select(SupportSetting).where(SupportSetting.id == 1)).scalar_one_or_none()

    if setting is not None:
        has_any = bool(
            (setting.pix_enabled and setting.pix_key)
            or (setting.alternative_enabled and setting.alternative_url)
        )
        return SupportPublicResponse(
            pix_enabled=setting.pix_enabled,
            pix_key=setting.pix_key if setting.pix_enabled else None,
            pix_recipient_name=setting.pix_recipient_name if setting.pix_enabled else None,
            pix_qr_code_url=setting.pix_qr_code_url if setting.pix_enabled else None,
            alternative_enabled=setting.alternative_enabled,
            alternative_label=setting.alternative_label if setting.alternative_enabled else None,
            alternative_url=setting.alternative_url if setting.alternative_enabled else None,
            custom_message=setting.custom_message,
            has_any_method_active=has_any,
        )

    # Fallback para variáveis de ambiente
    env_data = _get_env_fallback()
    return SupportPublicResponse(
        pix_enabled=env_data["pix_enabled"],
        pix_key=env_data["pix_key"] if env_data["pix_enabled"] else None,
        pix_recipient_name=env_data["pix_recipient_name"] if env_data["pix_enabled"] else None,
        pix_qr_code_url=env_data["pix_qr_code_url"] if env_data["pix_enabled"] else None,
        alternative_enabled=env_data["alternative_enabled"],
        alternative_label=env_data["alternative_label"] if env_data["alternative_enabled"] else None,
        alternative_url=env_data["alternative_url"] if env_data["alternative_enabled"] else None,
        custom_message=env_data["custom_message"],
        has_any_method_active=env_data["has_any_method_active"],
    )


def get_admin_support_config(session: Session) -> SupportAdminResponse:
    """Retorna parâmetros completos com metadados para o painel administrativo."""
    setting = session.execute(select(SupportSetting).where(SupportSetting.id == 1)).scalar_one_or_none()

    if setting is not None:
        has_any = bool(
            (setting.pix_enabled and setting.pix_key)
            or (setting.alternative_enabled and setting.alternative_url)
        )
        updater_name = None
        if setting.updated_by_user_id:
            updater = session.execute(
                select(User).where(User.id == setting.updated_by_user_id)
            ).scalar_one_or_none()
            if updater:
                updater_name = updater.display_name or updater.username

        return SupportAdminResponse(
            pix_enabled=setting.pix_enabled,
            pix_key=setting.pix_key,
            pix_recipient_name=setting.pix_recipient_name,
            pix_qr_code_url=setting.pix_qr_code_url,
            alternative_enabled=setting.alternative_enabled,
            alternative_label=setting.alternative_label,
            alternative_url=setting.alternative_url,
            custom_message=setting.custom_message,
            has_any_method_active=has_any,
            source="database",
            updated_at=setting.updated_at,
            updated_by_user_id=setting.updated_by_user_id,
            updated_by_name=updater_name,
        )

    # Fallback para ambiente ou default
    env_data = _get_env_fallback()
    source = "environment" if env_data["has_env"] else "default"

    return SupportAdminResponse(
        pix_enabled=env_data["pix_enabled"],
        pix_key=env_data["pix_key"],
        pix_recipient_name=env_data["pix_recipient_name"],
        pix_qr_code_url=env_data["pix_qr_code_url"],
        alternative_enabled=env_data["alternative_enabled"],
        alternative_label=env_data["alternative_label"],
        alternative_url=env_data["alternative_url"],
        custom_message=env_data["custom_message"],
        has_any_method_active=env_data["has_any_method_active"],
        source=source,
        updated_at=None,
        updated_by_user_id=None,
        updated_by_name=None,
    )


def update_support_config(
    session: Session,
    payload: SupportConfigUpdate,
    current_admin: User,
    request: Request | None = None,
) -> SupportAdminResponse:
    """Atualiza as configurações de apoio na tabela singleton e registra auditoria."""
    setting = session.execute(select(SupportSetting).where(SupportSetting.id == 1)).scalar_one_or_none()

    if setting is None:
        setting = SupportSetting(id=1)
        session.add(setting)

    setting.pix_enabled = payload.pix_enabled
    setting.pix_key = payload.pix_key.strip() if payload.pix_key else None
    setting.pix_recipient_name = payload.pix_recipient_name.strip() if payload.pix_recipient_name else None
    setting.pix_qr_code_url = payload.pix_qr_code_url.strip() if payload.pix_qr_code_url else None
    setting.alternative_enabled = payload.alternative_enabled
    setting.alternative_label = payload.alternative_label.strip() if payload.alternative_label else None
    setting.alternative_url = payload.alternative_url.strip() if payload.alternative_url else None
    setting.custom_message = payload.custom_message.strip() if payload.custom_message else None
    setting.updated_at = utc_now()
    setting.updated_by_user_id = current_admin.id

    session.flush()

    # Registro de auditoria
    log_security_event(
        session=session,
        event_type="admin.support_settings_updated",
        request=request,
        user_id=current_admin.id,
        actor_username=current_admin.username,
        details={
            "pix_enabled": setting.pix_enabled,
            "has_pix_key": bool(setting.pix_key),
            "alternative_enabled": setting.alternative_enabled,
            "has_alternative_url": bool(setting.alternative_url),
        },
    )

    session.commit()
    session.refresh(setting)

    return get_admin_support_config(session)
