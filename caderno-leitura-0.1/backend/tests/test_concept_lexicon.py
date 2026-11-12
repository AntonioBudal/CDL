"""F0.11.06 (spec 108): léxico de conceitos derivado dos estudos. Só dados fictícios; banco em tmp_path."""
from __future__ import annotations

from app.services.concept_lexicon import concept_key, extract_concept_mentions, parse_concepts
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    sharing_harness,
)

CONCEITOS = """### Mímese
Imitação da natureza pela arte.

- **Catarse**: purificação das emoções.
**Hamartia** — erro trágico do herói.
Peripécia: reviravolta da ação.
Anagnórise – reconhecimento.
- só uma linha solta sem definição
**Negrito sem definição**
Uma frase muito longa que tem bem mais do que oito palavras antes dos dois pontos: não vira conceito.
https://exemplo.invalid/pagina: link
"""


def test_parse_concepts_accepts_known_formats_and_ignores_the_rest():
    pairs = parse_concepts(CONCEITOS)
    assert pairs == [
        ("Mímese", "Imitação da natureza pela arte."),
        ("Catarse", "purificação das emoções."),
        ("Hamartia", "erro trágico do herói."),
        ("Peripécia", "reviravolta da ação."),
        ("Anagnórise", "reconhecimento."),
    ]
    assert parse_concepts("") == [] and parse_concepts(None) == []


def test_concept_key_and_mentions():
    assert concept_key("Mímese") == concept_key("mimese") == "mimese"
    assert concept_key("Razão Prática!") == "razao-pratica"
    found = extract_concept_mentions("Antes [[conceito: Mímese ]] depois [[Outro Estudo]] e [[conceito:]].")
    assert [term for term, _ in found] == ["Mímese"]
    assert "Antes" in found[0][1]
    assert "[[" not in found[0][1] and "Mímese" in found[0][1] and "Outro Estudo" in found[0][1], "trecho legível"


def _book(client, title="Livro de Teste", author="Ana Fictícia"):
    return client.post("/api/books", json={"title": title, "author": author}).json()


def _study(client, book, title, concepts="", summary="", chapter="Capítulo 1"):
    ch = client.post(f"/api/books/{book['id']}/chapters", json={"name": chapter}).json()
    res = client.post("/api/studies", json={
        "chapter_id": ch["id"], "title": title, "summary": summary or "Resumo fictício.",
        "explanation": "", "concepts": concepts, "references": "",
    })
    assert res.status_code == 201, res.text
    return res.json()


def test_lexicon_api_aggregates_merges_and_isolates(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    b1 = _book(c, "Livro A")
    b2 = _book(c, "Livro B")
    _study(c, b1, "Estudo 1", concepts="**Mímese**: imitação.\n- **Catarse**: purificação.")
    s2 = _study(c, b2, "Estudo 2", concepts="mimese: outra definição.\nConceitos: plural.\nConceito: singular.",
                summary="Ver [[conceito:Mímese]] e [[conceito:Tragédia]].")
    # Outro leitor com o mesmo termo não aparece para Alice
    _study(sharing_harness.client_bob, _book(sharing_harness.client_bob, "Livro do Bob"), "Estudo do Bob",
           concepts="**Mímese**: definição do Bob.")

    data = c.get("/api/concepts").json()
    by_key = {item["key"]: item for item in data["items"]}
    assert set(by_key) == {"catarse", "conceito", "mimese", "tragedia"}, "plural fundido; Bob fora"
    assert by_key["mimese"]["definitions"] == 2 and by_key["mimese"]["books"] == 2 and by_key["mimese"]["mentions"] == 1
    assert by_key["conceito"]["definitions"] == 2
    assert by_key["tragedia"]["definitions"] == 0 and by_key["tragedia"]["mentions"] == 1
    assert [i["key"] for i in data["items"]] == sorted(by_key)

    detail = c.get("/api/concepts/Mímese").json()
    assert detail["term"] in {"Mímese", "mimese"}
    assert {d["text"] for d in detail["definitions"]} == {"imitação.", "outra definição."}
    assert {d["book_title"] for d in detail["definitions"]} == {"Livro A", "Livro B"}
    assert detail["mentions"][0]["study_id"] == s2["id"]
    assert all("Bob" not in d["text"] for d in detail["definitions"])

    assert c.get("/api/concepts", params={"q": "cata"}).json()["total"] == 1
    assert [x["key"] for x in c.get("/api/concepts/candidates", params={"q": "mim"}).json()] == ["mimese"]
    assert c.get("/api/concepts/inexistente").status_code == 404
    page = c.get("/api/concepts", params={"per_page": 2, "page": 2}).json()
    assert page["total"] == 4 and len(page["items"]) == 2


def test_trashed_study_leaves_the_lexicon(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    study = _study(c, _book(c), "Estudo Lixeira", concepts="**Kátharsis**: termo grego.")
    assert c.get("/api/concepts/katharsis").status_code == 200
    assert c.post(f"/api/studies/{study['id']}/trash").status_code in (200, 204)
    assert c.get("/api/concepts/katharsis").status_code == 404
    assert c.post(f"/api/studies/{study['id']}/restore").status_code in (200, 204)
    assert c.get("/api/concepts/katharsis").status_code == 200
