"""Problema de validação do LDF: código estável, caminho (RFC 6901) e mensagem."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    """``code`` é ``V1`` (versão), ``S1`` (forma, JSON Schema) ou ``R1``–``R9`` (regras)."""

    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} {self.path or '/'}: {self.message}"
