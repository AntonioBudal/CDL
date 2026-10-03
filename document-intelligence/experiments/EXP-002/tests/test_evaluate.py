"""Testes do avaliador de layout: IoU de polígono, regiões ignorar, AP de blocos, vereditos."""

import pytest
from evaluate import evaluate_pages, latency_stats, polygon_iou, verdicts


def test_polygon_iou_known_values():
    square = [[0, 0], [10, 0], [10, 10], [0, 10]]
    shifted = [[5, 0], [15, 0], [15, 10], [5, 10]]
    assert polygon_iou(square, square) == pytest.approx(1.0)
    # Rasterização inclusiva: 11×11 px cada, interseção 6×11 → 66 / (121 + 121 - 66).
    assert polygon_iou(square, shifted) == pytest.approx(66 / 176)
    assert polygon_iou(square, [[50, 50], [60, 50], [60, 60]]) == 0.0
    assert polygon_iou(square, [[0, 0], [1, 1]]) == 0.0


def _truth_as_prediction(page, dx=0, blocks=True):
    lines = [
        {"bbox": [b[0] + dx, b[1], b[2] + dx, b[3]], "polygon": None, "score": 1.0}
        for b in (ln["bbox"] for ln in page["lines"])
    ]
    result = {"lines": lines, "blocks": []}
    if blocks:
        result["blocks"] = [
            {"type": b["type"], "bbox": b["bbox"], "score": 1.0} for b in page["blocks"]
        ]
    return result


def test_perfect_predictions(tiny_manifest):
    _, _, manifest = tiny_manifest
    predictions = {p["id"]: _truth_as_prediction(p) for p in manifest["pages"]}
    result = evaluate_pages(manifest, predictions)
    assert result["lines"]["bbox"]["0.5"]["f1"] == 1.0
    assert result["lines"]["polygon"]["0.75"]["f1"] == 1.0
    assert result["blocks"]["map50"] == pytest.approx(1.0)
    assert result["blocks"]["ap50"]["margin_note"] is None  # nenhuma verdade desse tipo
    assert set(result["lines_by_level"]) == {"clean", "light", "strong"}


def test_shift_gives_expected_iou_and_threshold_behaviour(tiny_manifest):
    _, _, manifest = tiny_manifest
    # Caixas de 200 px de largura deslocadas 40 px: IoU = 160 / 240 = 2/3.
    predictions = {p["id"]: _truth_as_prediction(p, dx=40, blocks=False) for p in manifest["pages"]}
    result = evaluate_pages(manifest, predictions)
    assert result["lines"]["bbox"]["0.5"]["f1"] == 1.0
    assert result["lines"]["bbox"]["0.5"]["mean_iou"] == pytest.approx(2 / 3)
    assert result["lines"]["bbox"]["0.75"]["f1"] == 0.0
    assert result["blocks"] is None


def test_predictions_inside_ignore_region_are_discarded(tiny_manifest):
    _, _, manifest = tiny_manifest
    predictions = {}
    for page in manifest["pages"]:
        result = _truth_as_prediction(page, blocks=False)
        result["lines"].append({"bbox": [420, 420, 580, 460], "polygon": None, "score": 1.0})
        predictions[page["id"]] = result
    lines = evaluate_pages(manifest, predictions)["lines"]["bbox"]["0.5"]
    assert lines["fp"] == 0 and lines["f1"] == 1.0


def test_missing_pages_count_as_empty(tiny_manifest):
    _, _, manifest = tiny_manifest
    result = evaluate_pages(manifest, {})
    assert len(result["missing"]) == 12
    assert result["lines"]["bbox"]["0.5"]["recall"] == 0.0


def test_latency_and_verdicts():
    assert latency_stats([])["median_ms"] is None
    stats = latency_stats([float(v) for v in range(1, 21)])
    assert stats["median_ms"] == 10.5 and stats["p95_ms"] == 19.0
    metrics = {
        "lines_by_level": {"clean": {"f1": 0.95}, "light": {"f1": 0.85}, "strong": {"f1": 0.7}},
        "blocks": {"map50": 0.75},
    }
    result = verdicts(metrics, {"median_ms": 1500.0}, 10**9)
    assert result == {
        "h1_lines_clean": True,
        "h1_lines_degraded": False,
        "h2_blocks": True,
        "h3_cost": True,
    }
    assert verdicts({"lines_by_level": {}, "blocks": None}, {"median_ms": None}, None) == {
        "h1_lines_clean": None,
        "h1_lines_degraded": None,
        "h2_blocks": None,
        "h3_cost": None,
    }
