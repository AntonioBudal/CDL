from datetime import datetime
from pydantic import BaseModel, Field


class SupportPublicResponse(BaseModel):
    """Informações públicas e sanitizadas sobre meios de contribuição voluntária."""
    pix_enabled: bool
    pix_key: str | None = None
    pix_recipient_name: str | None = None
    pix_qr_code_url: str | None = None
    alternative_enabled: bool
    alternative_label: str | None = None
    alternative_url: str | None = None
    custom_message: str | None = None
    has_any_method_active: bool


class SupportAdminResponse(SupportPublicResponse):
    """Informações administrativas completas com metadados de auditoria e origem."""
    source: str  # "database" | "environment" | "default"
    updated_at: datetime | None = None
    updated_by_user_id: str | None = None
    updated_by_name: str | None = None


class SupportConfigUpdate(BaseModel):
    """Payload de atualização dos parâmetros de apoio pelo administrador."""
    pix_enabled: bool
    pix_key: str | None = Field(default=None, max_length=255)
    pix_recipient_name: str | None = Field(default=None, max_length=255)
    pix_qr_code_url: str | None = None
    alternative_enabled: bool
    alternative_label: str | None = Field(default=None, max_length=100)
    alternative_url: str | None = None
    custom_message: str | None = Field(default=None, max_length=1000)
