"""Testes do gerador de linhas sintéticas (exigem Pillow e fontTools do ambiente do harness)."""

import json

import pytest

pytest.importorskip("PIL")
pytest.importorskip("fontTools")

from build_sentences import REQUIRED_CHARS, build_sentences  # noqa: E402
from PIL import Image  # noqa: E402
from synth import DEFAULT_FONT, generate, missing_glyphs, sha256_file  # noqa: E402


def _write_sentences(tmp_path, count=4):
    path = tmp_path / "sentences.json"
    document = {"sentences": build_sentences()[:count]}
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return path


def test_font_has_glyphs_for_required_alphabet():
    assert missing_glyphs(REQUIRED_CHARS, DEFAULT_FONT) == []
    assert missing_glyphs("日", DEFAULT_FONT) == ["日"]


def test_generate_writes_images_and_consistent_manifest(tmp_path):
    sentences = _write_sentences(tmp_path)
    manifest = generate(
        sentences, DEFAULT_FONT, tmp_path / "img", tmp_path / "manifest.json", root=tmp_path
    )
    assert json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8")) == manifest
    assert len(manifest["lines"]) == 4
    for line in manifest["lines"]:
        path = tmp_path / line["image"]
        assert sha256_file(path) == line["sha256"]
        with Image.open(path) as image:
            assert image.mode == "L"
            assert image.size == (line["width"], line["height"])
            low, high = image.getextrema()
        assert low < 64 and high == 255, "a linha deve ter tinta escura sobre fundo branco"


def test_generation_is_deterministic(tmp_path):
    sentences = _write_sentences(tmp_path)
    first = generate(sentences, DEFAULT_FONT, tmp_path / "a", tmp_path / "a.json", root=tmp_path)
    second = generate(sentences, DEFAULT_FONT, tmp_path / "b", tmp_path / "b.json", root=tmp_path)
    assert [line["sha256"] for line in first["lines"]] == [
        line["sha256"] for line in second["lines"]
    ]


def test_generate_rejects_text_without_glyph(tmp_path):
    path = tmp_path / "sentences.json"
    document = {"sentences": [{"id": "x-1", "text": "linha com 日"}]}
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="glifo"):
        generate(path, DEFAULT_FONT, tmp_path / "img", tmp_path / "m.json", root=tmp_path)
