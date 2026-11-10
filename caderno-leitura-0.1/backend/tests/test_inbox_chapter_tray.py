"""F0.11.02 (spec 104): capítulo da captura e bandeja por capítulo. Só dados fictícios; bancos em tmp_path."""
from __future__ import annotations

import sqlite3

from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.models import Book, Chapter, User
from tests.test_inbox import api  # noqa: F401  (fixture reaproveitada: banco migrado com upgrade head)

OTHER_USER = "77777777-7777-7777-7777-777777777777"


def _book_with_chapters(client, title="Livro de Teste", names=("Capítulo 1", "Capítulo 2")):
    book = client.post("/api/books", json={"title": title}).json()
    chapters = [client.post(f"/api/books/{book['id']}/chapters", json={"name": n}).json() for n in names]
    return book, chapters


def _capture(client, **fields):
    return client.post("/api/inbox", json={"content": "Ideia fictícia.", **fields})


# ---------- Migração ----------

def test_migration_0035_up_and_down(tmp_path):
    db = tmp_path / "m.db"
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "0034_book_reading_state")
    with sqlite3.connect(db) as conn:
        uid = conn.execute("SELECT id FROM users LIMIT 1").fetchone()[0]
        conn.execute("INSERT INTO inbox_captures (user_id, content, status) VALUES (?, 'Captura fictícia', 'inbox')", (uid,))
        conn.commit()
    backups = db.parent / "backups"
    for old in backups.glob("caderno-pre-migracao-*.db"):
        old.unlink()
    command.upgrade(cfg, "0035_inbox_capture_chapter")
    assert len(list(backups.glob("caderno-pre-migracao-*.db"))) == 1, "snapshot antes da 0035"
    with sqlite3.connect(db) as conn:
        assert "chapter_id" in {r[1] for r in conn.execute("PRAGMA table_info(inbox_captures)")}
        assert conn.execute("SELECT content, chapter_id FROM inbox_captures").fetchone() == ("Captura fictícia", None)
        fks = [r for r in conn.execute("PRAGMA foreign_key_list(inbox_captures)") if r[2] == "chapters"]
        assert fks and fks[0][6] == "SET NULL"
    command.downgrade(cfg, "0034_book_reading_state")
    with sqlite3.connect(db) as conn:
        assert "chapter_id" not in {r[1] for r in conn.execute("PRAGMA table_info(inbox_captures)")}
        assert conn.execute("SELECT content FROM inbox_captures").fetchone() == ("Captura fictícia",)
        assert conn.execute("PRAGMA quick_check").fetchone() == ("ok",)


# ---------- Criar e editar ----------

def test_capture_with_chapter_fills_book(api):  # noqa: F811
    client, _, _ = api
    book, (c1, _c2) = _book_with_chapters(client)
    res = _capture(client, chapter_id=c1["id"])
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["chapter_id"] == c1["id"]
    assert data["chapter_name"] == "Capítulo 1"
    assert data["book_id"] == book["id"]
    assert data["book_title"] == "Livro de Teste"


def test_chapter_from_other_book_or_reader_is_404(api):  # noqa: F811
    client, engine, _ = api
    book_a, (a1, _) = _book_with_chapters(client, "Livro A")
    book_b, _ = _book_with_chapters(client, "Livro B")
    assert _capture(client, book_id=book_b["id"], chapter_id=a1["id"]).status_code == 404

    with Session(engine) as s:
        s.add(User(id=OTHER_USER, username="outra-leitora", display_name="Outra Leitora", role="user", status="ativo"))
        s.flush()
        other_book = Book(user_id=OTHER_USER, title="Livro de Outra Pessoa")
        s.add(other_book)
        s.flush()
        other_chapter = Chapter(book_id=other_book.id, name="Capítulo Alheio")
        s.add(other_chapter)
        s.commit()
        other_chapter_id = other_chapter.id
    res = _capture(client, chapter_id=other_chapter_id)
    assert res.status_code == 404
    assert res.json()["detail"] == "Capítulo associado não encontrado."


def test_patch_chapter_rules(api):  # noqa: F811
    client, _, _ = api
    book_a, (a1, a2) = _book_with_chapters(client, "Livro A")
    book_b, (b1,) = _book_with_chapters(client, "Livro B", names=("Capítulo B1",))
    cap = _capture(client, chapter_id=a1["id"]).json()

    # trocar de capítulo dentro do livro
    cap = client.patch(f"/api/inbox/{cap['id']}", json={"chapter_id": a2["id"]}).json()
    assert (cap["book_id"], cap["chapter_id"]) == (book_a["id"], a2["id"])

    # capítulo de outro livro leva o livro junto
    cap = client.patch(f"/api/inbox/{cap['id']}", json={"chapter_id": b1["id"]}).json()
    assert (cap["book_id"], cap["chapter_id"]) == (book_b["id"], b1["id"])

    # trocar só o livro limpa o capítulo
    cap = client.patch(f"/api/inbox/{cap['id']}", json={"book_id": book_a["id"]}).json()
    assert (cap["book_id"], cap["chapter_id"]) == (book_a["id"], None)

    # null explícito limpa o capítulo; ausente não muda
    cap = client.patch(f"/api/inbox/{cap['id']}", json={"chapter_id": a1["id"]}).json()
    cap = client.patch(f"/api/inbox/{cap['id']}", json={"content": "Ideia editada."}).json()
    assert cap["chapter_id"] == a1["id"]
    cap = client.patch(f"/api/inbox/{cap['id']}", json={"chapter_id": None}).json()
    assert (cap["book_id"], cap["chapter_id"]) == (book_a["id"], None)

    # livro e capítulo incoerentes
    res = client.patch(f"/api/inbox/{cap['id']}", json={"book_id": book_b["id"], "chapter_id": a1["id"]})
    assert res.status_code == 404


# ---------- Bandeja ----------

def test_list_by_chapter_and_book_tray_counts(api):  # noqa: F811
    client, _, _ = api
    book, (c1, c2) = _book_with_chapters(client)
    other, (o1,) = _book_with_chapters(client, "Outro Livro", names=("Capítulo O1",))
    first = _capture(client, chapter_id=c1["id"]).json()
    _capture(client, chapter_id=c1["id"])
    _capture(client, chapter_id=c2["id"])
    _capture(client, book_id=book["id"])
    _capture(client, chapter_id=o1["id"])
    archived = _capture(client, chapter_id=c2["id"]).json()
    client.patch(f"/api/inbox/{archived['id']}", json={"status": "archived"})

    listed = client.get("/api/inbox", params={"chapter_id": c1["id"]}).json()
    assert {c["chapter_id"] for c in listed} == {c1["id"]} and len(listed) == 2

    tray = client.get("/api/inbox/book-tray", params={"book_id": book["id"]})
    assert tray.status_code == 200
    assert tray.json() == {"by_chapter": {str(c1["id"]): 2, str(c2["id"]): 1}, "without_chapter": 1}

    client.patch(f"/api/inbox/{first['id']}", json={"status": "archived"})
    assert client.get("/api/inbox/book-tray", params={"book_id": book["id"]}).json()["by_chapter"][str(c1["id"])] == 1


def test_deleting_chapter_keeps_capture_with_book(api):  # noqa: F811
    client, _, _ = api
    book, (c1, _c2) = _book_with_chapters(client)
    cap = _capture(client, chapter_id=c1["id"]).json()
    res = client.delete(f"/api/books/{book['id']}/chapters/{c1['id']}")
    assert res.status_code in (200, 204), res.text
    again = client.get(f"/api/inbox/{cap['id']}").json()
    assert (again["book_id"], again["chapter_id"]) == (book["id"], None)
    assert client.get("/api/inbox/book-tray", params={"book_id": book["id"]}).json() == {"by_chapter": {}, "without_chapter": 1}
