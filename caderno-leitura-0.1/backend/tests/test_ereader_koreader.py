"""F0.11.09 (spec 111): parsers do JSON do KOReader e do corpo Readwise (Readest). Só dados fictícios."""
from __future__ import annotations

import json

import pytest

from app.schemas.receiver import ReadwiseHighlightIn
from app.services.ereader_import import EreaderFormatError, detect_format
from app.services.ereader_import.koreader import parse_koreader_json
from app.services.ereader_import.readwise import parse_readwise_highlights

ONE_BOOK = {
    "title": "Livro de Teste", "author": "Ana Fictícia", "number_of_pages": 200, "file": "/livros/teste.epub",
    "exported": True, "created_on": 1762950000, "version": "json/1.0.0",
    "entries": [
        {"sort": "highlight", "page": 12, "time": 1762950000, "text": "Trecho fictício um.", "chapter": "Capítulo 1",
         "drawer": "lighten", "color": "yellow"},
        {"sort": "highlight", "page": 15, "time": 1762950100, "text": "Trecho fictício dois.", "note": "Minha nota."},
        {"sort": "highlight", "page": 16, "time": 1762950200, "text": "  "},
    ],
}


def test_koreader_single_book():
    data = json.dumps(ONE_BOOK).encode()
    assert detect_format(data) == "koreader"
    parsed = parse_koreader_json(data)
    assert parsed.source == "koreader" and parsed.skipped == 1
    [book] = parsed.books
    assert (book.title, book.author) == ("Livro de Teste", "Ana Fictícia")
    first, second = book.entries
    assert (first.text, first.page, first.chapter) == ("Trecho fictício um.", "12", "Capítulo 1")
    assert first.created_at.year == 2025 and first.created_at.tzinfo is not None
    assert (second.note, second.kind) == ("Minha nota.", "highlight")


def test_koreader_many_books_and_bom():
    many = {"created_on": 1762950000, "version": "json/1.0.0", "documents": [
        ONE_BOOK, {"title": "Outro Livro", "author": "", "entries": [{"text": "Só um trecho.", "page": "iv"}]},
        {"title": "Vazio", "entries": []},
    ]}
    data = b"\xef\xbb\xbf" + json.dumps(many).encode()
    assert detect_format(data) == "koreader"
    parsed = parse_koreader_json(data)
    assert [b.title for b in parsed.books] == ["Livro de Teste", "Outro Livro"]
    assert parsed.books[1].author is None and parsed.books[1].entries[0].page == "iv"


def test_other_json_is_rejected():
    with pytest.raises(EreaderFormatError):
        detect_format(json.dumps({"highlights": []}).encode())
    with pytest.raises(EreaderFormatError):
        parse_koreader_json(b"{nao e json")


def test_readwise_body_groups_books_and_skips_bookmarks():
    items = [ReadwiseHighlightIn.model_validate(x) for x in (
        {"text": "Trecho A.", "title": "Livro de Teste", "author": "Ana Fictícia", "note": "", "location": 12,
         "location_type": "page", "highlighted_at": "2026-11-10T12:00:00.000Z", "source_type": "readest",
         "category": "books", "color": "yellow", "highlight_url": "readest://x"},
        {"text": "Trecho B.", "title": "Livro de Teste", "author": "Ana Fictícia", "location": 30,
         "location_type": "order", "source_type": "readest"},
        {"text": "Page 40", "title": "Livro de Teste", "author": "Ana Fictícia", "source_type": "readest"},
        {"text": "", "title": "Livro de Teste", "source_type": "readest"},
        {"text": "Trecho C.", "title": "Outro Livro", "author": None, "source_type": "readest"},
    )]
    parsed = parse_readwise_highlights(items)
    assert parsed.source == "readest" and parsed.skipped == 2
    assert [(b.title, len(b.entries)) for b in parsed.books] == [("Livro de Teste", 2), ("Outro Livro", 1)]
    a, b = parsed.books[0].entries
    assert (a.page, a.location, a.created_at.isoformat()) == ("12", None, "2026-11-10T12:00:00+00:00")
    assert (b.page, b.location) == (None, "30")
