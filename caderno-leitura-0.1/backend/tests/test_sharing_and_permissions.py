from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.friendship import Friendship
from app.models.resource_permission import ResourcePermission
from app.models.study import Study
from app.models.user import User
from app.services.profile_service import get_or_create_profile

USER_ALICE_ID = "11111111-1111-1111-1111-111111111111"
USER_BOB_ID = "22222222-2222-2222-2222-222222222222"
USER_CARLOS_ID = "33333333-3333-3333-3333-333333333333"
USER_DANIEL_ID = "44444444-4444-4444-4444-444444444444"


@pytest.fixture
def sharing_harness(tmp_path: Path, monkeypatch):
    """Fixture hermética com banco SQLite temporário isolado e múltiplos usuários."""
    avatars_dir = tmp_path / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CADERNO_AVATARS_DIR", str(avatars_dir))
    monkeypatch.setenv("REQUIRE_AUTH", "false")

    db_path = tmp_path / "sharing_test.db"
    db_url = f"sqlite:///{db_path.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with testing_session_local() as db_session:
        alice = User(
            id=USER_ALICE_ID,
            username="alice",
            email="alice@exemplo.com",
            display_name="Alice Leitora",
            role="user",
            status="ativo",
        )
        bob = User(
            id=USER_BOB_ID,
            username="bob",
            email="bob@exemplo.com",
            display_name="Bob Estudioso",
            role="user",
            status="ativo",
        )
        carlos = User(
            id=USER_CARLOS_ID,
            username="carlos",
            email="carlos@exemplo.com",
            display_name="Carlos Visitante",
            role="user",
            status="ativo",
        )
        daniel = User(
            id=USER_DANIEL_ID,
            username="daniel",
            email="daniel@exemplo.com",
            display_name="Daniel Bloqueado",
            role="user",
            status="ativo",
        )
        for u in [alice, bob, carlos, daniel]:
            db_session.add(u)
            p = get_or_create_profile(u, db_session)
            if u.username == "alice":
                p.bio = "Leitora voraz"
            elif u.username == "bob":
                p.bio = "Estudante de filosofia"

        # Amizade Alice <-> Bob (aceita)
        u_a, u_b = Friendship.normalize_pair(USER_ALICE_ID, USER_BOB_ID)
        friendship_ab = Friendship(
            user_id_a=u_a,
            user_id_b=u_b,
            action_user_id=USER_ALICE_ID,
            status="accepted",
        )
        # Bloqueio Alice <-> Daniel (bloqueado por Alice)
        u_ad1, u_ad2 = Friendship.normalize_pair(USER_ALICE_ID, USER_DANIEL_ID)
        friendship_ad = Friendship(
            user_id_a=u_ad1,
            user_id_b=u_ad2,
            action_user_id=USER_ALICE_ID,
            status="blocked",
        )
        db_session.add_all([friendship_ab, friendship_ad])
        db_session.commit()

    app = create_app()

    def override_get_session():
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session

    alice_client = TestClient(app, headers={"X-User-Id": USER_ALICE_ID})
    bob_client = TestClient(app, headers={"X-User-Id": USER_BOB_ID})
    carlos_client = TestClient(app, headers={"X-User-Id": USER_CARLOS_ID})
    daniel_client = TestClient(app, headers={"X-User-Id": USER_DANIEL_ID})

    class Harness:
        session_factory = testing_session_local
        client_alice = alice_client
        client_bob = bob_client
        client_carlos = carlos_client
        client_daniel = daniel_client

    return Harness()


# ---------------------------------------------------------------------------
# US1: Modos Fundamentais de Visibilidade (Privado, Amigos, Público)
# ---------------------------------------------------------------------------


def test_private_resource_only_accessible_by_owner(sharing_harness):
    """Recursos privados só podem ser lidos pelo dono; outros recebem 404 anti-enumeração."""
    c_alice = sharing_harness.client_alice
    c_bob = sharing_harness.client_bob
    c_carlos = sharing_harness.client_carlos

    # Alice cria livro e capítulo
    r_book = c_alice.post("/api/books", json={"title": "Diário Privado de Alice"})
    assert r_book.status_code == 201
    book_id = r_book.json()["id"]

    r_chap = c_alice.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert r_chap.status_code == 201
    chap_id = r_chap.json()["id"]

    # Alice cria estudo (padrão de livro é 'private', estudo é 'inherit' -> privado)
    r_study = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Privado", "summary": "Anotações íntimas."},
    )
    assert r_study.status_code == 201
    study_id = r_study.json()["id"]

    # Alice consulta (dono -> can_edit=True)
    res_a = c_alice.get(f"/api/studies/{study_id}")
    assert res_a.status_code == 200
    assert res_a.json()["can_edit"] is True
    assert res_a.json()["visibility"] == "inherit"

    # Bob (amigo) tenta consultar recurso privado -> 404
    res_b = c_bob.get(f"/api/studies/{study_id}")
    assert res_b.status_code == 404

    # Carlos (estranho) tenta consultar recurso privado -> 404
    res_c = c_carlos.get(f"/api/studies/{study_id}")
    assert res_c.status_code == 404


def test_friends_visibility_accessible_by_friends_not_strangers(sharing_harness):
    """Estudo com visibilidade 'friends' pode ser lido por amigos (can_edit=False) e dá 404 para estranhos."""
    c_alice = sharing_harness.client_alice
    c_bob = sharing_harness.client_bob
    c_carlos = sharing_harness.client_carlos

    r_book = c_alice.post("/api/books", json={"title": "Livro de Filosofia"})
    book_id = r_book.json()["id"]
    r_chap = c_alice.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    chap_id = r_chap.json()["id"]

    r_study = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo para Amigos", "summary": "Reflexão compartilhada."},
    )
    study_id = r_study.json()["id"]

    # Alice altera visibilidade para 'friends'
    r_vis = c_alice.put(f"/api/studies/{study_id}/visibility", json={"visibility": "friends"})
    assert r_vis.status_code == 200
    assert r_vis.json()["visibility"] == "friends"
    assert r_vis.json()["effective_visibility"] == "friends"

    # Bob (amigo) consulta com sucesso em modo somente-leitura
    res_b = c_bob.get(f"/api/studies/{study_id}")
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["can_edit"] is False
    assert data_b["owner"]["username"] == "alice"
    assert data_b["title"] == "Estudo para Amigos"

    # Carlos (não é amigo) recebe 404
    res_c = c_carlos.get(f"/api/studies/{study_id}")
    assert res_c.status_code == 404


def test_public_visibility_accessible_by_any_authenticated_user(sharing_harness):
    """Estudo público pode ser lido por qualquer usuário autenticado com can_edit=False."""
    c_alice = sharing_harness.client_alice
    c_carlos = sharing_harness.client_carlos

    r_book = c_alice.post("/api/books", json={"title": "Ciência Aberta"})
    book_id = r_book.json()["id"]
    r_chap = c_alice.post(f"/api/books/{book_id}/chapters", json={"name": "Introdução"})
    chap_id = r_chap.json()["id"]

    r_study = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Público", "summary": "Conhecimento livre."},
    )
    study_id = r_study.json()["id"]

    # Altera para público
    r_vis = c_alice.put(f"/api/studies/{study_id}/visibility", json={"visibility": "public"})
    assert r_vis.status_code == 200

    # Carlos (estranho autenticado) consegue ler perfeitamente
    res_c = c_carlos.get(f"/api/studies/{study_id}")
    assert res_c.status_code == 200
    assert res_c.json()["can_edit"] is False
    assert res_c.json()["owner"]["username"] == "alice"


def test_inheritance_from_book(sharing_harness):
    """Estudo com visibility='inherit' adota visibilidade do livro; override individual tem precedência."""
    c_alice = sharing_harness.client_alice
    c_bob = sharing_harness.client_bob
    c_carlos = sharing_harness.client_carlos

    # Alice cria livro e define livro como 'friends'
    r_book = c_alice.post("/api/books", json={"title": "Livro de Amigos"})
    book_id = r_book.json()["id"]
    r_vis_book = c_alice.put(f"/api/books/{book_id}/visibility", json={"visibility": "friends"})
    assert r_vis_book.status_code == 200

    r_chap = c_alice.post(f"/api/books/{book_id}/chapters", json={"name": "Cap 1"})
    chap_id = r_chap.json()["id"]

    # Estudo 1: inherit (herda 'friends')
    r_s1 = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Herdado", "summary": "Herda do livro."},
    )
    s1_id = r_s1.json()["id"]

    # Bob (amigo) acessa s1
    res_b = c_bob.get(f"/api/studies/{s1_id}")
    assert res_b.status_code == 200
    assert res_b.json()["effective_visibility"] == "friends"

    # Carlos (estranho) não acessa s1
    assert c_carlos.get(f"/api/studies/{s1_id}").status_code == 404

    # Estudo 2: override para 'public' dentro de livro 'friends'
    r_s2 = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Override Publico", "summary": "Sobrescreve livro."},
    )
    s2_id = r_s2.json()["id"]
    c_alice.put(f"/api/studies/{s2_id}/visibility", json={"visibility": "public"})

    # Carlos acessa s2 com override público
    res_c = c_carlos.get(f"/api/studies/{s2_id}")
    assert res_c.status_code == 200
    assert res_c.json()["effective_visibility"] == "public"

    # Estudo 3: override para 'private' dentro de livro 'friends'
    r_s3 = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Override Privado", "summary": "Sobrescreve para privado."},
    )
    s3_id = r_s3.json()["id"]
    c_alice.put(f"/api/studies/{s3_id}/visibility", json={"visibility": "private"})

    # Bob não consegue acessar s3 (foi sobrescrito para privado)
    assert c_bob.get(f"/api/studies/{s3_id}").status_code == 404


def test_mutation_shield_403_for_readers(sharing_harness):
    """Convidado que pode ler estudo recebe 403 Forbidden ao tentar PATCH, DELETE ou mutação."""
    c_alice = sharing_harness.client_alice
    c_bob = sharing_harness.client_bob

    r_book = c_alice.post("/api/books", json={"title": "Livro Somente Leitura"})
    book_id = r_book.json()["id"]
    r_chap = c_alice.post(f"/api/books/{book_id}/chapters", json={"name": "Cap 1"})
    chap_id = r_chap.json()["id"]

    r_study = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Imutável", "summary": "Texto original."},
    )
    study_id = r_study.json()["id"]
    c_alice.put(f"/api/studies/{study_id}/visibility", json={"visibility": "friends"})

    # Bob consegue ler
    assert c_bob.get(f"/api/studies/{study_id}").status_code == 200

    # Bob tenta editar (PATCH) -> 403 Forbidden
    r_patch = c_bob.patch(f"/api/studies/{study_id}", json={"summary": "Tentativa de adulteração."})
    assert r_patch.status_code == 403
    assert "Acesso somente leitura" in r_patch.json()["detail"]

    # Bob tenta mover para lixeira -> 403 Forbidden
    r_trash = c_bob.post(f"/api/studies/{study_id}/trash")
    assert r_trash.status_code == 403

    # Bob tenta atualizar status de maturação -> 403 Forbidden
    r_status = c_bob.patch(f"/api/studies/{study_id}/status", json={"reading_status": "concluido"})
    assert r_status.status_code == 403

    # Bob tenta alterar visibilidade -> 404 (apenas o dono pode alterar visibilidade)
    r_vis = c_bob.put(f"/api/studies/{study_id}/visibility", json={"visibility": "public"})
    assert r_vis.status_code == 404


# ---------------------------------------------------------------------------
# US2: Permissões Granulares Nominais / ACL Customizada
# ---------------------------------------------------------------------------


def test_custom_acl_grant_and_revoke(sharing_harness):
    """No modo 'custom', apenas usuários concedidos nominalmente acessam o estudo."""
    c_alice = sharing_harness.client_alice
    c_carlos = sharing_harness.client_carlos

    r_book = c_alice.post("/api/books", json={"title": "Projeto Secreto"})
    book_id = r_book.json()["id"]
    r_chap = c_alice.post(f"/api/books/{book_id}/chapters", json={"name": "Cap 1"})
    chap_id = r_chap.json()["id"]

    r_study = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Custom", "summary": "Para pessoas selecionadas."},
    )
    study_id = r_study.json()["id"]

    # Define visibilidade como 'custom'
    c_alice.put(f"/api/studies/{study_id}/visibility", json={"visibility": "custom"})

    # Carlos (ainda sem permissão) recebe 404
    assert c_carlos.get(f"/api/studies/{study_id}").status_code == 404

    # Alice concede permissão nominal para @carlos
    r_grant = c_alice.post(f"/api/studies/{study_id}/permissions", json={"username": "carlos"})
    assert r_grant.status_code == 201
    assert r_grant.json()["username"] == "carlos"
    assert r_grant.json()["user_id"] == USER_CARLOS_ID

    # Carlos agora acessa o estudo com sucesso
    res_c = c_carlos.get(f"/api/studies/{study_id}")
    assert res_c.status_code == 200
    assert res_c.json()["can_edit"] is False

    # Alice lista permissões nominais
    r_perms = c_alice.get(f"/api/studies/{study_id}/permissions")
    assert r_perms.status_code == 200
    perms_data = r_perms.json()
    assert len(perms_data["permissions"]) == 1
    assert perms_data["permissions"][0]["username"] == "carlos"

    # Tentativa de conceder duplicada retorna 409 Conflict
    r_dup = c_alice.post(f"/api/studies/{study_id}/permissions", json={"username": "carlos"})
    assert r_dup.status_code == 409

    # Tentativa de conceder a si mesma retorna 400 Bad Request
    r_self = c_alice.post(f"/api/studies/{study_id}/permissions", json={"username": "alice"})
    assert r_self.status_code == 400

    # Alice revoga a permissão de Carlos
    r_rev = c_alice.delete(f"/api/studies/{study_id}/permissions/{USER_CARLOS_ID}")
    assert r_rev.status_code == 200
    assert r_rev.json()["ok"] is True

    # Carlos perde o acesso imediatamente (404)
    assert c_carlos.get(f"/api/studies/{study_id}").status_code == 404


# ---------------------------------------------------------------------------
# US3: Recursos Compartilhados Comigo (/api/shared)
# ---------------------------------------------------------------------------


def test_shared_with_me_feed(sharing_harness):
    """Feed /api/shared/studies lista estudos compartilhados e suporta busca textual."""
    c_alice = sharing_harness.client_alice
    c_bob = sharing_harness.client_bob

    r_book = c_alice.post("/api/books", json={"title": "A República"})
    book_id = r_book.json()["id"]
    r_chap = c_alice.post(f"/api/books/{book_id}/chapters", json={"name": "Livro I"})
    chap_id = r_chap.json()["id"]

    # Cria estudo compartilhado com amigos
    r_s1 = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "A Justiça em Platão", "summary": "Debate com Trasímaco."},
    )
    s1_id = r_s1.json()["id"]
    c_alice.put(f"/api/studies/{s1_id}/visibility", json={"visibility": "friends"})

    # Cria estudo privado (não deve aparecer)
    c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Anotações Pessoais Platão", "summary": "Rascunho."},
    )

    # Bob acessa feed compartilhado
    r_shared = c_bob.get("/api/shared/studies")
    assert r_shared.status_code == 200
    shared_data = r_shared.json()
    assert shared_data["total"] >= 1
    titles = [item["title"] for item in shared_data["items"]]
    assert "A Justiça em Platão" in titles
    assert "Anotações Pessoais Platão" not in titles

    # Busca por query 'Platão'
    r_search = c_bob.get("/api/shared/studies?q=Justiça")
    assert r_search.status_code == 200
    assert len(r_search.json()["items"]) == 1
    assert r_search.json()["items"][0]["title"] == "A Justiça em Platão"

    # Busca por autor 'alice'
    r_author = c_bob.get("/api/shared/studies?author=alice")
    assert r_author.status_code == 200
    assert len(r_author.json()["items"]) >= 1


# ---------------------------------------------------------------------------
# US4: Blindagem contra Bloqueios (F06)
# ---------------------------------------------------------------------------


def test_blocked_user_cannot_access_even_public_resources(sharing_harness):
    """Usuário bloqueado (Daniel) recebe 404 mesmo para estudos públicos de Alice e não aparece na ACL."""
    c_alice = sharing_harness.client_alice
    c_daniel = sharing_harness.client_daniel

    r_book = c_alice.post("/api/books", json={"title": "Livro Público Aberto"})
    book_id = r_book.json()["id"]
    r_chap = c_alice.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    chap_id = r_chap.json()["id"]

    r_study = c_alice.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo para Todos", "summary": "Acesso irrestrito."},
    )
    study_id = r_study.json()["id"]
    c_alice.put(f"/api/studies/{study_id}/visibility", json={"visibility": "public"})

    # Daniel está bloqueado por Alice -> recebe 404 inviolável
    res_d = c_daniel.get(f"/api/studies/{study_id}")
    assert res_d.status_code == 404

    # Daniel não vê o estudo no feed compartilhado
    res_shared = c_daniel.get("/api/shared/studies")
    assert res_shared.status_code == 200
    daniel_titles = [item["title"] for item in res_shared.json()["items"]]
    assert "Estudo para Todos" not in daniel_titles

    # Alice tenta conceder ACL nominal para Daniel -> recusado (400 Bad Request)
    r_grant_blocked = c_alice.post(f"/api/studies/{study_id}/permissions", json={"username": "daniel"})
    assert r_grant_blocked.status_code == 400
    assert "bloqueio ativo" in r_grant_blocked.json()["detail"].lower()
