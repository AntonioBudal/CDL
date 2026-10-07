"""Testes da conversão para o LDF 1.0 e da validação contra o JSON Schema."""

from to_ldf import to_ldf, validation_errors


def _prediction(page):
    return {
        "lines": [
            {"bbox": ln["bbox"], "polygon": ln["polygon"], "score": 0.9} for ln in page["lines"]
        ],
        "blocks": [{"type": b["type"], "bbox": b["bbox"], "score": 0.8} for b in page["blocks"]],
    }


def test_reference_page_converts_to_valid_ldf(tiny_manifest):
    _, _, manifest = tiny_manifest
    page = manifest["pages"][0]
    document, gaps = to_ldf(page, _prediction(page), "reference", 12.4)
    assert validation_errors(document) == []
    blocks = document["structure"]["blocks"]
    assert [b["type"] for b in blocks] == ["heading", "paragraph"]
    assert blocks[0]["line_ids"] == ["line_001"] and blocks[1]["line_ids"] == ["line_002"]
    assert len(document["structure"]["diagrams"]) == 1
    assert len(gaps) == 1 and "sem campo no LDF" in gaps[0]
    assert all(line["text"] == "" for line in document["recognition"]["lines"])
    assert document["pipeline_metadata"]["processing_time_ms"] == 12


def test_document_id_is_stable_and_invalid_documents_are_reported(tiny_manifest):
    _, _, manifest = tiny_manifest
    page = manifest["pages"][1]
    first, _ = to_ldf(page, _prediction(page), "x")
    second, _ = to_ldf(page, _prediction(page), "x")
    assert first["document_id"] == second["document_id"]
    first["structure"]["blocks"][0]["type"] = "title"  # não existe no enum de blocos do LDF 1.0
    assert any("title" in error for error in validation_errors(first))
