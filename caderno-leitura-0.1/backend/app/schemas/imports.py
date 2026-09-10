from pydantic import ConfigDict, Field, field_validator

from app.schemas.common import InputModel, OutputModel


class ImportPreviewRequest(InputModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "source_response": (
            "## Resumo\nIdeia principal do trecho.\n\n"
            "## Explicação\nDesenvolvimento da ideia.\n\n"
            "## Conceitos\n- Conceito central: significado no trecho.\n\n"
            "## Referências\nNenhuma referência externa verificada."
        ),
    }]})

    source_response: str = Field(description="Resposta inteira colada do ChatGPT, sem alterações.")

    @field_validator("source_response")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Cole a resposta do ChatGPT para preparar a prévia.")
        return value


class ImportWarningRead(OutputModel):
    code: str
    message: str
    section: str | None
    line: int | None = Field(description="Linha da resposta original, começando em 1, quando aplicável.")


class ImportPreviewRead(OutputModel):
    source_response: str
    summary: str
    explanation: str
    concepts: str
    references: str
    unassigned_text: str
    warnings: list[ImportWarningRead]
