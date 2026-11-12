"""F0.11.07 (spec 109): fontes do validador de paráfrase. Só dados fictícios; banco em tmp_path."""
from __future__ import annotations

from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    sharing_harness,
)

FICHAMENTO = "Fichamento fictício que nunca entra como fonte."


def _setup(client):
    book = client.post("/api/books", json={"title": "Livro de Teste", "author": "Ana Fictícia"}).json()
    ch = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    other = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 2"}).json()
    studies = []
    for title, chapter in (("Estudo de Teste", ch), ("Outro Estudo", other)):
        res = client.post("/api/studies", json={
            "chapter_id": chapter["id"], "title": title, "summary": f"Resumo fictício de {title}.",
            "explanation": "", "concepts": "", "references": "", "source_response": FICHAMENTO,
        })
        assert res.status_code == 201, res.text
        studies.append(res.json())
    return book, ch, other, studies[0], studies[1]


def _quote(client, study, text, kind="quote"):
    r = client.post(f"/api/studies/{study['id']}/highlights", json={"section": "summary", "selected_text": text, "kind": kind})
    assert r.status_code == 201, r.text


def test_sources_are_book_text_and_own_quotes_are_declared(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book, ch, other, study, other_study = _setup(c)
    _quote(c, study, "Resumo fictício")
    _quote(c, study, "Estudo de Teste", kind="highlight")
    _quote(c, other_study, "Outro Estudo")
    assert c.post("/api/inbox", json={"content": "Trecho capturado do capítulo um.", "chapter_id": ch["id"]}).status_code == 201
    assert c.post("/api/inbox", json={"content": "Trecho de outro capítulo.", "chapter_id": other["id"]}).status_code == 201
    assert c.post("/api/inbox", json={"content": "Captura solta, sem livro."}).status_code == 201
    other_book = c.post("/api/books", json={"title": "Outro Livro", "author": "Bia Fictícia"}).json()
    assert c.post("/api/inbox", json={"content": "Captura de outro livro.", "book_id": other_book["id"]}).status_code == 201

    data = c.get(f"/api/studies/{study['id']}/paraphrase-sources").json()
    assert [(s["kind"], s["label"], s["text"]) for s in data["sources"]] == [
        ("capture", "Captura deste capítulo", "Trecho capturado do capítulo um."),
        ("capture", "Captura deste livro", "Trecho de outro capítulo."),
        ("quote", "Citação literal em «Outro Estudo»", "Outro Estudo"),
    ]
    assert data["declared_quotes"] == [{"section": "summary", "text": "Resumo fictício"}]
    assert FICHAMENTO not in str(data), "o fichamento não é fonte"

    chapter = c.get(f"/api/chapters/{ch['id']}/paraphrase-sources").json()
    assert [s["text"] for s in chapter["sources"]] == [
        "Trecho capturado do capítulo um.", "Trecho de outro capítulo.", "Resumo fictício", "Outro Estudo",
    ]
    assert chapter["declared_quotes"] == []


def test_sources_are_private_and_hidden_in_trash(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    bob = sharing_harness.client_bob
    _, ch, _, study, other_study = _setup(c)
    _quote(c, other_study, "Outro Estudo")
    assert bob.get(f"/api/studies/{study['id']}/paraphrase-sources").status_code == 404
    assert bob.get(f"/api/chapters/{ch['id']}/paraphrase-sources").status_code == 404
    assert c.post(f"/api/studies/{other_study['id']}/trash").status_code == 200
    assert c.get(f"/api/studies/{study['id']}/paraphrase-sources").json()["sources"] == [], "estudo na lixeira não é fonte"
    assert c.post(f"/api/studies/{study['id']}/trash").status_code == 200
    assert c.get(f"/api/studies/{study['id']}/paraphrase-sources").status_code == 404


def test_study_without_book_text_returns_empty_lists(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    _, _, _, study, _ = _setup(c)
    assert c.get(f"/api/studies/{study['id']}/paraphrase-sources").json() == {"sources": [], "declared_quotes": []}
