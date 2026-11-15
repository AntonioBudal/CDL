"""F0.12.07 (spec 120): círculos de leitura com trava anti-spoiler. Só leitores e textos fictícios, banco em tmp_path."""
from __future__ import annotations

import json
import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config

from app.core.config import BACKEND_DIR
from app.models import Friendship
from tests.test_sharing_and_permissions import (  # noqa: F401  (fixture com vários usuários)
    USER_ALICE_ID,
    USER_BOB_ID,
    USER_CARLOS_ID,
    sharing_harness,
)

SPOILER = "O mordomo fictício era o culpado"


def _befriend(harness, a, b, status="accepted"):
    with harness.session_factory() as session:
        x, y = Friendship.normalize_pair(a, b)
        session.add(Friendship(user_id_a=x, user_id_b=y, action_user_id=a, status=status))
        session.commit()


def _book(client, title="Livro de Teste", chapters=("Capítulo 1", "Capítulo 2", "Capítulo 3"), isbn=None):
    payload = {"title": title, "author": "Ana Fictícia"}
    if isbn:
        payload["isbn"] = isbn
    book = client.post("/api/books", json=payload)
    assert book.status_code == 201, book.text
    for name in chapters:
        client.post(f"/api/books/{book.json()['id']}/chapters", json={"name": name})
    return book.json()["id"]


def _circle(harness):
    alice, bob = harness.client_alice, harness.client_bob
    created = alice.post("/api/circles", json={"book_id": _book(alice)})
    assert created.status_code == 201, created.text
    circle = created.json()
    assert [p["name"] for p in circle["parts"]] == ["Capítulo 1", "Capítulo 2", "Capítulo 3"]
    assert circle["role"] == "owner" and circle["name"] == "Livro de Teste"
    assert alice.post(f"/api/circles/{circle['id']}/invites", json={"username": "bob"}).status_code == 200
    assert bob.post(f"/api/circles/{circle['id']}/accept").status_code == 200
    return circle


def test_invites_only_friends_accept_decline_and_404(sharing_harness):  # noqa: F811
    alice, bob, carlos = sharing_harness.client_alice, sharing_harness.client_bob, sharing_harness.client_carlos
    circle_id = alice.post("/api/circles", json={"book_id": _book(alice)}).json()["id"]
    url = f"/api/circles/{circle_id}"

    assert alice.post(f"{url}/invites", json={"username": "carlos"}).status_code == 422, "não é amigo"
    assert alice.post(f"{url}/invites", json={"username": "daniel"}).status_code == 404, "bloqueado"
    assert bob.get(url).status_code == 404 and carlos.get(url).status_code == 404

    invited = alice.post(f"{url}/invites", json={"username": "bob"})
    assert invited.status_code == 200
    assert alice.post(f"{url}/invites", json={"username": "bob"}).status_code == 409
    assert [f["username"] for f in alice.get(f"{url}/invitable").json()] == []
    assert bob.get("/api/circles/invites/count").json() == {"count": 1}
    listing = bob.get("/api/circles").json()
    assert listing["circles"] == [] and listing["invites"][0]["invited_by"]["username"] == "alice"
    assert bob.get(url).status_code == 404, "convidado ainda não vê o círculo"

    assert bob.post(f"{url}/decline").status_code == 204
    assert bob.get("/api/circles/invites/count").json() == {"count": 0}
    alice.post(f"{url}/invites", json={"username": "bob"})
    detail = bob.post(f"{url}/accept").json()
    assert detail["role"] == "member" and {m["username"] for m in detail["members"]} == {"alice", "bob"}
    assert bob.post(f"{url}/invites", json={"username": "alice"}).status_code == 403, "só o dono convida"


def test_spoiler_lock_never_leaks_text(sharing_harness):  # noqa: F811
    alice, bob = sharing_harness.client_alice, sharing_harness.client_bob
    circle = _circle(sharing_harness)
    url = f"/api/circles/{circle['id']}"
    part1, part2, part3 = (p["id"] for p in circle["parts"])

    # Alice está na parte 3 e escreve lá; Bob ainda não começou.
    assert alice.put(f"{url}/progress", json={"progress": 3}).status_code == 200
    assert alice.post(f"{url}/parts/{part3}/posts", json={"body": SPOILER}).status_code == 200
    assert alice.post(f"{url}/parts/{part1}/posts", json={"body": "Começo tranquilo."}).status_code == 200

    locked = bob.get(f"{url}/parts/{part3}/posts").json()
    assert locked == {"part_id": part3, "locked": True, "count": 1, "posts": []}
    for response in (bob.get(url), bob.get("/api/circles"), locked):
        raw = json.dumps(response if isinstance(response, dict) else response.json(), ensure_ascii=False)
        assert SPOILER not in raw, "o texto à frente nunca vai para quem está atrás"
    detail = bob.get(url).json()
    assert [p["visible"] for p in detail["parts"]] == [False, False, False]
    assert [p["post_count"] for p in detail["parts"]] == [1, 0, 1]

    # Escrever à frente é recusado; avançar abre; voltar tranca de novo.
    assert bob.post(f"{url}/parts/{part2}/posts", json={"body": "Oi"}).status_code == 403
    bob.put(f"{url}/progress", json={"progress": 3})
    assert bob.get(f"{url}/parts/{part3}/posts").json()["posts"][0]["body"] == SPOILER
    bob.put(f"{url}/progress", json={"progress": 1})
    assert bob.get(f"{url}/parts/{part3}/posts").json()["locked"] is True
    assert bob.get(f"{url}/parts/{part1}/posts").json()["locked"] is False
    finished = bob.put(f"{url}/progress", json={"progress": 0, "finished": True}).json()
    assert all(p["visible"] for p in finished["parts"]) and finished["finished"] is True
    assert bob.put(f"{url}/progress", json={"progress": 4}).status_code == 422


def test_posts_edit_delete_moderation_and_block(sharing_harness):  # noqa: F811
    alice, bob, carlos = sharing_harness.client_alice, sharing_harness.client_bob, sharing_harness.client_carlos
    _befriend(sharing_harness, USER_ALICE_ID, USER_CARLOS_ID)
    circle = _circle(sharing_harness)
    url = f"/api/circles/{circle['id']}"
    part1 = circle["parts"][0]["id"]
    alice.post(f"{url}/invites", json={"username": "carlos"})
    carlos.post(f"{url}/accept")
    for client in (alice, bob, carlos):
        client.put(f"{url}/progress", json={"progress": 1})

    posts = bob.post(f"{url}/parts/{part1}/posts", json={"body": "Mensagem do Bob"}).json()["posts"]
    bob_post = posts[0]["id"]
    carlos.post(f"{url}/parts/{part1}/posts", json={"body": "Mensagem do Carlos"})
    assert carlos.patch(f"{url}/posts/{bob_post}", json={"body": "x"}).status_code == 403
    assert carlos.delete(f"{url}/posts/{bob_post}").status_code == 403
    edited = bob.patch(f"{url}/posts/{bob_post}", json={"body": "Mensagem editada"}).json()["posts"]
    assert edited[0]["body"] == "Mensagem editada" and edited[0]["edited_at"]
    assert bob.post(f"{url}/parts/{part1}/posts", json={"body": "   "}).status_code == 422
    assert bob.post(f"{url}/parts/{part1}/posts", json={"body": "x" * 4001}).status_code == 422

    # Bloqueio entre Bob e Carlos: cada um deixa de ver o outro.
    _befriend(sharing_harness, USER_BOB_ID, USER_CARLOS_ID, status="blocked")
    bodies = lambda c: [p["body"] for p in c.get(f"{url}/parts/{part1}/posts").json()["posts"]]  # noqa: E731
    assert bodies(bob) == ["Mensagem editada"] and bodies(carlos) == ["Mensagem do Carlos"]
    assert set(bodies(alice)) == {"Mensagem editada", "Mensagem do Carlos"}

    # Moderação: o dono apaga qualquer mensagem.
    assert alice.delete(f"{url}/posts/{bob_post}").status_code == 200
    assert bodies(alice) == ["Mensagem do Carlos"]


def test_parts_members_leave_delete_and_my_copy(sharing_harness):  # noqa: F811
    alice, bob = sharing_harness.client_alice, sharing_harness.client_bob
    bob_book = _book(bob, title="Livro de Teste: edição de bolso", chapters=())
    circle = _circle(sharing_harness)
    url = f"/api/circles/{circle['id']}"
    assert bob.get(url).json()["my_book_id"] == bob_book, "título sem subtítulo + autor"

    added = alice.post(f"{url}/parts", json={"name": "Epílogo"}).json()
    assert [p["position"] for p in added["parts"]] == [1, 2, 3, 4]
    assert bob.post(f"{url}/parts", json={"name": "x"}).status_code == 403
    first, last = added["parts"][0]["id"], added["parts"][-1]["id"]
    assert alice.patch(f"{url}/parts/{first}", json={"name": "Primeira parte"}).json()["parts"][0]["name"] == \
        "Primeira parte"
    assert alice.delete(f"{url}/parts/{first}").status_code == 422, "só a última"
    alice.put(f"{url}/progress", json={"progress": 4})
    alice.post(f"{url}/parts/{last}/posts", json={"body": "Fim fictício"})
    assert alice.delete(f"{url}/parts/{last}").status_code == 409, "tem mensagens"
    third = added["parts"][2]["id"]
    alice.delete(f"{url}/posts/{alice.get(f'{url}/parts/{last}/posts').json()['posts'][0]['id']}")
    after = alice.delete(f"{url}/parts/{last}").json()
    assert len(after["parts"]) == 3 and after["progress"] == 3 and after["parts"][-1]["id"] == third

    assert alice.post(f"{url}/leave").status_code == 422, "dono não sai"
    assert bob.post(f"{url}/leave").status_code == 204
    assert bob.get(url).status_code == 404
    alice.post(f"{url}/invites", json={"username": "bob"})
    bob.post(f"{url}/accept")
    assert {m["username"] for m in alice.delete(f"{url}/members/{USER_BOB_ID}").json()["members"]} == {"alice"}
    assert bob.delete(url).status_code == 404
    assert alice.delete(url).status_code == 204
    assert alice.get(url).status_code == 404
    assert alice.post("/api/circles", json={"book_id": 999999}).status_code == 404
    alice_book = _book(alice, title="Outro Livro Fictício")
    assert bob.post("/api/circles", json={"book_id": alice_book}).status_code == 404, "livro de outro leitor"


def test_migration_0042_up_and_down(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "head")
    with closing(sqlite3.connect(db)) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"reading_circles", "reading_circle_parts", "reading_circle_members", "reading_circle_posts"} <= tables
    command.downgrade(cfg, "0041_image_occlusion_cards")
    with closing(sqlite3.connect(db)) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert not {t for t in tables if t.startswith("reading_circle")}
