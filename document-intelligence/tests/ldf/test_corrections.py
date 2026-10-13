"""Correções humanas: alvo por identificador, saída original preservada, JSON Patch equivalente."""

import copy

import pytest

from leitorum_di.contracts.ldf import CorrectionError, apply_corrections, to_json_patch, validate
from leitorum_di.contracts.ldf.corrections import apply_operation
from tests.ldf.make_conformance import correction, full, with_corrections


def text_of(document, line_id):
    return next(line["text"] for line in document["recognition"]["lines"] if line["id"] == line_id)


def fix_text(ident, line_id, value):
    return correction(
        ident,
        {"collection": "recognition.lines", "id": line_id},
        [{"op": "replace", "path": "/text", "value": value}],
    )


def remove_line(ident, line_id, region_id, remaining):
    """Remover uma linha exige tirá-la também da região que a contém."""
    return [
        correction(
            f"{ident}_a",
            {"collection": "structure.regions", "id": region_id},
            [{"op": "replace", "path": "/line_ids", "value": remaining}],
        ),
        correction(
            f"{ident}_b",
            {"collection": "recognition.lines", "id": line_id},
            [{"op": "remove", "path": ""}],
        ),
    ]


def test_original_output_is_left_untouched():
    document = with_corrections()
    before = copy.deepcopy(document)
    corrected = apply_corrections(document)
    assert document == before
    assert corrected["human_corrections"] == []
    assert text_of(corrected, "line_003") == "segunda linha, corrigida"
    assert text_of(document, "line_003") == "segunda linha do mesmo parágrafo"


def test_correction_survives_removal_of_an_earlier_line():
    """História 4: a posição no vetor muda, o alvo continua o mesmo."""
    document = full()
    document["human_corrections"] = [
        fix_text("c1", "line_003", "terceira linha corrigida"),
        *remove_line("c2", "line_001", "region_001", []),
    ]
    assert validate(document) == []
    corrected = apply_corrections(document)
    assert [line["id"] for line in corrected["recognition"]["lines"]] == [
        "line_002",
        "line_003",
        "line_004",
    ]
    assert text_of(corrected, "line_003") == "terceira linha corrigida"


def test_order_of_corrections_does_not_change_the_target():
    first = full()
    first["human_corrections"] = [
        *remove_line("c2", "line_001", "region_001", []),
        fix_text("c1", "line_003", "terceira linha corrigida"),
    ]
    second = full()
    second["human_corrections"] = [
        fix_text("c1", "line_003", "terceira linha corrigida"),
        *remove_line("c2", "line_001", "region_001", []),
    ]
    assert apply_corrections(first) == apply_corrections(second)


def test_corrections_are_applied_in_list_order():
    document = full()
    document["human_corrections"] = [
        fix_text("c1", "line_001", "primeira versão"),
        fix_text("c2", "line_001", "segunda versão"),
    ]
    assert text_of(apply_corrections(document), "line_001") == "segunda versão"


def test_json_patch_is_equivalent_and_uses_absolute_paths():
    document = with_corrections()
    patch = to_json_patch(document)
    assert patch[0] == {
        "op": "replace",
        "path": "/recognition/lines/2/text",
        "value": "segunda linha, corrigida",
    }
    assert {"op": "remove", "path": "/recognition/lines/3"} in patch
    replayed = copy.deepcopy(document)
    replayed["human_corrections"] = []
    for operation in patch:
        apply_operation(replayed, operation)
    assert replayed == apply_corrections(document)


def test_authorship_stays_in_the_original_document():
    document = with_corrections()
    first = document["human_corrections"][0]
    assert first["author"] == "leitor-ficticio"
    assert first["timestamp"] == "2026-10-12T21:00:00Z"
    assert first["reason"] == "palavra lida errado"


def test_reader_can_type_text_for_a_page_without_recognition():
    """A visão corrigida não está sujeita a R7: o texto veio do leitor, não do pipeline."""
    from tests.ldf.make_conformance import layout_only

    document = layout_only()
    document["human_corrections"] = [
        correction(
            "c1",
            {"collection": "recognition.lines", "id": "line_001"},
            [{"op": "add", "path": "/text", "value": "digitado pelo leitor"}],
        )
    ]
    assert validate(document) == []
    assert text_of(apply_corrections(document), "line_001") == "digitado pelo leitor"


def test_missing_target_reports_the_correction_index():
    document = full()
    document["human_corrections"] = [
        fix_text("c1", "line_001", "ok"),
        fix_text("c2", "line_099", "sem alvo"),
    ]
    with pytest.raises(CorrectionError) as error:
        apply_corrections(document)
    assert error.value.index == 1
    assert "line_099" in error.value.reason
    assert [issue.path for issue in validate(document)] == ["/human_corrections/1"]


def test_target_removed_inside_the_same_correction_is_not_reused():
    document = full()
    document["human_corrections"] = [
        correction(
            "c1",
            {"collection": "semantics.entities", "id": "entity_001"},
            [{"op": "remove", "path": ""}, {"op": "replace", "path": "/type", "value": "x"}],
        )
    ]
    with pytest.raises(CorrectionError):
        apply_corrections(document)


@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        ({"op": "add", "path": "/b/1", "value": 9}, {"a": 1, "b": [1, 9, 2]}),
        ({"op": "add", "path": "/b/-", "value": 9}, {"a": 1, "b": [1, 2, 9]}),
        ({"op": "remove", "path": "/b/0"}, {"a": 1, "b": [2]}),
        ({"op": "replace", "path": "/a", "value": None}, {"a": None, "b": [1, 2]}),
        ({"op": "move", "from": "/a", "path": "/c"}, {"b": [1, 2], "c": 1}),
        ({"op": "copy", "from": "/b/0", "path": "/c"}, {"a": 1, "b": [1, 2], "c": 1}),
        ({"op": "test", "path": "/b", "value": [1, 2]}, {"a": 1, "b": [1, 2]}),
    ],
)
def test_the_six_rfc_6902_operations(operation, expected):
    document = {"a": 1, "b": [1, 2]}
    apply_operation(document, operation)
    assert document == expected


@pytest.mark.parametrize(
    "operation",
    [
        {"op": "remove", "path": "/zzz"},
        {"op": "replace", "path": "/zzz", "value": 1},
        {"op": "add", "path": "/b/5", "value": 1},
        {"op": "add", "path": "/b/01", "value": 1},
        {"op": "test", "path": "/a", "value": 2},
        {"op": "add", "path": "/a"},
        {"op": "move", "path": "/c"},
        {"op": "replace", "path": "", "value": {}},
        {"op": "add", "path": "sem-barra", "value": 1},
    ],
)
def test_invalid_operations_are_refused(operation):
    with pytest.raises((LookupError, ValueError)):
        apply_operation({"a": 1, "b": [1, 2]}, operation)


def test_escaped_pointer_tokens():
    document = {"a/b": {"c~d": 1}}
    apply_operation(document, {"op": "replace", "path": "/a~1b/c~0d", "value": 2})
    assert document == {"a/b": {"c~d": 2}}
