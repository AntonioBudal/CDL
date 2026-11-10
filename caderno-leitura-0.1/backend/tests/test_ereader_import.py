"""F0.11.03 (spec 105): destaques do Kindle e do Kobo. Arquivos sintéticos gerados aqui; bancos em tmp_path."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Book, InboxCapture, User
from app.services.ereader_import import EreaderFormatError, detect_format
from app.services.ereader_import.kindle import parse_kindle_clippings
from app.services.ereader_import.kobo import parse_kobo_database
from app.services.ereader_import.service import entry_source_hint
from tests.test_inbox import api  # noqa: F401  (fixture: banco migrado com upgrade head)

SEP = "=========="


def kindle_file(*blocks: str, bom=True, crlf=True) -> bytes:
    text = "\n".join(f"{block.strip()}\n{SEP}" for block in blocks) + "\n"
    if crlf:
        text = text.replace("\n", "\r\n")
    return (("﻿" if bom else "") + text).encode("utf-8")


KINDLE_EN = kindle_file(
    """Livro de Teste (Edição Fictícia) (Ana Fictícia)
- Your Highlight on page 32 | Location 488-489 | Added on Monday, March 3, 2025 10:12:01 AM

Primeiro trecho fictício.""",
    """Livro de Teste (Edição Fictícia) (Ana Fictícia)
- Your Note on page 32 | Location 489 | Added on Monday, March 3, 2025 10:13:00 AM

Minha nota fictícia.""",
    """Livro de Teste (Edição Fictícia) (Ana Fictícia)
- Your Bookmark on page 40 | Location 600 | Added on Monday, March 3, 2025 10:20:00 AM

""",
    """Outro Livro Fictício
- Your Highlight on Location 100-02 | Added on Tuesday, March 4, 2025 08:00:00 PM

Trecho sem autor.""",
)

KINDLE_PT = kindle_file(
    """Livro em Português (Bia Teste)
- Seu destaque na página 10 | posição 150-152 | Adicionado: segunda-feira, 3 de março de 2025 10:12:01

Trecho curto""",
    """Livro em Português (Bia Teste)
- Seu destaque na página 10 | posição 150-155 | Adicionado: segunda-feira, 3 de março de 2025 10:12:30

Trecho curto ajustado e mais longo""",
    """Livro em Português (Bia Teste)
- Sua nota na posição 900 | Adicionado: terça-feira, 4 de março de 2025 09:00:00

Nota solta fictícia.""",
    crlf=False,
)


def kobo_file(tmp_path) -> bytes:
    path = tmp_path / "KoboReader.sqlite"
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE content (ContentID TEXT PRIMARY KEY, ContentType INTEGER, Title TEXT, Attribution TEXT);
            CREATE TABLE Bookmark (BookmarkID TEXT PRIMARY KEY, VolumeID TEXT, ContentID TEXT, Text TEXT,
                                   Annotation TEXT, DateCreated TEXT);
            INSERT INTO content VALUES ('vol-1', 6, 'Livro Kobo Fictício', 'Caio Modelo');
            INSERT INTO content VALUES ('vol-1!cap-1', 9, 'Capítulo Kobo 1', NULL);
            INSERT INTO content VALUES ('vol-2', 6, NULL, NULL);
            INSERT INTO Bookmark VALUES ('b1', 'vol-1', 'vol-1!cap-1', 'Destaque Kobo fictício.', 'Anotação Kobo.', '2025-03-03T10:00:00.000');
            INSERT INTO Bookmark VALUES ('b2', 'vol-1', 'vol-1!cap-1', NULL, NULL, '2025-03-03T11:00:00Z');
            INSERT INTO Bookmark VALUES ('b3', 'vol-2', 'vol-2', NULL, 'Só anotação.', '2025-03-05T09:00:00');
            """
        )
    return path.read_bytes()


# ---------- Parsers ----------

def test_detect_format():
    assert detect_format(KINDLE_EN) == "kindle"
    assert detect_format(b"SQLite format 3\x00resto") == "kobo"
    with pytest.raises(EreaderFormatError):
        detect_format("Texto qualquer sem separador".encode())


def test_kindle_english_with_bom_crlf_notes_bookmarks():
    result = parse_kindle_clippings(KINDLE_EN)
    assert result.source == "kindle"
    assert result.skipped == 1, "o marcador é ignorado"
    titles = {(b.title, b.author) for b in result.books}
    assert titles == {("Livro de Teste (Edição Fictícia)", "Ana Fictícia"), ("Outro Livro Fictício", None)}
    first = next(b for b in result.books if b.author == "Ana Fictícia")
    assert len(first.entries) == 1, "a nota foi juntada ao destaque do mesmo lugar"
    entry = first.entries[0]
    assert (entry.text, entry.note, entry.page, entry.location) == (
        "Primeiro trecho fictício.", "Minha nota fictícia.", "32", "488-489")
    assert entry.created_at == datetime(2025, 3, 3, 10, 12, 1)
    other = next(b for b in result.books if b.author is None)
    assert other.entries[0].location == "100-102", "fim abreviado é expandido"


def test_kindle_portuguese_dedupes_adjusted_selection_and_keeps_loose_note():
    result = parse_kindle_clippings(KINDLE_PT)
    book = result.books[0]
    assert (book.title, book.author) == ("Livro em Português", "Bia Teste")
    highlights = [e for e in book.entries if e.kind == "highlight"]
    notes = [e for e in book.entries if e.kind == "note"]
    assert [h.text for h in highlights] == ["Trecho curto ajustado e mais longo"]
    assert highlights[0].created_at == datetime(2025, 3, 3, 10, 12, 30)
    assert [n.note for n in notes] == ["Nota solta fictícia."]


def test_kobo_database(tmp_path):
    result = parse_kobo_database(kobo_file(tmp_path))
    assert result.source == "kobo"
    assert result.skipped == 1, "marcador sem texto"
    by_title = {b.title: b for b in result.books}
    book = by_title["Livro Kobo Fictício"]
    assert book.author == "Caio Modelo"
    entry = book.entries[0]
    assert (entry.text, entry.note, entry.chapter) == ("Destaque Kobo fictício.", "Anotação Kobo.", "Capítulo Kobo 1")
    assert entry.created_at == datetime(2025, 3, 3, 10, 0)
    lonely = by_title["Livro sem título (Kobo)"]
    assert lonely.entries[0].kind == "note"
    assert entry_source_hint("kobo", entry) == "Kobo · cap. Capítulo Kobo 1 · 03/03/2025"


def test_kobo_rejects_other_sqlite(tmp_path):
    path = tmp_path / "outro.sqlite"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE qualquer (id INTEGER)")
    with pytest.raises(EreaderFormatError):
        parse_kobo_database(path.read_bytes())
    with pytest.raises(EreaderFormatError):
        parse_kobo_database(b"SQLite format 3\x00" + b"\x00" * 50)


def test_source_hint_format():
    result = parse_kindle_clippings(KINDLE_EN)
    entry = next(b for b in result.books if b.author).entries[0]
    assert entry_source_hint("kindle", entry) == "Kindle · p. 32 · pos. 488–489 · 03/03/2025"


# ---------- API ----------

def _upload(client, path, data, **form):
    return client.post(f"/api/inbox/ereader/{path}", files={"file": ("arquivo", data, "application/octet-stream")}, data=form)


def test_preview_does_not_write_and_suggests_existing_book(api):  # noqa: F811
    client, engine, _ = api
    existing = client.post("/api/books", json={"title": "livro de teste", "author": "Fictícia, Ana"}).json()
    res = _upload(client, "preview", KINDLE_EN)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["source"] == "kindle" and data["skipped"] == 1 and data["total_entries"] == 2
    match = next(b for b in data["books"] if b["author"] == "Ana Fictícia")
    assert match["suggested_action"] == "existing" and match["suggested_book_id"] == existing["id"]
    other = next(b for b in data["books"] if b["author"] is None)
    assert other["suggested_action"] == "create"
    with Session(engine) as s:
        assert s.scalars(select(InboxCapture)).all() == []


def test_import_creates_captures_and_reimport_skips_duplicates(api):  # noqa: F811
    client, engine, _ = api
    existing = client.post("/api/books", json={"title": "Livro de Teste", "author": "Ana Fictícia"}).json()
    preview = _upload(client, "preview", KINDLE_EN).json()
    first_key = next(b["key"] for b in preview["books"] if b["author"])
    other_key = next(b["key"] for b in preview["books"] if not b["author"])
    choices = [
        {"key": first_key, "action": "existing", "book_id": existing["id"]},
        {"key": other_key, "action": "create"},
    ]
    res = _upload(client, "import", KINDLE_EN, choices=json.dumps(choices))
    assert res.status_code == 200, res.text
    data = res.json()
    assert (data["created"], data["duplicates"]) == (2, 0)
    created_book = next(b for b in data["books"] if b["book_created"])
    assert created_book["book_title"] == "Outro Livro Fictício"

    with Session(engine) as s:
        caps = s.scalars(select(InboxCapture).where(InboxCapture.book_id == existing["id"])).all()
        assert len(caps) == 1
        assert caps[0].content == "Primeiro trecho fictício.\n\nNota: Minha nota fictícia."
        assert caps[0].source_hint == "Kindle · p. 32 · pos. 488–489 · 03/03/2025"
        assert caps[0].status == "inbox" and caps[0].chapter_id is None

    choices[1] = {"key": other_key, "action": "existing", "book_id": created_book["book_id"]}
    again = _upload(client, "import", KINDLE_EN, choices=json.dumps(choices)).json()
    assert (again["created"], again["duplicates"]) == (0, 2)
    after = next(b for b in _upload(client, "preview", KINDLE_EN).json()["books"] if b["author"])
    assert (after["new_count"], after["duplicate_count"]) == (0, 1), "a prévia já conta o que está na Mesa"


def test_skip_and_kobo_import(api, tmp_path):  # noqa: F811
    client, engine, _ = api
    data = kobo_file(tmp_path)
    preview = _upload(client, "preview", data).json()
    assert preview["source"] == "kobo"
    keys = {b["title"]: b["key"] for b in preview["books"]}
    choices = [
        {"key": keys["Livro Kobo Fictício"], "action": "create"},
        {"key": keys["Livro sem título (Kobo)"], "action": "skip"},
    ]
    res = _upload(client, "import", data, choices=json.dumps(choices)).json()
    assert res["created"] == 1 and len(res["books"]) == 1
    with Session(engine) as s:
        assert s.scalar(select(Book).where(Book.title == "Livro sem título (Kobo)")) is None
        cap = s.scalars(select(InboxCapture)).one()
        assert cap.content == "Destaque Kobo fictício.\n\nNota: Anotação Kobo."


def test_invalid_file_choices_and_foreign_book(api):  # noqa: F811
    client, engine, _ = api
    bad = _upload(client, "preview", "texto qualquer".encode())
    assert bad.status_code == 422
    assert "Não reconheci" in bad.json()["detail"]
    assert _upload(client, "preview", b"").status_code == 400
    assert _upload(client, "import", KINDLE_EN, choices="{não é json").status_code == 422

    with Session(engine) as s:
        s.add(User(id="88888888-8888-8888-8888-888888888888", username="alheia", display_name="Alheia",
                   role="user", status="ativo"))
        s.flush()
        foreign = Book(user_id="88888888-8888-8888-8888-888888888888", title="Livro Alheio")
        s.add(foreign)
        s.commit()
        foreign_id = foreign.id
    res = _upload(client, "import", KINDLE_EN, choices=json.dumps([{"key": "0", "action": "existing", "book_id": foreign_id}]))
    assert res.status_code == 404
    with Session(engine) as s:
        assert s.scalars(select(InboxCapture)).all() == []


def test_kindle_size_limit(api, monkeypatch):  # noqa: F811
    client, _, _ = api
    monkeypatch.setattr("app.services.ereader_import.service.KINDLE_MAX_BYTES", 10)
    assert _upload(client, "preview", KINDLE_EN).status_code == 413
