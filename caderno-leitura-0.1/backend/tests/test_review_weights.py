"""F0.11.08 (spec 110): peso de dificuldade e fila da revisão. Só dados fictícios; banco em tmp_path."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.review_weights import effective_weight, interval_days, is_due, next_weight, queue_key
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    sharing_harness,
)

NOW = datetime(2026, 11, 12, 12, tzinfo=UTC)


def test_weight_accumulates_history():
    assert next_weight(None, "hard") == 0.75
    assert next_weight(0.75, "hard") == 0.875
    assert next_weight(0.875, "easy") == 0.4375
    assert next_weight(None, "medium") == 0.5
    assert effective_weight(None, "hard") == 0.75 and effective_weight(0.3, "hard") == 0.3
    assert effective_weight(None, None) is None


def test_intervals_and_due():
    assert [interval_days(w) for w in (0.9, 0.75, 0.6, 0.5, 0.3, 0.1, None)] == [1, 1, 3, 3, 7, 14, 3]
    assert is_due(0.8, None, NOW)
    assert is_due(0.8, NOW - timedelta(days=1), NOW)
    assert not is_due(0.3, NOW - timedelta(days=6), NOW)
    assert is_due(0.3, NOW - timedelta(days=7), NOW)


def test_queue_order():
    items = {
        "novo": (None, None),
        "leve_vencido": (0.2, NOW - timedelta(days=20)),
        "pesado_vencido": (0.9, NOW - timedelta(days=2)),
        "pesado_recente": (0.9, NOW - timedelta(hours=2)),
        "leve_recente": (0.2, NOW - timedelta(days=1)),
    }
    order = sorted(items, key=lambda k: queue_key(*items[k], NOW, k))
    assert order == ["novo", "pesado_vencido", "leve_vencido", "pesado_recente", "leve_recente"]


def _item(client, kind="question"):
    book = client.post("/api/books", json={"title": "Livro de Teste", "author": "Ana Fictícia"}).json()
    ch = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    study = client.post("/api/studies", json={
        "chapter_id": ch["id"], "title": "Estudo de Teste", "summary": "Resumo fictício com trecho.",
        "explanation": "", "concepts": "", "references": "",
    }).json()
    res = client.post(f"/api/studies/{study['id']}/highlights", json={
        "section": "summary", "selected_text": "trecho", "kind": kind, "note": "Pergunta fictícia?",
    })
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_rating_records_weight(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    item = _item(c)
    for rating in ("hard", "hard", "easy"):
        assert c.post(f"/api/review/items/{item}/record", json={"rating": rating}).status_code == 200
    data = c.get("/api/review/items", params={"limit": 50}).json()
    assert [(i["id"], i["difficulty_weight"], i["review_count"]) for i in data] == [(item, 0.4375, 3)]
