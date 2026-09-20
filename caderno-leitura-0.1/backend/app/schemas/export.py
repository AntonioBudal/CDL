from enum import Enum
from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    TEXT = "text"


class ExportOptions(BaseModel):
    """Opções de configuração para exportação de anotações e estudos."""

    format: ExportFormat = Field(
        default=ExportFormat.MARKDOWN,
        description="Formato de saída: 'markdown' (.md) ou 'text' (.txt)",
    )
    include_notes: bool = Field(
        default=True,
        description="Incluir anotações pessoais do leitor",
    )
    include_sections: bool = Field(
        default=True,
        description="Incluir seções de análise (resumo, explicação, conceitos, referências)",
    )
    include_source: bool = Field(
        default=False,
        description="Incluir a resposta textual original da importação",
    )
    include_metadata: bool = Field(
        default=True,
        description="Incluir cabeçalho com metadados do livro/estudo",
    )
