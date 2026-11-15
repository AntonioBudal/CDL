"""F0.12.03 (spec 116): importar a biblioteca (Goodreads, StoryGraph, BookWyrm). Arquivos fictícios; tmp_path."""
from __future__ import annotations

import json
from datetime import date

import pytest

from app.services.library_import import (
    LibraryFormatError,
    detect_library_format,
    normalize_isbn,
    parse_date,
    parse_library,
)
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    sharing_harness,
)

GOODREADS = (
    "Book Id,Title,Author,Author l-f,Additional Authors,ISBN,ISBN13,My Rating,Average Rating,Publisher,Binding,"
    "Number of Pages,Year Published,Original Publication Year,Date Read,Date Added,Bookshelves,"
    "Bookshelves with positions,Exclusive Shelf,My Review,Spoiler,Private Notes,Read Count,Recommended For,"
    "Recommended By,Owned Copies,Original Purchase Date,Original Purchase Location,Condition,Condition Description,BCID\n"
    '1,Livro de Teste,Ana Fictícia,"Fictícia, Ana",Bia Fictícia,"=""8535900000""","=""9788535900002""",5,4.1,'
    'Editora Fictícia,Paperback,200,2020,2019,2021/03/12,2021/01/02,,,read,"Gostei <b>muito</b>.<br/>Fim.",,,1,,,0,,,,,\n'
    '2,Outro Livro Fictício,Caio Fictício,"Fictício, Caio",,"=""""","=""""",0,4.0,,,,,,,2021/02/02,,,to-read,,,,0,,,0,,,,,\n'
    '3,Lendo Agora,Dora Fictícia,"Fictícia, Dora",,"=""""","=""""",0,4.0,,,,,,,2021/02/02,,,currently-reading,,,,0,,,0,,,,,\n'
)
STORYGRAPH = (
    "﻿Title,Authors,Contributors,ISBN/UID,Format,Read Status,Date Added,Last Date Read,Dates Read,Read Count,Moods,"
    "Pace,Character- or Plot-Driven?,Strong Character Development?,Loveable Characters?,Diverse Characters?,"
    "Flawed Characters?,Star Rating,Review,Content Warnings,Content Warning Description,Tags,Owned?\r\n"
    '"Livro Coletivo","Ana Fictícia, Bia Fictícia","",9780520227354,,read,2021/05/10,2021/06/01,"",1,,,,,,,,4.5,"Boa leitura.",,,,No\r\n'
    '"Abandonado Fictício",Caio Fictício,"",,,did-not-finish,2021/05/10,"","",0,,,,,,,,,,,,,No\r\n'
)
BOOKWYRM = (
    "title,author_text,openlibrary_key,isbn_10,isbn_13,oclc_number,pages,start_date,finish_date,stopped_date,rating,"
    "review_name,review_cw,review_content,review_published,shelf,shelf_name,shelf_date\n"
    "Livro Wyrm,Ana Fictícia,,,9781250313195,,300,2022-01-02,2022-02-03,,4,,,<p>Resenha fictícia.</p>,2022-02-04,read,Read,2022-02-03\n"
    "Parado,Bia Fictícia,,,,,100,2022-01-02,,2022-01-20,,,,,,stopped-reading,Stopped Reading,2022-01-20\n"
)


def test_helpers():
    assert normalize_isbn('="9788535900002"') == "9788535900002"
    assert normalize_isbn("85-359-0000-X") == "853590000X"
    assert normalize_isbn('=""') is None
    assert parse_date("2021/03/12") == date(2021, 3, 12) and parse_date("2022-02-03") == date(2022, 2, 3)
    assert parse_date("2022-02-03T10:00:00Z") == date(2022, 2, 3) and parse_date("ontem") is None


def test_detection_and_parsers():
    assert detect_library_format(GOODREADS.encode()) == "goodreads"
    assert detect_library_format(STORYGRAPH.encode("utf-8")) == "storygraph"
    assert detect_library_format(BOOKWYRM.encode()) == "bookwyrm"
    with pytest.raises(LibraryFormatError):
        detect_library_format(b"Highlight,Book Title\nx,y\n")

    gr = parse_library(GOODREADS.encode())
    first, second, third = gr.rows
    assert (first.title, first.author, first.isbn, first.year, first.publisher) == (
        "Livro de Teste", "Ana Fictícia; Bia Fictícia", "9788535900002", 2020, "Editora Fictícia")
    assert (first.state, first.finished_on) == ("lido", date(2021, 3, 12))
    assert first.review == "Gostei muito.\nFim."
    assert (second.state, second.isbn, third.state) == ("quero_ler", None, "lendo")

    sg = parse_library(STORYGRAPH.encode("utf-8"))
    assert sg.rows[0].author == "Ana Fictícia; Bia Fictícia" and sg.rows[0].isbn == "9780520227354"
    assert (sg.rows[0].state, sg.rows[0].finished_on) == ("lido", date(2021, 6, 1))
    assert sg.rows[1].state == "abandonado"

    bw = parse_library(BOOKWYRM.encode())
    assert (bw.rows[0].state, bw.rows[0].started_on, bw.rows[0].finished_on) == ("lido", date(2022, 1, 2), date(2022, 2, 3))
    assert bw.rows[0].review == "Resenha fictícia."
    assert (bw.rows[1].state, bw.rows[1].finished_on) == ("abandonado", date(2022, 1, 20))


def test_semicolon_csv_and_duplicates():
    data = "Title;Authors;Read Status;ISBN/UID\nRepetido;Ana Fictícia;read;9780520227354\nRepetido;Ana Fictícia;read;9780520227354\n;x;read;\n"
    parsed = parse_library(data.encode())
    assert len(parsed.rows) == 1 and parsed.skipped == 2


def _post(client, url, data, **form):
    return client.post(url, files={"file": ("biblioteca.csv", data, "text/csv")}, data=form)


def test_preview_and_import(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    existing = c.post("/api/books", json={"title": "Livro de Teste", "author": "Ana Fictícia"}).json()
    by_isbn = c.post("/api/books", json={"title": "Título Diferente", "author": "Caio Fictício"}).json()
    c.patch(f"/api/books/{by_isbn['id']}", json={"isbn": "9780520227354"})

    preview = _post(c, "/api/books/import-library/preview", GOODREADS.encode())
    assert preview.status_code == 200, preview.text
    data = preview.json()
    assert data["service"] == "goodreads" and data["service_label"] == "Goodreads"
    assert [(r["title"], r["existing_book_id"], r["suggested_action"]) for r in data["rows"]] == [
        ("Livro de Teste", existing["id"], "skip"), ("Outro Livro Fictício", None, "create"), ("Lendo Agora", None, "create"),
    ]
    assert len(c.get("/api/books").json()) == 2, "a prévia não grava"

    choices = [{"key": "0", "action": "update"}, {"key": "1", "action": "create"}, {"key": "2", "action": "skip"}]
    res = _post(c, "/api/books/import-library/import", GOODREADS.encode(), choices=json.dumps(choices), with_reviews="true")
    assert res.status_code == 200, res.text
    assert {k: res.json()[k] for k in ("created", "updated", "skipped", "reviews")} == {
        "created": 1, "updated": 1, "skipped": 1, "reviews": 1}
    updated = c.get(f"/api/books/{existing['id']}").json()
    assert (updated["reading_state"], updated["reading_finished_on"]) == ("lido", "2021-03-12")
    inbox = c.get("/api/inbox").json()
    assert [(i["content"], i["source_hint"]) for i in inbox] == [("Gostei muito.\nFim.", "Resenha do Goodreads · 12/03/2021")]

    sg = _post(c, "/api/books/import-library/preview", STORYGRAPH.encode("utf-8")).json()
    assert sg["rows"][0]["isbn"] == "9780520227354"
    assert sg["rows"][0]["existing_book_id"] == by_isbn["id"], "casamento por ISBN, mesmo com título diferente"
    assert sg["rows"][1]["existing_book_id"] is None

    assert all(b["title"] != "Outro Livro Fictício" for b in sharing_harness.client_bob.get("/api/books").json()), \
        "isolamento entre leitores"


def test_errors(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    assert _post(c, "/api/books/import-library/preview", b"a,b\n1,2\n").status_code == 422
    assert _post(c, "/api/books/import-library/preview", b"").status_code == 422
    big = b"Title,Authors,Read Status\n" + b"x,y,read\n" * (1024 * 1024 + 10)
    assert _post(c, "/api/books/import-library/preview", big).status_code == 413
    bad = _post(c, "/api/books/import-library/import", GOODREADS.encode(), choices="não é json")
    assert bad.status_code == 422
