"""Classificação dos erros de linha, com caixas fictícias."""

from analyze import classify_unmatched

A = [100, 100, 700, 150]
B = [100, 200, 700, 250]


def test_matched_lines_are_not_errors():
    assert classify_unmatched([A, B], [A, B]) == {}


def test_missed_line():
    assert classify_unmatched([A, B], [A]) == {"missed": 1}


def test_two_lines_merged_into_one_detection():
    assert classify_unmatched([A, B], [[100, 100, 700, 250]]) == {"merged": 2}


def test_line_split_in_two_detections():
    halves = [[100, 100, 380, 150], [420, 100, 700, 150]]
    assert classify_unmatched([A], halves) == {"split": 1}


def test_misaligned_detection():
    assert classify_unmatched([A], [[100, 100, 330, 150]]) == {"misaligned": 1}
    assert classify_unmatched([A], [[100, 60, 700, 190]]) == {"misaligned": 1}


def test_page_without_detections():
    assert classify_unmatched([A, B], []) == {"missed": 2}
    assert classify_unmatched([], [A]) == {}


def test_fragments_inside_the_same_line_are_merged():
    from analyze import merge_fragments

    halves = [[100, 100, 380, 150], [420, 100, 700, 150]]
    stray = [100, 600, 300, 650]
    assert merge_fragments([A, B], [*halves, B, stray]) == [A, B, stray]
    assert merge_fragments([], [stray]) == [stray]
