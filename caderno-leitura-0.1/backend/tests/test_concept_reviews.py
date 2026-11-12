"""F0.11.08 (spec 110): cartões de conceito e conceitos frágeis. Só dados fictícios; banco em tmp_path."""
from __future__ import annotations

from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    sharing_harness,
)


def _study(client, book_title, concepts, chapter="Capítulo 1"):
    book = client.post("/api/books", json={"title": book_title, "author": "Ana Fictícia"}).json()
    ch = client.post(f"/api/books/{book['id']}/chapters", json={"name": chapter}).json()
    res = client.post("/api/studies", json={
        "chapter_id": ch["id"], "title": f"Estudo de {book_title}", "summary": "Resumo fictício com trecho.",
        "explanation": "", "concepts": concepts, "references": "",
    })
    assert res.status_code == 201, res.text
    return book, ch, res.json()


def test_concept_cards_list_filter_and_record(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    b1, ch1, _ = _study(c, "Livro A", "- **Mímese**: imitação fictícia.\n- **Catarse**: purificação fictícia.")
    _study(c, "Livro B", "Hamartia: erro fictício.\nmimese: outra definição fictícia.")
    _study(sharing_harness.client_bob, "Livro do Bob", "**Peripécia**: do Bob.")

    cards = c.get("/api/review/items", params={"kind": "concept", "limit": 50}).json()
    assert sorted(card["concept_key"] for card in cards) == ["catarse", "hamartia", "mimese"]
    mimese = next(card for card in cards if card["concept_key"] == "mimese")
    assert mimese["kind"] == "concept" and mimese["question_text"].startswith("O que é ")
    assert {d["text"] for d in mimese["definitions"]} == {"imitação fictícia.", "outra definição fictícia."}
    assert "imitação fictícia." in mimese["expected_answer"]

    by_book = c.get("/api/review/items", params={"kind": "concept", "book_id": b1["id"]}).json()
    assert sorted(card["concept_key"] for card in by_book) == ["catarse", "mimese"]
    by_book_mimese = next(card for card in by_book if card["concept_key"] == "mimese")
    assert [d["text"] for d in by_book_mimese["definitions"]] == ["imitação fictícia."]
    assert len(c.get("/api/review/items", params={"kind": "concept", "chapter_id": ch1["id"]}).json()) == 2

    rec = c.post("/api/review/concepts/Mímese/record", json={"rating": "hard"})
    assert rec.status_code == 200, rec.text
    assert rec.json()["difficulty_weight"] == 0.75 and rec.json()["review_count"] == 1
    assert c.post("/api/review/concepts/mimese/record", json={"rating": "hard"}).json()["review_count"] == 2
    assert c.post("/api/review/concepts/inexistente/record", json={"rating": "hard"}).status_code == 404
    assert sharing_harness.client_bob.post("/api/review/concepts/mimese/record", json={"rating": "easy"}).status_code == 404

    cards = c.get("/api/review/items", params={"kind": "concept", "limit": 50}).json()
    assert cards[-1]["concept_key"] == "mimese", "recém-avaliado vai para o fim; os novos vêm antes"
    stats = c.get("/api/review/stats", params={"kind": "concept"}).json()
    assert stats["buckets"] == {"new": 2, "hard": 1, "medium": 0, "easy": 0}
    assert (stats["total_eligible"], stats["reviewed_today"], stats["pending_review"]) == (3, 1, 2)
    hard = c.get("/api/review/items", params={"kind": "concept", "bucket": "hard"}).json()
    assert [card["concept_key"] for card in hard] == ["mimese"]


def test_fragile_concepts_by_card_and_by_questions(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    _study(c, "Livro A", "- **Mímese**: imitação fictícia.\n- **Catarse**: purificação fictícia.")
    _, _, study_b = _study(c, "Livro B", "Hamartia: erro fictício.")
    assert c.get("/api/review/fragile-concepts").json() == []

    for _ in range(2):
        c.post("/api/review/concepts/mimese/record", json={"rating": "hard"})
    c.post("/api/review/concepts/catarse/record", json={"rating": "easy"})
    q = c.post(f"/api/studies/{study_b['id']}/highlights", json={
        "section": "summary", "selected_text": "trecho", "kind": "question", "note": "Pergunta?",
    }).json()
    c.post(f"/api/review/items/{q['id']}/record", json={"rating": "hard"})

    fragile = c.get("/api/review/fragile-concepts").json()
    assert [(f["key"], f["reason"]) for f in fragile] == [("mimese", "card"), ("hamartia", "questions")]
    assert fragile[0]["weight"] == 0.875

    practice = c.get("/api/review/items", params={"kind": "concept", "fragile": "true", "limit": 50}).json()
    assert sorted(card["concept_key"] for card in practice) == ["hamartia", "mimese"]
    lexicon = {i["key"]: i["fragile"] for i in c.get("/api/concepts").json()["items"]}
    assert lexicon == {"catarse": False, "hamartia": True, "mimese": True}
    assert c.get("/api/concepts/mimese").json()["fragile"] is True
    assert c.get("/api/concepts/catarse").json()["fragile"] is False
