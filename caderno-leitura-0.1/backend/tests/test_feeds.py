"""F0.12.04 (spec 117): feeds RSS, Atom e JSON dos estudos publicados. Só dados fictícios; tmp_path."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    USER_ALICE_ID,
    sharing_harness,
)

ATOM = "{http://www.w3.org/2005/Atom}"
NOTE = "Nota pessoal secreta fictícia"
SOURCE = "Fichamento privado fictício"


def _anon(harness) -> TestClient:
    return TestClient(harness.client_alice.app)


def _published(client, title, summary="Resumo fictício."):
    book = client.post("/api/books", json={"title": f"Livro de {title}", "author": "Ana Fictícia"}).json()
    ch = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    study = client.post("/api/studies", json={
        "chapter_id": ch["id"], "title": title, "summary": summary, "explanation": "", "concepts": "", "references": "",
        "notes": NOTE, "source_response": SOURCE,
    }).json()
    assert client.post(f"/api/studies/{study['id']}/publication").status_code == 200
    return book, study


def test_empty_feeds_are_valid(sharing_harness):  # noqa: F811
    anon = _anon(sharing_harness)
    rss = anon.get("/feed.xml")
    assert rss.status_code == 200 and rss.headers["content-type"].startswith("application/rss+xml")
    root = ET.fromstring(rss.content)
    assert root.tag == "rss" and root.find("channel/title").text == "Leitorum — estudos publicados"
    assert root.findall("channel/item") == []
    atom = ET.fromstring(anon.get("/feed.atom").content)
    assert atom.tag == f"{ATOM}feed" and atom.find(f"{ATOM}id") is not None and atom.find(f"{ATOM}updated") is not None
    data = anon.get("/feed.json").json()
    assert data["version"] == "https://jsonfeed.org/version/1.1" and data["items"] == []


def test_feeds_list_only_published_and_escape(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    _published(c, "Primeiro Estudo")
    book, second = _published(c, "Segundo <Estudo> & ]]> fim", summary="Texto com <script>alert(1)</script> & ]]> fim.")
    hidden_book = c.post("/api/books", json={"title": "Livro Não Publicado"}).json()
    ch = c.post(f"/api/books/{hidden_book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    c.post("/api/studies", json={"chapter_id": ch["id"], "title": "Estudo Não Publicado", "summary": "Resumo.",
                                 "explanation": "", "concepts": "", "references": ""})
    anon = _anon(sharing_harness)

    rss = anon.get("/feed.xml").content
    root = ET.fromstring(rss)  # bem formado, mesmo com <, & e ]]>
    titles = [i.find("title").text for i in root.findall("channel/item")]
    assert titles == ["Segundo <Estudo> & ]]> fim", "Primeiro Estudo"], "mais recente primeiro; só publicados"
    item = root.find("channel/item")
    assert item.find("link").text.endswith(f"/compartilhado/{second['id']}")
    assert item.find("{http://purl.org/dc/elements/1.1/}creator").text
    content = item.find("{http://purl.org/rss/1.0/modules/content/}encoded").text
    assert "&lt;script&gt;" in content and "<script>" not in content

    atom = ET.fromstring(anon.get("/feed.atom").content)
    entries = atom.findall(f"{ATOM}entry")
    assert len(entries) == 2
    for tag in ("id", "title", "updated", "published"):
        assert entries[0].find(f"{ATOM}{tag}") is not None, tag
    assert entries[0].find(f"{ATOM}link").get("href").endswith(f"/compartilhado/{second['id']}")
    assert entries[0].find(f"{ATOM}content").get("type") == "html"

    data = anon.get("/feed.json").json()
    assert [i["title"] for i in data["items"]] == titles
    assert data["items"][0]["content_html"].count("<section>") == 1
    for body in (rss.decode("utf-8"), anon.get("/feed.atom").text, json.dumps(data, ensure_ascii=False)):
        for secret in (NOTE, SOURCE, USER_ALICE_ID, "Estudo Não Publicado"):
            assert secret not in body, secret

    c.delete(f"/api/studies/{second['id']}/publication")
    assert [i["title"] for i in anon.get("/feed.json").json()["items"]] == ["Primeiro Estudo"]
    c.post(f"/api/books/{book['id']}/trash")
    assert len(anon.get("/feed.json").json()["items"]) == 1


def test_etag_and_discovery(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    _, study = _published(c, "Estudo do ETag")
    anon = _anon(sharing_harness)
    first = anon.get("/feed.atom")
    etag = first.headers["etag"]
    assert first.headers["cache-control"] == "public, no-cache"
    again = anon.get("/feed.atom", headers={"If-None-Match": etag})
    assert again.status_code == 304 and again.content == b""
    c.patch(f"/api/studies/{study['id']}", json={"summary": "Resumo mudado."})
    assert anon.get("/feed.atom", headers={"If-None-Match": etag}).status_code == 200, "mudou, ETag novo"

    page = anon.get(f"/compartilhado/{study['id']}").text
    for feed_type, href in (("application/rss+xml", "/feed.xml"), ("application/atom+xml", "/feed.atom"),
                            ("application/feed+json", "/feed.json")):
        assert f'type="{feed_type}"' in page and f'href="{href}"' in page
    robots = anon.get("/robots.txt").text
    assert "Allow: /feed.xml" in robots and "Allow: /feed.json" in robots
