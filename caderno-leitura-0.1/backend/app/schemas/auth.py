from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import InputModel, OutputModel
from app.schemas.user import UserRead


class AuthConfigResponse(OutputModel):
    allow_registration: bool
    owner_setup_required: bool


class SetupOwnerRequest(InputModel):
    password: str = Field(min_length=8, description="Senha mestra inicial do proprietário canônico")


class RegisterRequest(InputModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
        description="Identificador único alfanumérico",
    )
    display_name: str = Field(min_length=1, max_length=100, description="Nome de exibição do leitor")
    email: str | None = Field(default=None, max_length=255, description="E-mail opcional do leitor")
    password: str = Field(min_length=8, description="Senha de acesso pessoal")


class LoginRequest(InputModel):
    username_or_email: str = Field(min_length=1, description="Nome de usuário ou e-mail cadastrado")
    password: str = Field(min_length=1, description="Senha de acesso")


class SessionItem(OutputModel):
    id: str
    device_name: str
    ip_address: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_current: bool = False


class AuthSuccessResponse(OutputModel):
    user: UserRead
    session_id: str


class LogoutResponse(OutputModel):
    ok: bool = True


class LogoutAllResponse(OutputModel):
    revoked_count: int
