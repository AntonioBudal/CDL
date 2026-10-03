from pydantic import BaseModel, Field


class SecurityErrorResponse(BaseModel):
    """Contrato padronizado de resposta de erro HTTP 500 sem vazamento de detalhes internos."""

    detail: str = Field(
        default="Ocorreu um erro interno no servidor.",
        description="Mensagem de erro amigável ao usuário sem dados confidenciais.",
    )
    error_id: str | None = Field(
        default=None,
        description="Identificador único anônimo (UUID) para correlação no log do servidor.",
    )
