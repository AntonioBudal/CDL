"""Fusão de fragmentos, cobertura e classes de erro do EXP-008, com caixas fictícias."""

import pytest
from common import classify_unmatched, ignored, line_f1, oracle_merge
from coverage import page_coverage, summarize
from merge import MergeParams, angle, merge_lines

PARAMS = MergeParams(v_overlap=0.5, max_gap=1.5, max_angle=10.0)


def box(x0, y0, x1, y1, score=1.0):
    return {"bbox": [x0, y0, x1, y1], "score": score}


def test_fragments_of_the_same_line_are_joined():
    lines = [box(100, 100, 300, 150, 0.9), box(330, 102, 500, 152, 0.7), box(100, 300, 500, 350)]
    merged = merge_lines(lines, PARAMS)
    assert [m["bbox"] for m in merged] == [[100, 100, 500, 152], [100, 300, 500, 350]]
    assert merged[0]["fragments"] == 2
    assert merged[0]["score"] == pytest.approx(0.8)
    assert len(merged[0]["polygon"]) == 4


def test_merge_is_transitive():
    lines = [box(0, 0, 100, 40), box(120, 0, 220, 40), box(240, 0, 340, 40)]
    assert [m["bbox"] for m in merge_lines(lines, PARAMS)] == [[0, 0, 340, 40]]


def test_far_apart_fragments_are_kept_separate():
    lines = [box(0, 0, 100, 40), box(400, 0, 500, 40)]
    assert len(merge_lines(lines, PARAMS)) == 2
    assert len(merge_lines(lines, MergeParams(max_gap=10.0))) == 1


def test_lines_one_above_the_other_are_never_joined():
    lines = [box(0, 0, 400, 40), box(0, 45, 400, 85), box(0, 30, 400, 70)]
    assert len(merge_lines(lines[:2], MergeParams(v_overlap=0.1, max_gap=50))) == 2
    assert len(merge_lines([lines[0], lines[2]], MergeParams(v_overlap=0.5, max_gap=50))) == 2
    assert len(merge_lines([lines[0], lines[2]], MergeParams(v_overlap=0.2, max_gap=50))) == 1


def test_different_slopes_are_not_joined():
    flat = {"bbox": [0, 0, 200, 40], "polygon": [[0, 0], [200, 0], [200, 40], [0, 40]]}
    tilted = {"bbox": [210, 0, 400, 110], "polygon": [[210, 80], [380, 0], [400, 30], [230, 110]]}
    assert abs(angle(flat)) < 1 and abs(angle(tilted)) > 20
    assert len(merge_lines([flat, tilted], PARAMS)) == 2
    assert len(merge_lines([flat, tilted], MergeParams(max_angle=45))) == 1


def test_trivial_inputs():
    assert merge_lines([], PARAMS) == []
    assert merge_lines([box(0, 0, 10, 10)], PARAMS) == [box(0, 0, 10, 10)]


PAGE = {
    "id": "p1",
    "width": 1000,
    "height": 1000,
    "lines": [{"bbox": [100, 100, 900, 200]}, {"bbox": [100, 400, 900, 500]}],
    "ignore": [[100, 700, 900, 800]],
}


def test_coverage_does_not_depend_on_how_the_line_is_split():
    whole = page_coverage(PAGE, [[100, 100, 900, 200]])
    pieces = page_coverage(PAGE, [[100, 100, 400, 200], [400, 100, 900, 200]])
    assert whole == pieces
    result = summarize([whole])
    assert result["covered"] == pytest.approx(0.5, abs=0.02)
    assert result["spill"] == pytest.approx(0.0, abs=0.02)


def test_spill_ignores_the_ignore_regions():
    counts = page_coverage(PAGE, [[100, 700, 900, 800], [100, 850, 900, 950]])
    result = summarize([counts])
    assert result["covered"] == 0
    assert result["spill"] == pytest.approx(0.5, abs=0.03)
    assert summarize([]) == {"covered": None, "spill": None, "area_f1": None}


def test_line_f1_applies_the_ignore_rule():
    manifest = {"pages": [PAGE]}
    predictions = {
        "p1": [box(100, 100, 900, 200), box(100, 400, 900, 500), box(100, 700, 900, 800)]
    }
    assert line_f1(manifest, predictions)["f1"] == 1.0
    assert ignored([100, 700, 900, 800], PAGE["ignore"]) is True
    assert line_f1(manifest, {})["recall"] == 0.0


def test_error_classes_and_oracle_merge():
    truths = [[100, 100, 700, 150], [100, 200, 700, 250]]
    halves = [[100, 100, 380, 150], [420, 100, 700, 150]]
    assert classify_unmatched(truths, [*halves, truths[1]]) == {"split": 1}
    assert classify_unmatched(truths, [[100, 100, 700, 250]]) == {"merged": 2}
    assert classify_unmatched(truths, []) == {"missed": 2}
    assert oracle_merge(truths, [*halves, truths[1]]) == truths
