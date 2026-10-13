"""Métricas e saída em LDF 2.0 do EXP-007, com layout fictício."""

import json

from orderers import OrderParams
from postprocess import BlockFilter
from run import as_paragraphs, block_metrics, ldf_items, line_metrics, order_metrics, subset
from to_ldf2 import convert_all, layout_component, order_component, page_document

from leitorum_di.contracts.ldf import validate

FILTER = BlockFilter(min_score=0.4, nms_iou=0.7, containment=0.6)
SHA = "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a"


def page(page_id="p1"):
    lines = [
        {"id": "l1", "block_id": "b1", "bbox": [100, 100, 700, 150]},
        {"id": "l2", "block_id": "b2", "bbox": [100, 300, 700, 350]},
    ]
    for line in lines:
        x0, y0, x1, y1 = line["bbox"]
        line["polygon"] = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    return {
        "id": page_id,
        "image": f"dataset/processed/ficticio/{page_id}.png",
        "sha256": SHA,
        "width": 800,
        "height": 1000,
        "level": "x3",
        "family": "essay",
        "lines": lines,
        "blocks": [
            {"id": "b1", "type": "paragraph", "bbox": [90, 90, 710, 160], "line_ids": ["l1"]},
            {"id": "b2", "type": "paragraph", "bbox": [90, 290, 710, 360], "line_ids": ["l2"]},
        ],
        "reading_order": ["b1", "b2"],
        "ignore": [],
    }


def detected_for(manifest, blocks, lines=None):
    return {
        "pages": {
            p["id"]: {
                "blocks": blocks,
                "lines": {
                    "original": lines
                    if lines is not None
                    else [{"bbox": ln["bbox"], "polygon": ln["polygon"]} for ln in p["lines"]]
                },
            }
            for p in manifest["pages"]
        }
    }


def test_block_class_is_ignored_and_the_operating_point_is_applied():
    manifest = {"pages": [page()]}
    blocks = [
        {"type": "title", "bbox": [92, 92, 708, 158], "score": 0.9},  # classe errada: conta
        {"type": "paragraph", "bbox": [90, 290, 710, 360], "score": 0.8},
        {"type": "paragraph", "bbox": [95, 295, 705, 355], "score": 0.5},  # duplicata: suprimida
        {"type": "graphic_box", "bbox": [300, 600, 500, 700], "score": 0.3},  # abaixo do limiar
    ]
    result = block_metrics(manifest, detected_for(manifest, blocks), FILTER)
    assert result["at_operating_point"]["0.5"]["f1"] == 1.0
    assert result["predicted_blocks"] == 2
    assert result["raw_predicted_blocks"] == 4
    assert result["truth_blocks"] == 2
    assert 0 < result["class_agnostic_ap50"] <= 1.0
    assert {b["type"] for b in as_paragraphs(blocks)} == {"paragraph"}


def test_line_metrics_and_subset():
    manifest = {"pages": [page("p1"), page("p2")]}
    detected = detected_for(manifest, [])
    detected["pages"]["p2"]["lines"]["original"] = []
    result = line_metrics(manifest, detected, "original")
    assert result["bbox"]["0.5"]["recall"] == 0.5
    assert result["truth_lines"] == 4 and result["predicted_lines"] == 2
    only_first = line_metrics(subset(manifest, {"p1"}), detected, "original")
    assert only_first["bbox"]["0.5"]["f1"] == 1.0


def test_order_with_true_and_detected_paragraphs():
    manifest = {"pages": [page()]}
    blocks = [
        {"type": "paragraph", "bbox": [90, 290, 710, 360], "score": 0.9},
        {"type": "text", "bbox": [90, 90, 710, 160], "score": 0.8},
    ]
    orderers = {"naive": OrderParams(method="naive", deskew=False, tie=0.0)}
    result = order_metrics(manifest, detected_for(manifest, blocks), FILTER, orderers)
    assert result["naive"]["true_layout"]["blocks_accuracy"] == 1.0
    assert result["naive"]["detected_layout"]["blocks_accuracy"] == 1.0
    assert result["pages_with_more_than_one_block"] == 1


REGISTRY = {
    "candidates": [
        {
            "id": "docufcn-norhand-line",
            "license_status": "VERIFIED",
            "weights": {"revision": "a" * 40},
        },
        {"id": "heron", "license_status": "VERIFIED", "weights": {"revision": "b" * 40}},
    ]
}


def test_pages_become_valid_ldf_2_documents():
    manifest = {"pages": [page()]}
    blocks = [
        {"type": "paragraph", "bbox": [90, 90, 710, 160], "score": 0.9},
        {"type": "graphic_box", "bbox": [200, 500, 600, 800], "score": 0.7},
    ]
    detected = detected_for(manifest, blocks)
    detected["pages"]["p1"]["rectification"] = {
        "found": True,
        "quad": [[10, 10], [790, 20], [780, 990], [20, 980]],
        "size": [770, 970],
    }
    items = ldf_items(manifest, detected, FILTER, OrderParams(method="naive"), "original")
    layout, orderer = layout_component(REGISTRY), order_component("naive")
    document = page_document(layout=layout, orderer=orderer, **items[0])
    assert validate(document) == []
    assert [r["type"] for r in document["structure"]["regions"]] == ["paragraph", "graphic"]
    assert len(document["structure"]["reading_order"]) == 2
    assert document["coordinate_space"]["rectification"]["output_size"] == [770, 970]
    stages = document["pipeline"]["stages"]
    assert stages["layout"]["component"]["revision"] == "aaaaaaaa+bbbbbbbb"
    assert stages["recognition"]["status"] == "not_run"
    assert "text" not in json.dumps(document["recognition"])
    summary = convert_all(items, layout, orderer)
    assert summary["documents"] == summary["valid"] == 1 and summary["not_representable"] == 0


def test_degenerate_detection_is_counted_not_hidden():
    manifest = {"pages": [page()]}
    lines = [{"bbox": [100, 100, 100, 150], "polygon": None}]
    items = ldf_items(
        manifest, detected_for(manifest, [], lines), FILTER, OrderParams(), "original"
    )
    summary = convert_all(items, layout_component(REGISTRY), order_component("anchored"))
    assert summary == {
        "documents": 1,
        "valid": 0,
        "not_representable": 1,
        "regions": 0,
        "lines": 0,
        "reasons": {"R5": 1},
    }
