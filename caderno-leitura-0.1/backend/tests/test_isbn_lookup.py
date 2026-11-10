"""F0.11.04 (spec 106): ISBN sob demanda. Nenhum teste vai à rede: respostas simuladas com httpx.MockTransport."""
from __future__ import annotations

import io
import json
import sqlite3
import zipfile

import httpx
import pytest
from alembic import command
from alembic.config import Config

from app.core.config import BACKEND_DIR
from app.services import isbn_service
from app.services.isbn_service import InvalidIsbnError, normalize_isbn
from tests.test_inbox import api  # noqa: F401  (fixture: banco migrado com upgrade head)

ISBN13 = "9788535908466"  # ISBN-13 sintético com dígito verificador válido
ISBN10 = "8535908463"     # mesmo livro em ISBN-10 → 9788535908466

BRASILAPI_OK = {
    "isbn": ISBN13, "title": "Livro Fictício da BrasilAPI", "subtitle": "um subtítulo",
    "authors": ["Ana Fictícia", "Bia Teste"], "publisher": "Editora Fictícia", "location": "São Paulo",
    "year": 1997, "provider": "teste",
}
OPENLIB_OK = {
    f"ISBN:{ISBN13}": {
        "title": "Fictional Open Library Book",
        "authors": [{"name": "Caio Modelo"}],
        "publishers": [{"name": "Fictional Press"}],
        "publish_places": [{"name": "London"}],
        "publish_date": "March 1999",
    }
}


@pytest.fixture
def fake_net():
    """Instala um transporte falso; cada teste define as respostas por domínio."""
    routes: dict[str, httpx.Response | Exception] = {}
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        assert request.headers.get("user-agent") == "Leitorum"
        assert "cookie" not in request.headers
        reply = routes.get(request.url.host)
        if isinstance(reply, Exception):
            raise reply
        return reply or httpx.Response(404)

    isbn_service.set_transport(httpx.MockTransport(handler))
    yield routes, calls
    isbn_service.set_transport(None)


# ---------- ISBN ----------

def test_normalize_isbn():
    assert normalize_isbn(ISBN13) == ISBN13
    assert normalize_isbn("978-85-359-0846-6") == ISBN13
    assert normalize_isbn(ISBN10) == ISBN13
    assert normalize_isbn("85-359-0846-3") == ISBN13
    for bad in ("9788535908467", "8535908464", "123", "", None, "9771234567898"):
        with pytest.raises(InvalidIsbnError):
            normalize_isbn(bad)


# ---------- Busca ----------

def test_brasilapi_found(api, fake_net):  # noqa: F811
    client, _, _ = api
    routes, calls = fake_net
    routes["brasilapi.com.br"] = httpx.Response(200, json=BRASILAPI_OK)
    res = client.get(f"/api/books/isbn/{ISBN10}")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["source"] == "brasilapi" and data["isbn"] == ISBN13
    assert data["author"] == "Ana Fictícia; Bia Teste"
    assert (data["publisher"], data["place"], data["year"]) == ("Editora Fictícia", "São Paulo", 1997)
    assert len(calls) == 1 and calls[0].endswith(f"/api/isbn/v1/{ISBN13}")


def test_falls_back_to_openlibrary(api, fake_net):  # noqa: F811
    client, _, _ = api
    routes, calls = fake_net
    routes["brasilapi.com.br"] = httpx.Response(404)
    routes["openlibrary.org"] = httpx.Response(200, json=OPENLIB_OK)
    data = client.get(f"/api/books/isbn/{ISBN13}").json()
    assert data["source"] == "openlibrary"
    assert (data["title"], data["author"], data["year"], data["publisher"], data["place"]) == (
        "Fictional Open Library Book", "Caio Modelo", 1999, "Fictional Press", "London")
    assert len(calls) == 2


def test_not_found_unavailable_invalid_and_bad_payload(api, fake_net):  # noqa: F811
    client, _, _ = api
    routes, calls = fake_net
    routes["openlibrary.org"] = httpx.Response(200, json={})
    res = client.get(f"/api/books/isbn/{ISBN13}")
    assert res.status_code == 404 and "Não encontrei" in res.json()["detail"]

    routes["brasilapi.com.br"] = httpx.ConnectError("sem rede")
    routes["openlibrary.org"] = httpx.ReadTimeout("demorou")
    res = client.get(f"/api/books/isbn/{ISBN13}")
    assert res.status_code == 503

    routes["brasilapi.com.br"] = httpx.Response(200, content=b"<html>nao e json</html>")
    routes["openlibrary.org"] = httpx.Response(500)
    assert client.get(f"/api/books/isbn/{ISBN13}").status_code == 404, "um serviço respondeu: não encontrado"

    calls.clear()
    res = client.get("/api/books/isbn/1234")
    assert res.status_code == 422 and calls == [], "ISBN inválido não vai à rede"


def test_redirect_is_not_followed(api, fake_net):  # noqa: F811
    client, _, _ = api
    routes, calls = fake_net
    routes["brasilapi.com.br"] = httpx.Response(302, headers={"Location": "http://127.0.0.1/interno"})
    routes["openlibrary.org"] = httpx.Response(404)
    assert client.get(f"/api/books/isbn/{ISBN13}").status_code == 404
    assert all("127.0.0.1" not in call for call in calls)


def test_switch_off(api, fake_net, monkeypatch):  # noqa: F811
    client, _, _ = api
    _routes, calls = fake_net
    monkeypatch.setenv("LEITORUM_ISBN_LOOKUP", "off")
    res = client.get(f"/api/books/isbn/{ISBN13}")
    assert res.status_code == 404 and "desligada" in res.json()["detail"]
    assert calls == []


def test_existing_book_warned(api, fake_net):  # noqa: F811
    client, _, _ = api
    routes, _ = fake_net
    routes["brasilapi.com.br"] = httpx.Response(200, json=BRASILAPI_OK)
    own = client.post("/api/books", json={"title": "Livro de Teste", "isbn": ISBN10}).json()
    assert own["isbn"] == ISBN13
    data = client.get(f"/api/books/isbn/{ISBN13}").json()
    assert data["existing_book"] == {"id": own["id"], "title": "Livro de Teste"}


# ---------- Livro: gravar, exportar, migração ----------

def test_book_fields_patch_and_export(api):  # noqa: F811
    client, _, _ = api
    book = client.post("/api/books", json={"title": "Livro de Teste", "author": "Ana Fictícia"}).json()
    res = client.patch(f"/api/books/{book['id']}", json={
        "expected_version": book["version"], "isbn": "978-85-359-0846-6",
        "publisher": " Editora Fictícia ", "publication_place": "São Paulo"})
    assert res.status_code == 200, res.text
    book = res.json()
    assert (book["isbn"], book["publisher"], book["publication_place"]) == (ISBN13, "Editora Fictícia", "São Paulo")
    assert client.patch(f"/api/books/{book['id']}", json={"isbn": "123"}).status_code == 422
    cleared = client.patch(f"/api/books/{book['id']}", json={"isbn": ""}).json()
    assert cleared["isbn"] is None

    client.patch(f"/api/books/{book['id']}", json={"isbn": ISBN13})
    md = client.get(f"/api/books/{book['id']}/export", params={"format": "markdown"}).text
    assert f'isbn: "{ISBN13}"' in md and 'publisher: "Editora Fictícia"' in md
    txt = client.get(f"/api/books/{book['id']}/export", params={"format": "text"}).text
    assert "Publicação: São Paulo, Editora Fictícia" in txt and f"ISBN: {ISBN13}" in txt
    zipped = client.get("/api/account/export").content
    with zipfile.ZipFile(io.BytesIO(zipped)) as zf:
        exported = next(b for b in json.loads(zf.read("dados_acervo.json"))["books"] if b["id"] == book["id"])
    assert (exported["isbn"], exported["publisher"], exported["publication_place"]) == (ISBN13, "Editora Fictícia", "São Paulo")


def test_status_reports_switch(api, monkeypatch):  # noqa: F811
    client, _, _ = api
    assert client.get("/api/system/status").json()["isbn_lookup_enabled"] is True
    monkeypatch.setenv("LEITORUM_ISBN_LOOKUP", "off")
    assert client.get("/api/system/status").json()["isbn_lookup_enabled"] is False


def test_migration_0036_up_and_down(tmp_path):
    db = tmp_path / "m.db"
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "0035_inbox_capture_chapter")
    with sqlite3.connect(db) as conn:
        uid = conn.execute("SELECT id FROM users LIMIT 1").fetchone()[0]
        conn.execute("INSERT INTO books (user_id, title) VALUES (?, 'Livro de Teste')", (uid,))
        conn.commit()
    backups = db.parent / "backups"
    for old in backups.glob("caderno-pre-migracao-*.db"):
        old.unlink()
    command.upgrade(cfg, "0036_book_isbn_publisher")
    assert len(list(backups.glob("caderno-pre-migracao-*.db"))) == 1
    with sqlite3.connect(db) as conn:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(books)")}
        assert {"isbn", "publisher", "publication_place"} <= cols
        assert conn.execute("SELECT title, isbn FROM books").fetchone() == ("Livro de Teste", None)
    command.downgrade(cfg, "0035_inbox_capture_chapter")
    with sqlite3.connect(db) as conn:
        assert "isbn" not in {r[1] for r in conn.execute("PRAGMA table_info(books)")}
        assert conn.execute("PRAGMA quick_check").fetchone() == ("ok",)
