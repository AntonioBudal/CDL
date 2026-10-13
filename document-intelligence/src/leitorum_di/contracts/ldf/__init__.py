"""Leitorum Document Format (LDF) 2.0 — contrato entre o Document Intelligence e o Leitorum.

A fonte normativa é o JSON Schema em ``schemas/ldf-2.0.schema.json``; a descrição em prosa e as
regras R1–R9 estão em ``docs/ldf.md``.
"""

from leitorum_di.contracts.ldf.build import (
    LDF_VERSION,
    build_document,
    component,
    rectification_from_corners,
)
from leitorum_di.contracts.ldf.corrections import (
    CorrectionError,
    apply_corrections,
    to_json_patch,
)
from leitorum_di.contracts.ldf.issues import Issue
from leitorum_di.contracts.ldf.models import LDFDocument
from leitorum_di.contracts.ldf.schema import load_schema
from leitorum_di.contracts.ldf.validate import LDFValidationError, ensure_valid, validate

__all__ = [
    "LDF_VERSION",
    "CorrectionError",
    "Issue",
    "LDFDocument",
    "LDFValidationError",
    "apply_corrections",
    "build_document",
    "component",
    "ensure_valid",
    "load_schema",
    "rectification_from_corners",
    "to_json_patch",
    "validate",
]
