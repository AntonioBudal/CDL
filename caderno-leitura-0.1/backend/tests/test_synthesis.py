"""F0.11.11 (spec 113): cadernos de síntese com transclusão. Só dados fictícios; banco em tmp_path."""
from __future__ import annotations

import io
import zipfile

from app.services.synthesis_service import parse_embed, parse_embeds, split_body
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    sharing_harness,
)

BODY = """# Minha síntese

Texto meu sobre os dois livros.

![[Estudo A|5]]
![[Estudo A|5#resumo]]
  ![[destaque:9]]
Isto tem ![[Estudo A|5]] no meio.
![[Sem id]]
![[Estudo A|5#capitulo]]

```
![[Estudo A|5]]
```
![[Estudo A|5]]
"""


def test_parser():
    kinds = [(s.type, s.embed.key if s.embed else None) for s in split_body(BODY)]
    assert kinds == [
        ("text", None),
        ("embed", "study:5"),
        ("embed", "study:5#resumo"),
        ("embed", "highlight:9"),
        ("invalid", None),
        ("invalid", None),
        ("invalid", None),
        ("text", None),
        ("embed", "study:5"),
        ("text", None),
    ]
    assert [e.key for e in parse_embeds(BODY)] == ["study:5", "study:5#resumo", "highlight:9"]
    assert parse_embed("Título com | barra|12#Conceitos").key == "study:12#conceitos"
    assert parse_embed("destaque:0") is None and parse_embed("Título|0") is None


def _study(client, title="Estudo de Teste", summary="Resumo fictício.", book_title="Livro de Teste"):
    book = client.post("/api/books", json={"title": book_title, "author": "Ana Fictícia"}).json()
    ch = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    res = client.post("/api/studies", json={
        "chapter_id": ch["id"], "title": title, "summary": summary, "explanation": "Explicação fictícia.",
        "concepts": "", "references": "",
    })
    assert res.status_code == 201, res.text
    return res.json()


def test_crud_version_and_trash(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    created = c.post("/api/syntheses", json={"title": "Síntese de Teste", "body": "Texto."})
    assert created.status_code == 201, created.text
    nb = created.json()
    assert nb["version"] == 1
    upd = c.patch(f"/api/syntheses/{nb['id']}", json={"body": "Texto novo.", "version": 1})
    assert upd.status_code == 200 and upd.json()["version"] == 2
    assert c.patch(f"/api/syntheses/{nb['id']}", json={"body": "Velho.", "version": 1}).status_code == 409
    assert c.patch(f"/api/syntheses/{nb['id']}", json={"title": "  "}).status_code == 422

    assert sharing_harness.client_bob.get(f"/api/syntheses/{nb['id']}").status_code == 404
    assert sharing_harness.client_bob.get("/api/syntheses").json() == []
    assert [s["title"] for s in c.get("/api/syntheses").json()] == ["Síntese de Teste"]

    assert c.delete(f"/api/syntheses/{nb['id']}").status_code == 204
    assert c.get("/api/syntheses").json() == []
    assert c.get(f"/api/syntheses/{nb['id']}").status_code == 404
    assert [s["id"] for s in c.get("/api/syntheses/trash").json()] == [nb["id"]]
    assert c.delete(f"/api/syntheses/{nb['id']}/permanent").status_code == 204
    assert c.get("/api/syntheses/trash").json() == []

    other = c.post("/api/syntheses", json={"title": "Outra"}).json()
    c.delete(f"/api/syntheses/{other['id']}")
    assert c.post(f"/api/syntheses/{other['id']}/restore").status_code == 200
    assert [s["title"] for s in c.get("/api/syntheses").json()] == ["Outra"]
    assert c.delete(f"/api/syntheses/{other['id']}/permanent").status_code == 404, "só da lixeira"


def test_resolution_isolation_and_export(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    mine = _study(c)
    gone = _study(c, title="Estudo que vai para a lixeira", book_title="Outro Livro")
    bobs = _study(sharing_harness.client_bob, title="Estudo do Bob", summary="Segredo do Bob.", book_title="Livro do Bob")
    hl = c.post(f"/api/studies/{mine['id']}/highlights", json={
        "section": "summary", "selected_text": "Resumo fictício", "kind": "highlight", "note": "Nota fictícia.",
    }).json()
    body = "\n".join([
        "Introdução minha.",
        f"![[Estudo de Teste|{mine['id']}]]",
        f"![[Estudo de Teste|{mine['id']}#explicacao]]",
        f"![[destaque:{hl['id']}]]",
        f"![[Lixeira|{gone['id']}]]",
        f"![[Bob|{bobs['id']}]]",
        "![[Inexistente|999999]]",
    ])
    nb = c.post("/api/syntheses", json={"title": "Síntese Resolvida", "body": body}).json()
    assert c.post(f"/api/studies/{gone['id']}/trash").status_code == 200

    data = c.get(f"/api/syntheses/{nb['id']}/resolved").json()
    embeds = data["embeds"]
    whole = embeds[f"study:{mine['id']}"]
    assert whole["available"] and "#### Resumo" in whole["markdown"] and "Resumo fictício." in whole["markdown"]
    assert whole["book_title"] == "Livro de Teste" and whole["chapter_name"] == "Capítulo 1"
    section = embeds[f"study:{mine['id']}#explicacao"]
    assert section["markdown"] == "Explicação fictícia." and section["section_label"] == "Explicação"
    assert embeds[f"highlight:{hl['id']}"]["note"] == "Nota fictícia."
    for key in (f"study:{gone['id']}", f"study:{bobs['id']}", "study:999999"):
        assert embeds[key]["available"] is False and embeds[key]["title"] == "" and embeds[key]["book_title"] == ""
    assert "Segredo do Bob" not in str(data)

    # Editar o estudo muda o caderno na hora.
    c.patch(f"/api/studies/{mine['id']}", json={"explanation": "Explicação revista."})
    again = c.get(f"/api/syntheses/{nb['id']}/resolved").json()["embeds"]
    assert again[f"study:{mine['id']}#explicacao"]["markdown"] == "Explicação revista."

    exported = c.get(f"/api/syntheses/{nb['id']}/export")
    assert exported.status_code == 200 and exported.headers["content-type"].startswith("text/markdown")
    text = exported.content.decode("utf-8")
    assert text.startswith("# Síntese Resolvida") and "> Explicação revista." in text
    assert "— *Livro de Teste · Capítulo 1 · Estudo de Teste · Explicação*" in text
    assert "Segredo do Bob" not in text and "Trecho indisponível" in text
    assert "Introdução minha.\n\n> " in text, "trecho separado do parágrafo por linha em branco"
    assert "\n\n\n" not in text

    package = c.get("/api/account/export")
    assert package.status_code == 200
    with zipfile.ZipFile(io.BytesIO(package.content)) as zf:
        names = [n for n in zf.namelist() if n.startswith("sinteses/")]
        assert len(names) == 1
        assert "Explicação revista." in zf.read(names[0]).decode("utf-8")
