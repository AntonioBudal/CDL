"""F0.12.02 (spec 115): publicar estudos e a página pública /compartilhado/{id}. Só dados fictícios; tmp_path."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.models import User
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    USER_ALICE_ID,
    sharing_harness,
)

NOTE = "Nota pessoal secreta fictícia"
SOURCE = "Fichamento da fonte fictício e privado"
HIGHLIGHT_NOTE = "Comentário do destaque fictício"


def _anon(harness) -> TestClient:
    return TestClient(harness.client_alice.app)


def _study(client, title="Estudo de Teste", summary="Resumo **fictício** do estudo.", **extra):
    book = client.post("/api/books", json={
        "title": "Livro de Teste", "author": "Ana Fictícia", "year": 2020,
    }).json()
    ch = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    payload = {
        "chapter_id": ch["id"], "title": title, "summary": summary, "explanation": "Explicação fictícia.",
        "concepts": "", "references": "", "notes": NOTE, "source_response": SOURCE, **extra,
    }
    res = client.post("/api/studies", json=payload)
    assert res.status_code == 201, res.text
    return book, res.json()


def test_publish_unpublish_and_owner_only(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    _, study = _study(c)
    anon = _anon(sharing_harness)
    assert anon.get(f"/compartilhado/{study['id']}").status_code == 404, "não publicado"
    assert sharing_harness.client_bob.post(f"/api/studies/{study['id']}/publication").status_code == 404

    res = c.post(f"/api/studies/{study['id']}/publication")
    assert res.status_code == 200, res.text
    assert res.json()["path"] == f"/compartilhado/{study['id']}"
    assert c.get(f"/api/studies/{study['id']}").json()["published_at"] is not None
    listed = c.get("/api/studies/published").json()
    assert [(i["study_id"], i["available"]) for i in listed] == [(study["id"], True)]
    assert sharing_harness.client_bob.get("/api/studies/published").json() == []

    page = anon.get(f"/compartilhado/{study['id']}")
    assert page.status_code == 200
    assert "noindex" not in page.headers.get("x-robots-tag", "")
    assert page.headers["cache-control"] == "public, no-cache", "sempre revalida: despublicar vale na hora"
    assert "script-src 'self'" in page.headers["content-security-policy"]

    assert c.delete(f"/api/studies/{study['id']}/publication").status_code == 204
    assert anon.get(f"/compartilhado/{study['id']}").status_code == 404
    assert c.get("/api/studies/published").json() == []


def test_page_shows_only_the_allowed_fields(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    _, other = _study(c, title="Outro Estudo Publicado")
    _, hidden = _study(c, title="Estudo Não Publicado")
    _, study = _study(
        c, summary=f"Resumo com [[Outro Estudo Publicado|{other['id']}]] e [[Estudo Não Publicado|{hidden['id']}]] "
        "e <script>alert(1)</script>.",
    )
    c.post(f"/api/studies/{study['id']}/highlights", json={
        "section": "summary", "selected_text": "Resumo", "kind": "highlight", "note": HIGHLIGHT_NOTE,
    })
    c.post(f"/api/studies/{other['id']}/publication")
    c.post(f"/api/studies/{study['id']}/publication")

    html = _anon(sharing_harness).get(f"/compartilhado/{study['id']}").text
    assert "<h1>Estudo de Teste</h1>" in html and "<h2>Resumo</h2>" in html and "<h2>Explicação</h2>" in html
    assert "por Alice" in html or "por " in html
    assert "FICTÍCIA, Ana." in html and "<em>Livro de Teste</em>." in html and "2020" in html
    assert f'<a href="/compartilhado/{other["id"]}">Outro Estudo Publicado</a>' in html
    assert f"/compartilhado/{hidden['id']}" not in html and "Estudo Não Publicado" in html
    assert "<script>alert" not in html and "&lt;script&gt;" in html
    for secret in (NOTE, SOURCE, HIGHLIGHT_NOTE, "alice@", USER_ALICE_ID):
        assert secret not in html, secret
    assert '"@type": "Article"' in html and '<link rel="canonical"' in html and 'og:title' in html


def test_unavailable_cases_are_404(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    anon = _anon(sharing_harness)
    book, study = _study(c)
    c.post(f"/api/studies/{study['id']}/publication")
    assert anon.get(f"/compartilhado/{study['id']}").status_code == 200

    c.post(f"/api/studies/{study['id']}/trash")
    assert anon.get(f"/compartilhado/{study['id']}").status_code == 404
    c.post(f"/api/studies/{study['id']}/restore")
    assert anon.get(f"/compartilhado/{study['id']}").status_code == 200, "restaurar devolve a página"

    c.post(f"/api/books/{book['id']}/trash")
    assert anon.get(f"/compartilhado/{study['id']}").status_code == 404
    c.post(f"/api/books/{book['id']}/restore")
    assert anon.get(f"/compartilhado/{study['id']}").status_code == 200

    with sharing_harness.session_factory() as session:
        session.get(User, USER_ALICE_ID).status = "deactivated"
        session.commit()
    assert anon.get(f"/compartilhado/{study['id']}").status_code == 404
    assert anon.get("/compartilhado/999999").status_code == 404
    assert "noindex" in anon.get("/compartilhado/999999").headers.get("x-robots-tag", "")
