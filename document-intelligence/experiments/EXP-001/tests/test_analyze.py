"""Testes da análise de erros: alinhamento, classes de caractere, confusões e CERs auxiliares."""

import pytest
from analyze import (
    EMPTY,
    align,
    analyze,
    char_class,
    glue_punctuation,
    load_symbols,
    strip_diacritics,
)

from leitorum_di.metrics.base import levenshtein_distance


def test_char_classes():
    expected = {
        "ã": "acentuada", "É": "acentuada", "ç": "cedilha", "Ç": "cedilha", "7": "dígito",
        "?": "pontuação", '"': "pontuação", "A": "maiúscula", "z": "minúscula", " ": "espaço",
    }  # fmt: skip
    assert {char: char_class(char) for char in expected} == expected


@pytest.mark.parametrize(
    ("reference", "hypothesis"),
    [("", ""), ("abc", ""), ("", "abc"), ("ação", "acao"), ("casa", "caasa"), ("pato", "gato!")],
)
def test_alignment_is_consistent_with_levenshtein(reference, hypothesis):
    ops = align(reference, hypothesis)
    assert "".join(r for _, r, _ in ops if r is not None) == reference
    assert "".join(h for _, _, h in ops if h is not None) == hypothesis
    assert sum(op != "eq" for op, _, _ in ops) == levenshtein_distance(reference, hypothesis)


def test_alignment_operations():
    assert align("ação", "acao") == [
        ("eq", "a", "a"), ("sub", "ç", "c"), ("sub", "ã", "a"), ("eq", "o", "o"),
    ]  # fmt: skip
    assert [op for op, _, _ in align("ab", "a")] == ["eq", "del"]
    assert [op for op, _, _ in align("a", "ab")] == ["eq", "ins"]


def test_analyze_counts_by_class_and_confusions():
    result = analyze([("ação 12", "acao l2"), ("Olá.", "Olá .")])
    assert result["operations"] == {"eq": 8, "sub": 3, "del": 0, "ins": 1}
    assert result["by_class"]["cedilha"] == {
        "ref_chars": 1, "errors": 1, "error_rate": 1.0, "insertions": 0,
    }  # fmt: skip
    assert result["by_class"]["acentuada"]["ref_chars"] == 2
    assert result["by_class"]["acentuada"]["errors"] == 1
    assert result["by_class"]["dígito"]["error_rate"] == 0.5
    assert result["by_class"]["espaço"]["insertions"] == 1
    assert result["by_class"]["outro"]["error_rate"] is None
    confusions = {(c["ref"], c["hyp"]): c["count"] for c in result["top_confusions"]}
    assert confusions == {("ç", "c"): 1, ("ã", "a"): 1, ("1", "l"): 1, (EMPTY, " "): 1}
    pairs = {(p["a"], p["b"]): p["count"] for p in result["ambiguous_pairs"]}
    assert pairs[("l", "1")] == 1


def test_auxiliary_cers_isolate_error_sources():
    result = analyze([("ação 12", "acao l2"), ("Olá.", "olá .")])
    assert result["cer"] == pytest.approx(5 / 11)
    assert result["cer_without_diacritics"] == pytest.approx(3 / 11)
    assert result["cer_case_insensitive"] == pytest.approx(4 / 11)
    assert result["cer_punctuation_glued"] == pytest.approx(4 / 11)


def test_text_helpers():
    assert strip_diacritics("ação é pão") == "acao e pao"
    assert glue_punctuation("( a , b ) . Fim ?") == "(a, b). Fim?"


def test_alphabet_coverage(tmp_path):
    syms = tmp_path / "syms.txt"
    syms.write_text("<ctc> 0\na 1\nc 2\no 3\n<space> 4\n", encoding="utf-8")
    symbols = load_symbols(syms)
    assert symbols == {"a", "c", "o"}
    result = analyze([("ação", "acao")], symbols)
    assert result["alphabet"]["unreachable_ref_chars"] == 2
    assert result["alphabet"]["unreachable_by_char"] == {"ç": 1, "ã": 1}
    assert result["alphabet"]["unreachable_share"] == 0.5
