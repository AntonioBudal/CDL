"""EXP-027: alinhamento e quebra do erro, só com frases fictícias."""

from __future__ import annotations

import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1] / "harness"
if str(HARNESS) not in sys.path:
    sys.path.append(str(HARNESS))

import align  # noqa: E402
import textnorm  # noqa: E402

REF = [
    "Capítulo 1: a leitura atenta",
    "A fórmula $x^2 + y^2 = r^2$ descreve o círculo",
    "[figura]",
    "Notas sobre o método [?] de estudo",
    "Última linha da página de teste",
]


def test_parse_reference_marks():
    lines = textnorm.parse_reference("\n".join(REF))
    assert len(lines) == 5
    assert lines[2].figure and lines[2].text == ""
    formula = lines[1]
    assert "$" not in formula.text
    assert formula.formula_chars == len("x^2 + y^2 = r^2")
    assert formula.text == "A fórmula x^2 + y^2 = r^2 descreve o círculo"
    assert lines[3].illegible and "[?]" not in lines[3].text
    assert lines[3].text == "Notas sobre o método de estudo"


def test_levenshtein_and_edit_ops():
    assert align.levenshtein("casa", "cama") == 1
    assert align.levenshtein("", "abc") == 3
    ops = [op for op, _, _ in align.edit_ops("abc", "abXcd")]
    assert ops.count("ins") == 2 and ops.count("eq") == 3


def test_perfect_page_has_no_error():
    lines = textnorm.text_lines(textnorm.parse_reference("\n".join(REF)))
    score = align.score_page(lines, [line.text for line in lines])
    assert score.distance_total == 0
    assert score.matching.one_to_one == 4
    assert not score.matching.missing and not score.matching.spurious
    assert score.recognition_detail["errors_formula"] == 0


def test_recognition_error_inside_formula_is_attributed():
    lines = textnorm.text_lines(textnorm.parse_reference("\n".join(REF)))
    hyps = [line.text for line in lines]
    hyps[1] = "A fórmula x2 + y2 = r2 descreve o círculo"  # três "^" perdidos
    score = align.score_page(lines, hyps)
    assert score.recognition == 3
    assert score.recognition_detail["errors_formula"] == 3
    assert score.recognition_detail["errors_text"] == 0
    assert score.weights()["recognition"] == 1.0


def test_missing_and_spurious_lines():
    lines = textnorm.text_lines(textnorm.parse_reference("\n".join(REF)))
    hyps = [lines[0].text, lines[1].text, lines[3].text, "xxxxxxxx"]
    score = align.score_page(lines, hyps)
    assert score.matching.missing == [2]
    assert score.matching.spurious == [3]
    assert score.missing_chars == len(lines[2].text)
    assert score.spurious_chars == 8


def test_swapped_lines_count_as_order_error():
    lines = textnorm.text_lines(textnorm.parse_reference("\n".join(REF)))
    hyps = [line.text for line in lines]
    hyps[0], hyps[3] = hyps[3], hyps[0]
    score = align.score_page(lines, hyps)
    assert score.inversions > 0
    assert score.distance_reordered == 0
    assert score.order == score.distance_total > 0
    assert score.recognition == 0


def test_merged_and_split_lines():
    lines = textnorm.text_lines(textnorm.parse_reference("\n".join(REF)))
    texts = [line.text for line in lines]
    merged = [texts[0] + " " + texts[1], texts[2], texts[3]]
    m = align.match_lines(texts, merged)
    assert m.merged == 1 and not m.missing and not m.spurious
    split = [texts[0], "A fórmula x^2 + y^2", "= r^2 descreve o círculo", texts[2], texts[3]]
    s = align.match_lines(texts, split)
    assert s.split == 1 and not s.missing and not s.spurious


def test_word_near_misses():
    counts, pairs = align.word_near_misses("a leitura atenta do livro", "a leitora atemta de livro")
    assert counts["sub_d1"] == 3 and counts["words_ok"] == 2
    assert all(d == 1 for _, _, d in pairs)
