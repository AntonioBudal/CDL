"""F0.12.03 (spec 116): destaques do Readwise (CSV) e do Omnivore (ZIP). Arquivos fictícios montados no teste."""
from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime

import pytest

from app.services.ereader_import import EreaderFormatError, detect_format
from app.services.ereader_import import omnivore
from app.services.ereader_import.omnivore import parse_highlights_markdown, parse_omnivore_zip
from app.services.ereader_import.readwise_csv import parse_readwise_csv
from tests.test_sharing_and_permissions import (  # noqa: F401
    sharing_harness,
)

READWISE = (
    "Highlight,Book Title,Book Author,Amazon Book ID,Note,Color,Tags,Location Type,Location,Highlighted at,Document tags\n"
    'Trecho fictício um.,Livro de Teste,Ana Fictícia,,Minha nota.,yellow,,page,12,2024-03-12 10:00:00+00:00,\n'
    'Trecho fictício dois.,Livro de Teste,Ana Fictícia,,,yellow,,order,345,2024-03-13T11:00:00Z,\n'
    ',Livro de Teste,Ana Fictícia,,,,,,,,\n'
)
HIGHLIGHTS_MD = "> Trecho do artigo\n> em duas linhas\n\n#leitura #teste\n\nMinha anotação.\n\n> Segundo trecho\n\nNota solta, sem trecho."


def _zip(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buffer.getvalue()


OMNIVORE = _zip({
    "metadata_0_to_20.json": json.dumps([
        {"id": "1", "slug": "artigo-ficticio", "title": "Artigo Fictício", "author": "Bia Fictícia", "savedAt": "2024-01-01"},
        {"id": "2", "slug": "sem-destaques", "title": "Sem Destaques"},
    ]),
    "content/artigo-ficticio.html": "<p>conteúdo</p>",
    "highlights/artigo-ficticio.md": HIGHLIGHTS_MD,
})


def test_readwise():
    assert detect_format(READWISE.encode()) == "readwise"
    parsed = parse_readwise_csv(READWISE.encode())
    assert parsed.source == "readwise" and parsed.skipped == 1
    [book] = parsed.books
    first, second = book.entries
    assert (first.text, first.note, first.page, first.location) == ("Trecho fictício um.", "Minha nota.", "12", None)
    assert first.created_at == datetime.fromisoformat("2024-03-12T10:00:00+00:00")
    assert (second.page, second.location) == (None, "345")
    with pytest.raises(EreaderFormatError):
        parse_readwise_csv(b"Highlight,Title\nx,y\n")


def test_omnivore_markdown_and_zip():
    assert parse_highlights_markdown(HIGHLIGHTS_MD) == [
        ("Trecho do artigo\nem duas linhas", "Minha anotação."),
        ("Segundo trecho", "Nota solta, sem trecho."),
    ]
    assert detect_format(OMNIVORE) == "omnivore"
    parsed = parse_omnivore_zip(OMNIVORE)
    assert parsed.source == "omnivore"
    [book] = parsed.books
    assert (book.title, book.author, len(book.entries)) == ("Artigo Fictício", "Bia Fictícia", 2)


def test_omnivore_limits(monkeypatch):
    with pytest.raises(EreaderFormatError):
        parse_omnivore_zip(_zip({"outro.txt": "x"}))
    monkeypatch.setattr(omnivore, "MAX_MEMBERS", 2)
    with pytest.raises(EreaderFormatError):
        parse_omnivore_zip(OMNIVORE)
    monkeypatch.setattr(omnivore, "MAX_MEMBERS", 5000)
    monkeypatch.setattr(omnivore, "MAX_UNCOMPRESSED", 10)
    with pytest.raises(EreaderFormatError):
        parse_omnivore_zip(OMNIVORE)
    with pytest.raises(EreaderFormatError):
        parse_omnivore_zip(b"PK\x03\x04 corrompido")


def test_api_imports_both(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    for name, data, label in (("readwise.csv", READWISE.encode(), "Readwise"), ("omnivore.zip", OMNIVORE, "Omnivore")):
        preview = c.post("/api/inbox/ereader/preview", files={"file": (name, data, "application/octet-stream")})
        assert preview.status_code == 200, preview.text
        body = preview.json()
        choices = [{"key": b["key"], "action": "create"} for b in body["books"]]
        res = c.post("/api/inbox/ereader/import", files={"file": (name, data, "application/octet-stream")},
                     data={"choices": json.dumps(choices)})
        assert res.status_code == 200, res.text
        assert res.json()["created"] == 2
    hints = {i["source_hint"] for i in c.get("/api/inbox").json()}
    assert "Readwise · p. 12 · 12/03/2024" in hints and any(h.startswith("Omnivore") for h in hints)
