from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.local_credential import LocalCredential
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.profile_service import get_or_create_profile

USER_ALICE_ID = "11111111-1111-1111-1111-111111111111"
USER_BOB_ID = "22222222-2222-2222-2222-222222222222"
USER_CARLOS_ID = "33333333-3333-3333-3333-333333333333"
USER_DANIEL_ID = "44444444-4444-4444-4444-444444444444"


@pytest.fixture
def friends_harness(tmp_path: Path, monkeypatch):
    """Fixture hermética com banco SQLite temporário isolado e clientes para Alice, Bob, Carlos e Daniel."""
    avatars_dir = tmp_path / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CADERNO_AVATARS_DIR", str(avatars_dir))
    monkeypatch.setenv("REQUIRE_AUTH", "false")

    db_path = tmp_path / "friends_test.db"
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
            display_name="Carlos Filosofia",
            role="user",
            status="ativo",
        )
        daniel = User(
            id=USER_DANIEL_ID,
            username="daniel",
            email="daniel@exemplo.com",
            display_name="Daniel Crítico",
            role="user",
            status="ativo",
        )
        for u in [alice, bob, carlos, daniel]:
            cred = LocalCredential(user_id=u.id, password_hash=hash_password("Senha123!"))
            db_session.add(u)
            db_session.add(cred)
            get_or_create_profile(u, db_session)
        db_session.commit()

    def get_test_db():
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_session] = get_test_db

    class Harness:
        def __init__(self):
            self.session_factory = testing_session_local
            self.raw_client = TestClient(app)

        def client_for(self, user_id: str):
            class UserClient:
                def __init__(self, raw_client, uid):
                    self.raw = raw_client
                    self.headers = {"X-User-Id": uid}

                def get(self, url, **kwargs):
                    h = {**self.headers, **kwargs.pop("headers", {})}
                    return self.raw.get(url, headers=h, **kwargs)

                def post(self, url, **kwargs):
                    h = {**self.headers, **kwargs.pop("headers", {})}
                    return self.raw.post(url, headers=h, **kwargs)

                def put(self, url, **kwargs):
                    h = {**self.headers, **kwargs.pop("headers", {})}
                    return self.raw.put(url, headers=h, **kwargs)

                def delete(self, url, **kwargs):
                    h = {**self.headers, **kwargs.pop("headers", {})}
                    return self.raw.delete(url, headers=h, **kwargs)

            return UserClient(self.raw_client, user_id)

    return Harness()


# ============================================================================
# User Story 1 (P1): Solicitação, Aceite, Recusa e Solicitações Cruzadas
# ============================================================================


def test_friend_request_and_accept_flow(friends_harness):
    """Alice solicita a Bob, Bob aceita, ambos tornam-se amigos."""
    alice_client = friends_harness.client_for(USER_ALICE_ID)
    bob_client = friends_harness.client_for(USER_BOB_ID)

    # 1. Alice solicita amizade a Bob
    resp = alice_client.post("/api/friends/request/bob")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["ok"] is True
    assert data["status"] == "pending"

    # Tentativa duplicada de solicitação gera conflito 409
    dup = alice_client.post("/api/friends/request/bob")
    assert dup.status_code == 409

    # 2. Bob lista pendências e visualiza solicitação recebida de Alice
    reqs_bob = bob_client.get("/api/friends/requests").json()
    assert len(reqs_bob["received"]) == 1
    assert reqs_bob["received"][0]["user"]["username"] == "alice"
    assert len(reqs_bob["sent"]) == 0
    request_id = reqs_bob["received"][0]["request_id"]

    # 3. Alice lista pendências e visualiza solicitação enviada para Bob
    reqs_alice = alice_client.get("/api/friends/requests").json()
    assert len(reqs_alice["sent"]) == 1
    assert reqs_alice["sent"][0]["user"]["username"] == "bob"
    assert len(reqs_alice["received"]) == 0

    # 4. Alice tenta aceitar a própria solicitação (deve ser 403 Forbidden)
    forbidden_resp = alice_client.post(f"/api/friends/accept/{request_id}")
    assert forbidden_resp.status_code == 403

    # 5. Bob aceita a solicitação
    accept_resp = bob_client.post(f"/api/friends/accept/{request_id}")
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

    # 6. Ambos agora constam mutuamente na lista de amigos
    friends_alice = alice_client.get("/api/friends").json()
    assert len(friends_alice) == 1
    assert friends_alice[0]["user"]["username"] == "bob"

    friends_bob = bob_client.get("/api/friends").json()
    assert len(friends_bob) == 1
    assert friends_bob[0]["user"]["username"] == "alice"


def test_self_request_and_invalid_user(friends_harness):
    """Auto-solicitação é proibida e usuário inexistente retorna 404."""
    alice_client = friends_harness.client_for(USER_ALICE_ID)

    self_req = alice_client.post("/api/friends/request/alice")
    assert self_req.status_code == 400
    assert "si mesmo" in self_req.json()["detail"]

    not_found_req = alice_client.post("/api/friends/request/usuario_fantasma")
    assert not_found_req.status_code == 404


def test_cross_simultaneous_requests_auto_accept(friends_harness):
    """Solicitações simultâneas cruzadas convertem-se automaticamente em amizade aceita."""
    carlos_client = friends_harness.client_for(USER_CARLOS_ID)
    daniel_client = friends_harness.client_for(USER_DANIEL_ID)

    # Carlos envia solicitação para Daniel
    resp1 = carlos_client.post("/api/friends/request/daniel")
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "pending"

    # Daniel envia solicitação para Carlos (antes de aceitar a primeira)
    resp2 = daniel_client.post("/api/friends/request/carlos")
    assert resp2.status_code == 200
    # Deve reconhecer a solicitação mútua e aceitar automaticamente
    assert resp2.json()["status"] == "accepted"
    assert "amigos" in resp2.json()["message"].lower()

    # Ambos agora são amigos
    assert len(carlos_client.get("/api/friends").json()) == 1
    assert len(daniel_client.get("/api/friends").json()) == 1


def test_reject_request_returns_to_neutral(friends_harness):
    """Recusar solicitação remove o vínculo e permite nova solicitação futura."""
    alice_client = friends_harness.client_for(USER_ALICE_ID)
    carlos_client = friends_harness.client_for(USER_CARLOS_ID)

    # Alice envia para Carlos
    alice_client.post("/api/friends/request/carlos")
    req_id = carlos_client.get("/api/friends/requests").json()["received"][0]["request_id"]

    # Carlos recusa
    reject_resp = carlos_client.post(f"/api/friends/reject/{req_id}")
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "none"

    # Pendências limpas para ambos
    assert len(carlos_client.get("/api/friends/requests").json()["received"]) == 0
    assert len(alice_client.get("/api/friends/requests").json()["sent"]) == 0

    # Alice pode solicitar novamente no futuro (estado neutro)
    new_req = alice_client.post("/api/friends/request/carlos")
    assert new_req.status_code == 200
    assert new_req.json()["status"] == "pending"


# ============================================================================
# User Story 2 (P2): Cancelamento e Desfazimento de Amizade
# ============================================================================


def test_cancel_friend_request(friends_harness):
    """Remetente cancela a solicitação enviada antes da resposta."""
    alice_client = friends_harness.client_for(USER_ALICE_ID)
    bob_client = friends_harness.client_for(USER_BOB_ID)

    alice_client.post("/api/friends/request/bob")
    req_id = alice_client.get("/api/friends/requests").json()["sent"][0]["request_id"]

    # Bob tenta cancelar a solicitação que Alice enviou (403 Forbidden)
    forbidden_resp = bob_client.delete(f"/api/friends/cancel/{req_id}")
    assert forbidden_resp.status_code == 403

    # Alice cancela a própria solicitação
    cancel_resp = alice_client.delete(f"/api/friends/cancel/{req_id}")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "none"

    # Nenhuma solicitação pendente permanece
    assert len(alice_client.get("/api/friends/requests").json()["sent"]) == 0
    assert len(bob_client.get("/api/friends/requests").json()["received"]) == 0


def test_unfriend_removes_relationship_for_both(friends_harness):
    """Qualquer um dos amigos pode desfazer a amizade, removendo o vínculo de ambos."""
    alice_client = friends_harness.client_for(USER_ALICE_ID)
    bob_client = friends_harness.client_for(USER_BOB_ID)

    # Tornam-se amigos
    alice_client.post("/api/friends/request/bob")
    req_id = bob_client.get("/api/friends/requests").json()["received"][0]["request_id"]
    bob_client.post(f"/api/friends/accept/{req_id}")

    assert len(alice_client.get("/api/friends").json()) == 1
    assert len(bob_client.get("/api/friends").json()) == 1

    # Alice desfaz a amizade com Bob
    unfriend_resp = alice_client.delete("/api/friends/bob")
    assert unfriend_resp.status_code == 200
    assert unfriend_resp.json()["status"] == "none"

    # Ambos deixam de ser amigos
    assert len(alice_client.get("/api/friends").json()) == 0
    assert len(bob_client.get("/api/friends").json()) == 0

    # Tentar desfazer novamente retorna 404
    unfriend_again = alice_client.delete("/api/friends/bob")
    assert unfriend_again.status_code == 404


# ============================================================================
# User Story 3 (P3): Bloqueio, Desbloqueio e Blindagem Bilateral (404)
# ============================================================================


def test_block_unblock_and_anti_enumeration(friends_harness):
    """Bloqueio unilateral ativa blindagem 404 e exclui de buscas em ambas as direções."""
    alice_client = friends_harness.client_for(USER_ALICE_ID)
    daniel_client = friends_harness.client_for(USER_DANIEL_ID)

    # Auto-bloqueio proibido
    self_block = alice_client.post("/api/friends/block/alice")
    assert self_block.status_code == 400

    # Alice bloqueia Daniel
    block_resp = alice_client.post("/api/friends/block/daniel")
    assert block_resp.status_code == 200
    assert block_resp.json()["status"] == "blocked"

    # 1. Blindagem 404: Daniel tenta acessar o perfil público de Alice
    profile_blocked = daniel_client.get("/api/users/alice")
    assert profile_blocked.status_code == 404

    # 2. Blindagem 404: Daniel tenta enviar solicitação para Alice
    request_blocked = daniel_client.post("/api/friends/request/alice")
    assert request_blocked.status_code == 404

    # 3. Exclusão em buscas: Daniel não encontra Alice e Alice não encontra Daniel
    search_daniel = daniel_client.get("/api/users?q=alice").json()
    assert not any(u["username"] == "alice" for u in search_daniel)

    search_alice = alice_client.get("/api/users?q=daniel").json()
    assert not any(u["username"] == "daniel" for u in search_alice)

    # 4. Alice lista usuários bloqueados e Daniel está lá
    blocked_list = alice_client.get("/api/friends/blocked").json()
    assert len(blocked_list) == 1
    assert blocked_list[0]["user"]["username"] == "daniel"
    assert "blocked_at" in blocked_list[0]

    # Daniel não vê nada em sua lista de bloqueados (ele foi a vítima, não o autor)
    assert len(daniel_client.get("/api/friends/blocked").json()) == 0

    # 5. Alice desbloqueia Daniel
    unblock_resp = alice_client.post("/api/friends/unblock/daniel")
    assert unblock_resp.status_code == 200
    assert unblock_resp.json()["status"] == "none"

    # Após desbloqueio, Daniel consegue acessar o perfil de Alice novamente
    profile_restored = daniel_client.get("/api/users/alice")
    assert profile_restored.status_code == 200
    assert profile_restored.json()["username"] == "alice"


# ============================================================================
# User Story 4 (P4): Hub Social, Resumo e Friends Count no Perfil
# ============================================================================


def test_friends_summary_and_status(friends_harness):
    """Resumo de contadores reflete pendências e amigos com precisão."""
    alice_client = friends_harness.client_for(USER_ALICE_ID)
    bob_client = friends_harness.client_for(USER_BOB_ID)
    carlos_client = friends_harness.client_for(USER_CARLOS_ID)

    # Alice solicita a Bob
    alice_client.post("/api/friends/request/bob")

    # Resumo de Alice: 0 amigos, 0 recebidas, 1 enviada
    summary_alice = alice_client.get("/api/friends/summary").json()
    assert summary_alice["friends_count"] == 0
    assert summary_alice["pending_received_count"] == 0
    assert summary_alice["pending_sent_count"] == 1

    # Resumo de Bob: 0 amigos, 1 recebida, 0 enviadas
    summary_bob = bob_client.get("/api/friends/summary").json()
    assert summary_bob["friends_count"] == 0
    assert summary_bob["pending_received_count"] == 1
    assert summary_bob["pending_sent_count"] == 0

    # Status entre Alice e Bob
    status_alice_bob = alice_client.get("/api/friends/status/bob").json()
    assert status_alice_bob["relation_status"] == "pending_sent"

    status_bob_alice = bob_client.get("/api/friends/status/alice").json()
    assert status_bob_alice["relation_status"] == "pending_received"

    # Bob aceita a amizade
    req_id = bob_client.get("/api/friends/requests").json()["received"][0]["request_id"]
    bob_client.post(f"/api/friends/accept/{req_id}")

    # Novo resumo para ambos: 1 amigo
    assert alice_client.get("/api/friends/summary").json()["friends_count"] == 1
    assert bob_client.get("/api/friends/summary").json()["friends_count"] == 1

    # Status mútuo vira "friends"
    assert alice_client.get("/api/friends/status/bob").json()["relation_status"] == "friends"
    assert bob_client.get("/api/friends/status/alice").json()["relation_status"] == "friends"

    # Carlos verifica status com Alice (deve ser "none")
    assert carlos_client.get("/api/friends/status/alice").json()["relation_status"] == "none"

    # Perfil público de Alice agora exibe friends_count == 1
    alice_profile = carlos_client.get("/api/users/alice").json()
    assert alice_profile["friends_count"] == 1
