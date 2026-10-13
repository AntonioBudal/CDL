"""Carga da fonte normativa do LDF 2.0 (JSON Schema) e validação de forma."""

from __future__ import annotations

import json
from functools import cache
from importlib import resources
from typing import Any

import jsonschema

from leitorum_di.contracts.ldf.issues import Issue

SCHEMA_RESOURCE = "schemas/ldf-2.0.schema.json"
SUPPORTED_MAJOR = 2
SUPPORTED_MINOR = 0


@cache
def load_schema() -> dict[str, Any]:
    """Devolve o JSON Schema normativo, lido do pacote instalado."""
    text = resources.files(__package__).joinpath(SCHEMA_RESOURCE).read_text(encoding="utf-8")
    return json.loads(text)


@cache
def _validator() -> jsonschema.Draft202012Validator:
    schema = load_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def pointer(parts) -> str:
    """Monta um JSON Pointer (RFC 6901) a partir dos componentes do caminho."""
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def check_shape(document: Any) -> list[Issue]:
    """Problemas de forma (código ``S1``) segundo o JSON Schema; lista vazia = forma válida."""
    errors = sorted(_validator().iter_errors(document), key=lambda e: [str(p) for p in e.path])
    return [Issue("S1", pointer(error.absolute_path), error.message) for error in errors]
