from typing import Literal

from pydantic import Field

from app.schemas.common import OutputModel


class DigitizeStatusRead(OutputModel):
    available: bool
    reason: Literal["not_installed", "integrity_failed"] | None = Field(
        description="Motivo da indisponibilidade; nunca contém caminhos."
    )


class DigitizeLineRead(OutputModel):
    index: int = Field(description="Posição da linha na ordem de leitura, começando em 0.")
    text: str
    confidence: float = Field(ge=0, le=1)
    low_confidence: bool


class DigitizeWarningRead(OutputModel):
    code: Literal["draft", "no_text", "many_uncertain"]
    message: str


class DigitizeEngineRead(OutputModel):
    name: str
    version: str
    reader: str
    license_status: str


class DigitizePreviewRead(OutputModel):
    text: str = Field(description="Leitura automática, linhas unidas por quebra de linha; vira source_response.")
    lines: list[DigitizeLineRead]
    low_confidence_count: int
    warnings: list[DigitizeWarningRead]
    engine: DigitizeEngineRead
    elapsed_ms: int
