"""Validação completa de um documento LDF 2.0: versão, forma (JSON Schema) e regras R1–R9."""

from __future__ import annotations

import re
from typing import Any

from leitorum_di.contracts.ldf.corrections import CorrectionError, apply_corrections
from leitorum_di.contracts.ldf.issues import Issue
from leitorum_di.contracts.ldf.rules import check_rules
from leitorum_di.contracts.ldf.schema import SUPPORTED_MAJOR, SUPPORTED_MINOR, check_shape

_VERSION = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)$")


class LDFValidationError(ValueError):
    """Documento LDF inválido; ``issues`` traz todos os problemas encontrados."""

    def __init__(self, issues: list[Issue]) -> None:
        super().__init__("; ".join(str(issue) for issue in issues[:5]))
        self.issues = issues


def check_version(document: Any) -> list[Issue]:
    """``V1`` quando o documento declara versão que este leitor não suporta."""
    version = document.get("ldf_version") if isinstance(document, dict) else None
    match = _VERSION.match(version) if isinstance(version, str) else None
    if match is None:
        return []  # ausente ou malformada: o schema acusa
    major, minor = int(match[1]), int(match[2])
    if major != SUPPORTED_MAJOR or minor > SUPPORTED_MINOR:
        supported = f"{SUPPORTED_MAJOR}.{SUPPORTED_MINOR}"
        return [
            Issue("V1", "/ldf_version", f"versão não suportada: {version} (leitor {supported})")
        ]
    return []


def _check_corrections(document: dict[str, Any]) -> list[Issue]:
    if not document["human_corrections"]:
        return []
    try:
        corrected = apply_corrections(document)
    except CorrectionError as error:
        return [Issue("R9", f"/human_corrections/{error.index}", error.reason)]
    after = check_shape(corrected) or check_rules(corrected, stage_rules=False)
    return [
        Issue("R9", issue.path, f"após as correções: {issue.code} {issue.message}")
        for issue in after
    ]


def validate(document: Any) -> list[Issue]:
    """Devolve os problemas do documento; lista vazia significa documento válido.

    A ordem é: versão (``V1``), forma (``S1``) e regras (``R1``–``R9``). Cada passo só roda se o
    anterior não encontrou problema.
    """
    issues = check_version(document) or check_shape(document)
    if issues:
        return issues
    return check_rules(document) + _check_corrections(document)


def ensure_valid(document: Any) -> None:
    """Levanta ``LDFValidationError`` se o documento for inválido."""
    issues = validate(document)
    if issues:
        raise LDFValidationError(issues)
