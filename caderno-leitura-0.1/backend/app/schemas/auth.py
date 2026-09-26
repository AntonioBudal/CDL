from __future__ import annotations

from datetime import datetime
import re
from typing import Any

from pydantic import Field, field_validator

from app.schemas.common import InputModel, OutputModel
from app.schemas.user import UserRead

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]+$")


class AuthConfigResponse(OutputModel):
    allow_registration: bool
    owner_setup_required: bool
    google_auth_enabled: bool = False
    google_client_id: str | None = None


class GoogleAuthRequest(InputModel):
    credential: str = Field(
        min_length=1,
        description="ID Token JWT emitido pelo Google Identity Services (GIS)",
    )


class ExternalIdentityRead(OutputModel):
    id: str
    provider: str
    email_at_link: str | None = None
    created_at: datetime


class SetupOwnerRequest(InputModel):
    password: str = Field(min_length=8, description="Senha mestra inicial do proprietário canônico")


class RegisterRequest(InputModel):
    username: str = Field(
        min_length=3,
        max_length=30,
        description="Identificador único alfanumérico",
    )
    display_name: str = Field(min_length=1, max_length=60, description="Nome de exibição do leitor")
    email: str | None = Field(default=None, max_length=255, description="E-mail opcional do leitor")
    password: str = Field(min_length=8, description="Senha de acesso pessoal")

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, v: Any) -> str:
        if isinstance(v, str):
            v = v.strip().lstrip("@").lower()
            if len(v) < 3:
                raise ValueError("O nome de usuário deve conter no mínimo 3 caracteres.")
            if len(v) > 30:
                raise ValueError("O nome de usuário deve conter no máximo 30 caracteres.")
            if not USERNAME_REGEX.match(v):
                raise ValueError(
                    "O nome de usuário deve conter apenas letras sem acento, números, ponto (.) ou hífen (-), sem espaços."
                )
            return v
        return v

    @field_validator("display_name", mode="before")
    @classmethod
    def normalize_display_name(cls, v: Any) -> str:
        if isinstance(v, str):
            v = v.strip()
            if len(v) < 1:
                raise ValueError("O nome de exibição não pode estar em branco.")
            if len(v) > 60:
                raise ValueError("O nome de exibição deve conter no máximo 60 caracteres.")
            return v
        return v

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip().lower()
            return v if v else None
        return v

    @field_validator("password", mode="before")
    @classmethod
    def normalize_password(cls, v: Any) -> str:
        if isinstance(v, str) and len(v) < 8:
            raise ValueError("A senha deve conter no mínimo 8 caracteres.")
        return v


class LoginRequest(InputModel):
    username_or_email: str = Field(min_length=1, description="Nome de usuário ou e-mail cadastrado")
    password: str = Field(min_length=1, description="Senha de acesso")

    @field_validator("username_or_email", mode="before")
    @classmethod
    def normalize_username_or_email(cls, v: Any) -> str:
        if isinstance(v, str):
            v = v.strip()
            if len(v) < 1:
                raise ValueError("Informe o nome de usuário ou e-mail.")
            return v
        return v


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
