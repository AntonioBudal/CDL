"""F0.10.07 (spec 100): leituras e estudos em comum entre amigos. Só dados fictícios, banco em tmp_path."""
from __future__ import annotations

from datetime import datetime, timezone

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.services import in_common_service
from app.services.in_common_service import first_author_surname_key, normalize_title_key
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture reaproveitada)
    USER_ALICE_ID,
    USER_BOB_ID,
    sharing_harness,
)


def _book(session, owner, title, author=None, visibility="private", deleted=False):
    book = Book(user_id=owner, title=title, author=author, visibility=visibility)
    if deleted:
        book.deleted_at = datetime.now(timezone.utc)
    session.add(book)
    session.flush()
    return book


def _study(session, owner, book, title, visibility="inherit", deleted=False, chapter_name="Capítulo 1"):
    chapter = Chapter(book_id=book.id, name=chapter_name)
    session.add(chapter)
    session.flush()
    study = Study(user_id=owner, chapter_id=chapter.id, title=title, visibility=visibility, summary="Resumo fictício.")
    if deleted:
        study.deleted_at = datetime.now(timezone.utc)
    session.add(study)
    session.flush()
    return study


# ---------- Normalização ----------

def test_normalize_title_key_ignores_accents_case_punctuation_and_subtitle():
    assert normalize_title_key("Dom Casmurro: romance") == "dom casmurro"
    assert normalize_title_key("  DOM   casmurro!! ") == "dom casmurro"
    assert normalize_title_key("Ética a Nicômaco") == normalize_title_key("etica a nicomaco")
    assert normalize_title_key("") == ""


def test_first_author_surname_key():
    assert first_author_surname_key("Machado de Assis") == "assis"
    assert first_author_surname_key("Assis, Machado de") == "assis"
    assert first_author_surname_key("Ana Fictícia; Bia Teste") == "ficticia"
    assert first_author_surname_key("Carlos Teste Júnior") == "teste junior"
    assert first_author_surname_key(None) == ""


# ---------- Rota ----------

def test_in_common_between_friends(sharing_harness):
    with sharing_harness.session_factory() as s:
        # Alice (visitante) tem três livros.
        a1 = _book(s, USER_ALICE_ID, "dom casmurro", "Machado de Assis")
        _book(s, USER_ALICE_ID, "Poemas", "Autora Fictícia")
        a3 = _book(s, USER_ALICE_ID, "Livro de Teste")
        # Bob (amigo) tem livros legíveis e privados.
        b1 = _book(s, USER_BOB_ID, "Dom Casmurro: romance", "Assis, Machado de", visibility="friends")
        _book(s, USER_BOB_ID, "Poemas", "Outro Autor", visibility="public")  # autor diferente: não casa
        b3 = _book(s, USER_BOB_ID, "LIVRO DE TESTE", visibility="public")  # sem autor: casa pelo título
        _book(s, USER_BOB_ID, "Livro de Teste", "X", visibility="friends", deleted=True)  # excluído
        _study(s, USER_BOB_ID, b1, "Estudo legível 1")
        _study(s, USER_BOB_ID, b1, "Estudo privado", visibility="private")
        _study(s, USER_BOB_ID, b1, "Estudo na lixeira", deleted=True)
        _study(s, USER_BOB_ID, b3, "Estudo público", visibility="public", chapter_name="Capítulo 2")
        s.commit()
        ids = (a1.id, a3.id, b1.id, b3.id)

    res = sharing_harness.client_alice.get("/api/users/bob/in-common")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["is_friend"] is True
    assert data["books_truncated"] is False
    by_friend_id = {b["friend_book_id"]: b for b in data["books"]}
    assert set(by_friend_id) == {ids[2], ids[3]}
    dom = by_friend_id[ids[2]]
    assert dom["my_book_id"] == ids[0]
    assert dom["friend_studies_total"] == 1
    assert [st["title"] for st in dom["friend_studies"]] == ["Estudo legível 1"]
    assert dom["friend_studies"][0]["book_id"] == ids[2]
    teste = by_friend_id[ids[3]]
    assert teste["my_book_id"] == ids[1]
    assert teste["friend_studies"][0]["chapter_name"] == "Capítulo 2"
    assert data["shared_with_me_total"] == 2


def test_private_books_of_friend_never_appear(sharing_harness):
    with sharing_harness.session_factory() as s:
        _book(s, USER_ALICE_ID, "Livro Secreto")
        _book(s, USER_BOB_ID, "Livro Secreto", visibility="private")
        s.commit()
    data = sharing_harness.client_alice.get("/api/users/bob/in-common").json()
    assert data["books"] == []


def test_not_friend_gets_flag_without_lists(sharing_harness):
    with sharing_harness.session_factory() as s:
        _book(s, "33333333-3333-3333-3333-333333333333", "Livro Público", visibility="public")
        _book(s, USER_ALICE_ID, "Livro Público")
        s.commit()
    res = sharing_harness.client_alice.get("/api/users/carlos/in-common")
    assert res.status_code == 200
    assert res.json() == {"is_friend": False, "books": [], "books_truncated": False, "shared_with_me_total": 0}


def test_blocked_self_and_unknown_are_404(sharing_harness):
    c = sharing_harness.client_alice
    assert c.get("/api/users/daniel/in-common").status_code == 404
    assert sharing_harness.client_daniel.get("/api/users/alice/in-common").status_code == 404
    assert c.get("/api/users/alice/in-common").status_code == 404
    assert c.get("/api/users/ninguem/in-common").status_code == 404


def test_books_limit_is_truncated(sharing_harness, monkeypatch):
    monkeypatch.setattr(in_common_service, "MAX_BOOKS", 2)
    with sharing_harness.session_factory() as s:
        for i in range(3):
            _book(s, USER_ALICE_ID, f"Livro {i}")
            _book(s, USER_BOB_ID, f"Livro {i}", visibility="friends")
        s.commit()
    data = sharing_harness.client_alice.get("/api/users/bob/in-common").json()
    assert len(data["books"]) == 2
    assert data["books_truncated"] is True


def test_studies_per_book_limited_to_five_with_total(sharing_harness):
    with sharing_harness.session_factory() as s:
        _book(s, USER_ALICE_ID, "Livro Cheio")
        b = _book(s, USER_BOB_ID, "Livro Cheio", visibility="friends")
        for i in range(7):
            _study(s, USER_BOB_ID, b, f"Estudo {i}", chapter_name=f"Cap {i}")
        s.commit()
    book = sharing_harness.client_alice.get("/api/users/bob/in-common").json()["books"][0]
    assert len(book["friend_studies"]) == 5
    assert book["friend_studies_total"] == 7
