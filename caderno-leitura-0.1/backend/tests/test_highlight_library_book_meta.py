"""F0.10.05 (spec 098): a biblioteca de destaques devolve ano e subtítulo do livro para a cópia ABNT."""
from tests.test_highlights_library import api, make_client  # noqa: F401  (fixture reaproveitada)


def _book_with_highlight(client, **book_fields):
    res_b = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autora Fictícia", **book_fields})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]
    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": res_c.json()["id"],
            "title": "Estudo de Teste",
            "summary": "Trecho fictício para citação.",
            "explanation": "",
            "concepts": "",
            "references": "",
        },
    )
    assert res_s.status_code == 201
    res_h = client.post(
        f"/api/studies/{res_s.json()['id']}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 6,
            "selected_text": "Trecho",
            "color": "yellow",
            "kind": "highlight",
        },
    )
    assert res_h.status_code == 201
    return book_id


def test_library_item_has_book_year_and_subtitle(api):  # noqa: F811
    client, _, _ = api
    _book_with_highlight(client, year=1997, subtitle="Um Subtítulo")
    item = client.get("/api/highlights/library").json()["items"][0]
    assert item["book_year"] == 1997
    assert item["book_subtitle"] == "Um Subtítulo"


def test_library_item_without_year_or_subtitle(api):  # noqa: F811
    client, _, _ = api
    _book_with_highlight(client)
    item = client.get("/api/highlights/library").json()["items"][0]
    assert item["book_year"] is None
    assert item["book_subtitle"] == ""
