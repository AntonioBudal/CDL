# ruff: noqa: N806 — A e S seguem a notação da spec
"""Invariantes da organização (spec §2) e regras de segmentação (spec §3 e decisão 2 da §11)."""

import random

import organizer as org
import pytest
from noise import corrupt
from pages import build_pages, layout, page_text
from train import seed_model


@pytest.fixture(scope="module")
def engine():
    return org.Organizer(seed_model())


@pytest.fixture(scope="module")
def sample_pages():
    pages = build_pages()
    return pages["train"][:10] + pages["val"][:5]


def covered(text, result):
    marks = [0] * len(text)
    for seg in result["segments"]:
        for i in range(seg["start"], seg["end"]):
            marks[i] += 1
    return marks


def test_lossless_every_non_space_char_exactly_once(engine, sample_pages):
    for page in sample_pages:
        text, _, _ = page_text(page)
        for geo in (True, False):
            result = engine.organize(text, layout(page) if geo else None)
            marks = covered(text, result)
            assert all(m == 1 for ch, m in zip(text, marks, strict=False) if not ch.isspace())
            assert all(m <= 1 for m in marks)
            starts = [s["start"] for s in result["segments"]]
            assert starts == sorted(starts)


def test_sections_are_original_text_only(engine, sample_pages):
    text, _, _ = page_text(sample_pages[0])
    result = engine.organize(text)
    pieces = [text[s["start"] : s["end"]] for s in result["segments"]]
    for section, body in result["sections"].items():
        segs = zip(pieces, result["segments"], strict=True)
        expected = [p for p, s in segs if s["section"] == section]
        assert body == "\n".join(expected)


def test_lossless_with_reading_noise(engine, sample_pages):
    model = {
        "cer": 0.29,
        "p_delete": {"a": 0.1, "e": 0.1},
        "p_substitute": {"o": 0.2, "s": 0.2},
        "substitute_to": {"o": {"a": 1}, "s": {"5": 1}},
        "p_insert": 0.02,
        "insert_chars": {"i": 1, ".": 1},
    }
    rng = random.Random(1)
    for page in sample_pages[:5]:
        text, labels, _ = page_text(page)
        noisy, _ = corrupt(text, list(labels), model, 0.25, rng)
        result = engine.organize(noisy)
        marks = covered(noisy, result)
        assert all(m == 1 for ch, m in zip(noisy, marks, strict=True) if not ch.isspace())


def test_deterministic(engine, sample_pages):
    text, _, _ = page_text(sample_pages[3])
    first = engine.organize(text, layout(sample_pages[3]))
    second = engine.organize(text, layout(sample_pages[3]))
    assert first["segments"] == second["segments"]
    assert first["sections"] == second["sections"]


def test_empty_text(engine):
    assert engine.organize("  \n \n")["segments"] == []


def test_explicit_headings_are_hard_constraints(engine):
    text = (
        "Conceitos:\nTermo de teste: definição fictícia.\n"
        "Resumo:\nO capítulo trata de um tema fictício.\n"
        "Referências\nSOBRENOME, Nome. Livro de Teste. Cidade: Editora, 2020."
    )
    result = engine.organize(text)
    assert result["explicit_headings"] is True
    by_text = {text[s["start"] : s["end"]]: s["section"] for s in result["segments"]}
    assert by_text["Termo de teste: definição fictícia."] == "concepts"
    assert by_text["O capítulo trata de um tema fictício."] == "summary"
    assert by_text["SOBRENOME, Nome. Livro de Teste. Cidade: Editora, 2020."] == "references"


def test_wrapped_abnt_reference_stays_whole():
    units, _ = org.segment("SOBRENOME, Nome. Livro de Teste. Cidade:\nEditora Fictícia, 2019.")
    assert [u.text for u in units] == [
        "SOBRENOME, Nome. Livro de Teste. Cidade:\nEditora Fictícia, 2019."
    ]


def test_page_comment_and_quote_lines_are_own_units():
    text = (
        "Uma ideia de teste sobre o capítulo\np. 23 — achei confuso o exemplo\n"
        "“Citação fictícia que\ncontinua aqui.”\ncf. cap. 4"
    )
    units, _ = org.segment(text)
    assert [u.text for u in units] == [
        "Uma ideia de teste sobre o capítulo",
        "p. 23 — achei confuso o exemplo",
        "“Citação fictícia que\ncontinua aqui.”",
        "cf. cap. 4",
    ]


def test_abbreviations_do_not_split_sentences():
    units, _ = org.segment(
        "Ver o cap. 4 e a fig. 2 do livro, p. 30. Depois comparar com o Sr. Fulano de Teste."
    )
    assert len(units) == 2


def test_lines_join_by_continuation_cues():
    units, _ = org.segment(
        "A leitura de teste continua\nna linha seguinte sem ponto.\nOutra frase começa aqui."
    )
    assert [u.text for u in units] == [
        "A leitura de teste continua\nna linha seguinte sem ponto.",
        "Outra frase começa aqui.",
    ]


def test_layout_gap_breaks_paragraph():
    text = (
        "Primeira frase de teste sem ponto\nsegunda linha do mesmo parágrafo\n"
        "novo parágrafo depois de um espaço"
    )
    layout_lines = [
        {"text": "Primeira frase de teste sem ponto", "bbox": [120, 100, 1500, 150]},
        {"text": "segunda linha do mesmo parágrafo", "bbox": [120, 175, 900, 225]},
        {"text": "novo parágrafo depois de um espaço", "bbox": [180, 400, 1500, 450]},
    ]
    units, _ = org.segment(text, layout_lines)
    assert len(units) == 2
    assert units[1].text == "novo parágrafo depois de um espaço"


def test_edited_text_keeps_matching_geometry():
    lines = org.split_lines("linha um\nlinha dois editada\nlinha nova")
    org.attach_layout(
        lines,
        [{"text": "linha um", "bbox": [1, 2, 3, 4]}, {"text": "linha dois", "bbox": [5, 6, 7, 8]}],
    )
    assert lines[0].bbox == [1, 2, 3, 4]
    assert lines[2].bbox is None


def test_fuzzy_cues_tolerate_one_error():
    cue = org.CueIndex({"x": ["portanto", "por exemplo"]})
    assert cue.count(org.words(org.fold("Portamto isso vale")))["x"] == 1
    assert cue.count(org.words(org.fold("por exemplu")))["x"] == 1


def test_viterbi_switch_cost_keeps_cohesive_neighbours_together():
    A = [[0.0, -0.1, -9, -9], [-0.2, 0.0, -9, -9], [0.0, -0.1, -9, -9]]
    S = {(0, 1): 5.0, (1, 0): 5.0, (1, 2): 5.0, (2, 1): 5.0}
    path, marginals = org.decode(A, S, {"tau": 0.0, "omega": 0.0, "lambda": 1.0})
    assert len(set(path)) == 1
    assert all(abs(sum(row) - 1) < 1e-9 for row in marginals)
