"""O modelo Pydantic é um espelho fiel do JSON Schema normativo (estrutura e veredicto)."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from leitorum_di.contracts.ldf import LDFDocument, load_schema
from leitorum_di.contracts.ldf.schema import check_shape

CONFORMANCE = Path(__file__).resolve().parent / "conformance"
CASES = sorted(CONFORMANCE.glob("*/*.json"))
CONSTRAINTS = (
    "type",
    "enum",
    "const",
    "pattern",
    "minimum",
    "maximum",
    "minItems",
    "maxItems",
    "minLength",
)


def normalize(node: dict[str, Any], root: dict[str, Any]) -> dict[str, Any]:
    """Reduz um schema ao que define o contrato: campos, obrigatoriedade e restrições."""
    if "$ref" in node:
        target = root
        for part in node["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return normalize(target, root)
    out: dict[str, Any] = {key: node[key] for key in CONSTRAINTS if key in node}
    if "enum" in out or "const" in out:
        out.pop("type", None)
    if "enum" in out:
        out["enum"] = sorted(out["enum"])
    if "properties" in node:
        out["properties"] = {k: normalize(v, root) for k, v in node["properties"].items()}
        out["required"] = sorted(node.get("required", []))
        out["additionalProperties"] = node.get("additionalProperties", True)
    if "items" in node:
        out["items"] = normalize(node["items"], root)
    return out


def differences(a: Any, b: Any, path: str = "") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        found = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                found.append(f"{path}/{key}: só em {'modelo' if key in b else 'schema'}")
            else:
                found.extend(differences(a[key], b[key], f"{path}/{key}"))
        return found
    return [] if a == b else [f"{path}: schema={a!r} modelo={b!r}"]


def test_model_structure_matches_the_schema():
    schema = load_schema()
    model = LDFDocument.model_json_schema(by_alias=True)
    assert differences(normalize(schema, schema), normalize(model, model)) == []


def test_every_schema_object_forbids_unknown_fields():
    def walk(node: dict[str, Any]) -> None:
        if "properties" in node:
            assert node["additionalProperties"] is False
            for child in node["properties"].values():
                walk(child)
        if "items" in node:
            walk(node["items"])

    schema = load_schema()
    walk(normalize(schema, schema))


@pytest.mark.parametrize("path", CASES, ids=lambda p: f"{p.parent.name}/{p.stem}")
def test_model_and_schema_give_the_same_verdict_on_shape(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    by_schema = not check_shape(document)
    try:
        LDFDocument.model_validate(document)
        by_model = True
    except ValidationError:
        by_model = False
    assert by_model == by_schema


@pytest.mark.parametrize("path", sorted(CONFORMANCE.glob("valid/*.json")), ids=lambda p: p.stem)
def test_round_trip_through_the_model_is_lossless(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    assert LDFDocument.model_validate(document).to_dict() == document


def test_explicit_null_is_kept_in_operation_value():
    document = json.loads((CONFORMANCE / "valid" / "with-corrections.json").read_text("utf-8"))
    document["human_corrections"][0]["ops"][0]["value"] = None
    assert not check_shape(document)
    assert LDFDocument.model_validate(document).to_dict() == document
