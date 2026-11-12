"""F0.11.09 (spec 111): token de recepção e receptor compatível com o Readwise. Só dados fictícios; tmp_path."""
from __future__ import annotations

import logging

from sqlalchemy import select

from app.models import InboxCapture, ReceiverToken
from app.services.receiver_tokens import hash_token
from fastapi.testclient import TestClient

from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    USER_ALICE_ID,
    USER_BOB_ID,
    sharing_harness,
)


def _anon(harness) -> TestClient:
    """Cliente sem sessão nem X-User-Id, como o Readest."""
    return TestClient(harness.client_alice.app)

BASE = "/api/receptor/readwise/v2"


def _body(*texts, title="Livro de Teste", author="Ana Fictícia"):
    return {"highlights": [
        {"text": t, "title": title, "author": author, "note": "", "location": 12 + i, "location_type": "page",
         "highlighted_at": "2026-11-10T12:00:00Z", "source_type": "readest", "category": "books"}
        for i, t in enumerate(texts)
    ]}


def _auth(token):
    return {"Authorization": f"Token {token}"}


def test_token_lifecycle_and_only_hash_stored(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    assert c.get("/api/account/receiver-token").json()["active"] is False
    issued = c.post("/api/account/receiver-token").json()
    token = issued["token"]
    assert token.startswith("lt_") and len(token) > 40
    assert issued["status"]["hint"] == token[:7] and issued["status"]["active"] is True
    status = c.get("/api/account/receiver-token").json()
    assert "token" not in status and status["hint"] == token[:7]
    with sharing_harness.session_factory() as session:
        row = session.scalar(select(ReceiverToken))
        assert row.token_hash == hash_token(token) and token not in (row.token_hash, row.token_hint)

    anon = _anon(sharing_harness)
    assert anon.get(f"{BASE}/auth/", headers=_auth(token)).status_code == 204
    assert anon.get(f"{BASE}/auth", headers={"Authorization": f"Bearer {token}"}).status_code == 204
    assert anon.get(f"{BASE}/auth/").status_code == 401
    assert anon.get(f"{BASE}/auth/", headers=_auth("lt_errado")).status_code == 401
    assert c.get("/api/account/receiver-token").json()["last_used_at"] is not None

    new = c.post("/api/account/receiver-token").json()["token"]
    assert anon.get(f"{BASE}/auth/", headers=_auth(token)).status_code == 401, "o anterior para na hora"
    assert anon.get(f"{BASE}/auth/", headers=_auth(new)).status_code == 204
    assert c.delete("/api/account/receiver-token").status_code == 204
    assert anon.get(f"{BASE}/auth/", headers=_auth(new)).status_code == 401
    assert c.get("/api/account/receiver-token").json()["active"] is False


def test_highlights_go_to_inbox_without_duplicates(sharing_harness, caplog):  # noqa: F811
    c = sharing_harness.client_alice
    existing = c.post("/api/books", json={"title": "Livro de Teste", "author": "Ana Fictícia"}).json()
    token = c.post("/api/account/receiver-token").json()["token"]
    anon = _anon(sharing_harness)

    with caplog.at_level(logging.INFO):
        res = anon.post(f"{BASE}/highlights/", headers=_auth(token), json={"highlights": [
            *_body("Trecho fictício um.", "Page 40")["highlights"],
            *_body("Trecho de outro livro.", title="Livro Novo Fictício", author="Bia Fictícia")["highlights"],
        ]})
    assert res.status_code == 200, res.text
    books = {b["title"]: b for b in res.json()}
    assert books["Livro de Teste"]["id"] == existing["id"], "livro existente pela regra de título/autor"
    assert "Livro Novo Fictício" in books
    assert token not in caplog.text and "Trecho fictício" not in caplog.text, "log só com contagens"

    again = anon.post(f"{BASE}/highlights", headers=_auth(token), json=_body("Trecho fictício um."))
    assert again.status_code == 200
    with sharing_harness.session_factory() as session:
        rows = session.scalars(select(InboxCapture).order_by(InboxCapture.id)).all()
        assert [(r.content, r.status) for r in rows] == [
            ("Trecho fictício um.", "inbox"), ("Trecho de outro livro.", "inbox"),
        ]
        assert rows[0].source_hint == "Readest · p. 12 · 10/11/2026"
        assert rows[0].book_id == existing["id"]
        assert {r.user_id for r in rows} == {USER_ALICE_ID}


def test_receiver_ignores_cookies_and_origin_but_requires_token(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    token = c.post("/api/account/receiver-token").json()["token"]
    # Com cookie de sessão e sem token: recusado (cookie não vale no receptor).
    assert c.post(f"{BASE}/highlights/", json=_body("Trecho.")).status_code == 401
    # Origem de fora não é barrada pela conferência de origem (isenção), mas sem token nada passa.
    foreign = {"Origin": "https://exemplo.invalid"}
    assert _anon(sharing_harness).post(f"{BASE}/highlights/", headers=foreign, json=_body("Trecho.")).status_code == 401
    ok = _anon(sharing_harness).post(f"{BASE}/highlights/", headers={**foreign, **_auth(token)}, json=_body("Trecho."))
    assert ok.status_code == 200
    # A isenção é só do receptor.
    assert c.post("/api/books", headers=foreign, json={"title": "X"}).status_code == 403


def test_limits_and_bad_body(sharing_harness):  # noqa: F811
    c = sharing_harness.client_alice
    token = c.post("/api/account/receiver-token").json()["token"]
    anon = _anon(sharing_harness)
    many = {"highlights": [{"text": f"t{i}", "title": "Livro"} for i in range(1001)]}
    assert anon.post(f"{BASE}/highlights/", headers=_auth(token), json=many).status_code == 413
    huge = {"highlights": [{"text": "x" * 20_001, "title": "Livro"}]}
    assert anon.post(f"{BASE}/highlights/", headers=_auth(token), json=huge).status_code == 422
    assert anon.post(f"{BASE}/highlights/", headers=_auth(token), content=b"nao e json").status_code == 422
    with sharing_harness.session_factory() as session:
        assert session.scalars(select(InboxCapture)).all() == []


def test_inactive_account_token_fails(sharing_harness):  # noqa: F811
    c = sharing_harness.client_bob
    token = c.post("/api/account/receiver-token").json()["token"]
    with sharing_harness.session_factory() as session:
        from app.models import User

        user = session.get(User, USER_BOB_ID)
        user.status = "deactivated"
        session.commit()
    assert _anon(sharing_harness).get(f"{BASE}/auth/", headers=_auth(token)).status_code == 401
