"""F0.12.05 (spec 118): exportar o livro em JSON Canvas 1.0. Só dados fictícios; tmp_path."""
from __future__ import annotations

import json

from app.services.json_canvas_export import canvas_color, estimate_height
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    sharing_harness,
)

NOTE = "Nota pessoal secreta fictícia"
SOURCE = "Fichamento privado fictício"


def _study(client, chapter_id, title, summary="Resumo fictício."):
    res = client.post("/api/studies", json={
        "chapter_id": chapter_id, "title": title, "summary": summary, "explanation": "", "concepts": "",
        "references": "", "notes": NOTE, "source_response": SOURCE,
    })
    assert res.status_code == 201, res.text
    return res.json()


def _export(client, book_id):
    res = client.get(f"/api/books/{book_id}/canvas/export")
    assert res.status_code == 200, res.text
    assert res.headers["content-type"].startswith("application/json")
    assert ".canvas" in res.headers["content-disposition"]
    return json.loads(res.content)


def _valid(canvas):
    assert set(canvas) == {"nodes", "edges"}
    ids = [n["id"] for n in canvas["nodes"]]
    assert len(ids) == len(set(ids)), "ids únicos"
    for node in canvas["nodes"]:
        assert node["type"] in {"text", "file", "link", "group"}
        for key in ("x", "y", "width", "height"):
            assert isinstance(node[key], int), (node["id"], key)
        if node["type"] == "text":
            assert isinstance(node["text"], str)
    for edge in canvas["edges"]:
        assert edge["fromNode"] in ids and edge["toNode"] in ids, "aresta aponta para nó existente"
        assert edge["id"] not in ids


def _overlap(a, b):
    return not (a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"]
                or a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"])


def test_helpers():
    assert canvas_color("amber") == "2" and canvas_color("emerald") == "4" and canvas_color("violet") == "6"
    assert canvas_color("#AABBCC") == "#aabbcc" and canvas_color("neutral") is None and canvas_color(None) is None
    assert estimate_height("curto") == 120 and estimate_height("x" * 10_000) == 600


def test_export_saved_positions_frames_relations_and_auto_layout(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book = c.post("/api/books", json={"title": "Livro de Teste", "author": "Ana Fictícia"}).json()
    ch1 = c.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    ch2 = c.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 2"}).json()
    placed = _study(c, ch1["id"], "Estudo Posicionado")
    a = _study(c, ch1["id"], "Estudo A", summary='Texto com "aspas", \\ barra e\nquebra de linha 📚.')
    b = _study(c, ch2["id"], "Estudo B")
    gone = _study(c, ch2["id"], "Estudo na Lixeira")
    assert c.patch(f"/api/studies/{placed['id']}/canvas", json={
        "pos_x": 10.0, "pos_y": 20.0, "width": 300.0, "height": 200.0, "color_tag": "amber"}).status_code == 200
    frame = c.post(f"/api/books/{book['id']}/canvas/frames", json={
        "title": "Moldura Fictícia", "color": "violet", "pos_x": 0.0, "pos_y": 0.0, "width": 500.0, "height": 400.0}).json()
    for target, kind, desc in ((b, "complementa", "detalhe fictício"), (gone, "contradiz", "")):
        assert c.post(f"/api/studies/{a['id']}/relations", json={
            "target_study_id": target["id"], "relation_type": kind, "description": desc}).status_code in (200, 201)
    c.post(f"/api/studies/{gone['id']}/trash")

    canvas = _export(c, book["id"])
    _valid(canvas)
    nodes = {n["id"]: n for n in canvas["nodes"]}
    assert nodes[f"frame-{frame['id']}"] | {} == {**nodes[f"frame-{frame['id']}"], "type": "group",
                                                   "label": "Moldura Fictícia", "color": "6"}
    p = nodes[f"study-{placed['id']}"]
    assert (p["x"], p["y"], p["width"], p["height"], p["color"]) == (10, 20, 300, 200, "2")
    assert p["text"].startswith("## Estudo Posicionado")
    assert f"study-{gone['id']}" not in nodes, "lixeira fora"
    groups = {n["label"]: n for n in canvas["nodes"] if n["type"] == "group" and n["id"].startswith("chapter-")}
    assert set(groups) == {"Capítulo 1", "Capítulo 2"}
    auto = [nodes[f"study-{a['id']}"], nodes[f"study-{b['id']}"]]
    assert all(n["x"] > 500 for n in auto), "automáticos à direita do que já tinha posição"
    assert not _overlap(*auto)
    for card in auto:
        group = groups["Capítulo 1"] if card is auto[0] else groups["Capítulo 2"]
        assert group["x"] <= card["x"] and card["x"] + card["width"] <= group["x"] + group["width"]
        assert group["y"] <= card["y"] and card["y"] + card["height"] <= group["y"] + group["height"]
    assert nodes[f"study-{a['id']}"]["text"].endswith('"aspas", \\ barra e\nquebra de linha 📚.')
    assert [e["label"] for e in canvas["edges"]] == ["Complementa: detalhe fictício"], "relação com lixeira fora"
    assert canvas["edges"][0]["toEnd"] == "arrow"
    raw = json.dumps(canvas, ensure_ascii=False)
    assert NOTE not in raw and SOURCE not in raw


def test_empty_book_and_isolation(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    book = c.post("/api/books", json={"title": "Livro Vazio"}).json()
    assert _export(c, book["id"]) == {"nodes": [], "edges": []}
    assert sharing_harness.client_bob.get(f"/api/books/{book['id']}/canvas/export").status_code == 404
