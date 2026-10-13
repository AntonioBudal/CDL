"""Fonte normativa do LDF 2.0 e casos de conformidade (forma e regras R1–R9)."""

import json
import subprocess
from importlib import resources
from pathlib import Path

import jsonschema
import pytest

from leitorum_di.contracts.ldf import load_schema, validate
from tests.ldf import make_conformance

ROOT = Path(__file__).resolve().parents[2]
CONFORMANCE = Path(__file__).resolve().parent / "conformance"
INDEX = json.loads((CONFORMANCE / "index.json").read_text(encoding="utf-8"))


def load(*parts: str) -> dict:
    return json.loads(CONFORMANCE.joinpath(*parts).read_text(encoding="utf-8"))


def test_schema_is_a_valid_draft_2020_12_schema():
    schema = load_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["$id"].endswith("ldf-2.0.schema.json")


def test_schema_is_packaged_with_the_code():
    resource = resources.files("leitorum_di.contracts.ldf").joinpath("schemas/ldf-2.0.schema.json")
    assert resource.is_file()


def test_there_is_a_single_copy_of_the_normative_schema():
    try:
        listed = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "."],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git indisponível")
    copies = [path for path in listed if path.endswith("ldf-2.0.schema.json")]
    assert copies == ["src/leitorum_di/contracts/ldf/schemas/ldf-2.0.schema.json"]


def test_conformance_is_current():
    """Os arquivos versionados são exatamente os que ``make_conformance.py`` gera."""
    expected = make_conformance.files()
    for path, content in expected.items():
        assert path.is_file(), f"falta gerar {path.name}"
        assert json.loads(path.read_text(encoding="utf-8")) == content, path.name
    on_disk = set(CONFORMANCE.rglob("*.json"))
    assert on_disk == {p for p in expected if CONFORMANCE in p.parents}


@pytest.mark.parametrize("name", INDEX["valid"])
def test_valid_cases_are_accepted(name):
    assert [str(issue) for issue in validate(load("valid", name))] == []


@pytest.mark.parametrize(("name", "code"), sorted(INDEX["invalid"].items()))
def test_invalid_cases_are_rejected_with_the_declared_code(name, code):
    issues = validate(load("invalid", name))
    assert issues, "documento inválido foi aceito"
    assert {issue.code for issue in issues} == {code}, [str(issue) for issue in issues]
    assert all(issue.message for issue in issues)
    assert all(issue.path == "" or issue.path.startswith("/") for issue in issues)


def test_every_rule_has_at_least_two_invalid_cases():
    codes = list(INDEX["invalid"].values())
    for code in ["V1", "S1", *(f"R{n}" for n in range(1, 10))]:
        assert codes.count(code) >= 2, code


@pytest.mark.parametrize("name", sorted(make_conformance.EXAMPLE_FILES))
def test_published_examples_are_valid(name):
    document = json.loads((ROOT / "docs" / "ldf-examples" / name).read_text(encoding="utf-8"))
    assert validate(document) == []


def test_issue_points_to_the_offending_element():
    issues = validate(load("invalid", "r2-missing-line.json"))
    assert issues[0].path == "/structure/regions/0/line_ids/0"
    assert "line_099" in issues[0].message


def test_non_object_document_is_rejected():
    assert {issue.code for issue in validate([])} == {"S1"}
