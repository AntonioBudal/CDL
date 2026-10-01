"""Testes das frases sintéticas: cobertura do alfabeto PT-BR, unicidade e determinismo."""

import json
import unicodedata

from build_sentences import (
    COUNT,
    DEFAULT_OUT,
    MAX_CHARS,
    REQUIRED_CHARS,
    build_sentences,
    render_document,
)


def test_sentences_cover_required_alphabet():
    text = "".join(item["text"] for item in build_sentences())
    assert not set(REQUIRED_CHARS) - set(text)


def test_sentences_are_unique_nfc_and_line_sized():
    sentences = build_sentences()
    texts = [item["text"] for item in sentences]
    assert len(sentences) == COUNT == len(set(texts))
    assert len({item["id"] for item in sentences}) == COUNT
    for text in texts:
        assert text == unicodedata.normalize("NFC", text)
        assert 0 < len(text) <= MAX_CHARS


def test_generation_is_deterministic_and_matches_committed_fixture():
    assert build_sentences() == build_sentences()
    committed = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert committed == json.loads(render_document())
