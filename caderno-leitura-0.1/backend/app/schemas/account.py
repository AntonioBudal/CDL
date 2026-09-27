from __future__ import annotations

from pydantic import BaseModel, Field


class DeactivateAccountRequest(BaseModel):
    password: str | None = Field(default=None, description="Senha atual do leitor (obrigatória caso possua senha local)")


class ReactivateAccountRequest(BaseModel):
    username_or_email: str = Field(..., description="Nome de usuário ou e-mail da conta desativada")
    password: str | None = Field(default=None, description="Senha local para reativação")
    google_credential: str | None = Field(default=None, description="Token Google GIS para reativação de conta vinculada")


class DeleteAccountRequest(BaseModel):
    password: str | None = Field(default=None, description="Senha atual do leitor (obrigatória caso possua senha local)")
    confirmation_text: str = Field(..., description="Digitação exata do username para confirmação inequívoca de exclusão")


class AccountLifecycleResponse(BaseModel):
    ok: bool = True
    message: str
