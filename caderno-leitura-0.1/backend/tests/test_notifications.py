from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

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
from app.models.notification import Notification
from app.models.study import Study
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services import friendship_service, notification_service, sharing_service
from app.services.profile_service import get_or_create_profile

USER_ALICE_ID = "11111111-1111-1111-1111-111111111111"
USER_BOB_ID = "22222222-2222-2222-2222-222222222222"
USER_CARLOS_ID = "33333333-3333-3333-3333-333333333333"
ADMIN_USER_ID = "99999999-9999-9999-9999-999999999999"


@pytest.fixture
def notifications_harness(tmp_path: Path, monkeypatch):
    """Fixture hermética com banco SQLite temporário isolado e clientes para Alice, Bob e Admin."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")

    db_path = tmp_path / "notifications_test.db"
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
            display_name="Carlos Leitor",
            role="user",
            status="ativo",
        )
        admin = User(
            id=ADMIN_USER_ID,
            username="admin",
            email="admin@exemplo.com",
            display_name="Administrador",
            role="admin",
            status="ativo",
        )
        for u in [alice, bob, carlos, admin]:
            db_session.add(u)
            profile = get_or_create_profile(u, db_session)
            if u.id == USER_ALICE_ID:
                profile.bio = "Leitora voraz"
                profile.avatar_url = "/avatars/alice.webp"
            elif u.id == USER_BOB_ID:
                profile.bio = "Estudante de filosofia"
        db_session.commit()

    app = create_app()

    def override_get_session():
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session

    client_alice = TestClient(app, headers={"X-User-Id": USER_ALICE_ID})
    client_bob = TestClient(app, headers={"X-User-Id": USER_BOB_ID})
    client_carlos = TestClient(app, headers={"X-User-Id": USER_CARLOS_ID})
    client_admin = TestClient(app, headers={"X-User-Id": ADMIN_USER_ID})

    return {
        "session_factory": testing_session_local,
        "alice": client_alice,
        "bob": client_bob,
        "carlos": client_carlos,
        "admin": client_admin,
    }


def test_unread_count_empty(notifications_harness):
    """Verifica que o leitor inicia com contador de não lidas zerado."""
    client = notifications_harness["alice"]
    resp = client.get("/api/notifications/unread-count")
    assert resp.status_code == 200
    assert resp.json() == {"unread_count": 0}


def test_create_and_list_notifications(notifications_harness):
    """Verifica a criação de notificações e a listagem com paginação e ator preenchido."""
    session_factory = notifications_harness["session_factory"]
    with session_factory() as session:
        notification_service.create_notification(
            session=session,
            user_id=USER_ALICE_ID,
            event_type="friend_request",
            actor_id=USER_BOB_ID,
            payload={"friendship_id": 1, "message": "Bob enviou uma solicitação de amizade."},
        )
        notification_service.create_notification(
            session=session,
            user_id=USER_ALICE_ID,
            event_type="system_alert",
            actor_id=None,
            payload={"title": "Bem-vindo", "message": "Boas-vindas ao Leitorum!"},
        )
        session.commit()

    client = notifications_harness["alice"]

    # Checa contagem de não lidos
    count_resp = client.get("/api/notifications/unread-count")
    assert count_resp.status_code == 200
    assert count_resp.json()["unread_count"] == 2

    # Lista notificações
    list_resp = client.get("/api/notifications?limit=10")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] == 2
    assert data["unread_count"] == 2
    assert len(data["items"]) == 2

    # Checa ator preenchido
    friend_notif = next(item for item in data["items"] if item["event_type"] == "friend_request")
    assert friend_notif["actor"]["id"] == USER_BOB_ID
    assert friend_notif["actor"]["username"] == "bob"

    # Checa alerta de sistema sem ator
    system_notif = next(item for item in data["items"] if item["event_type"] == "system_alert")
    assert system_notif["actor"] is None


def test_mark_as_read_individual(notifications_harness):
    """Marca notificação como lida individualmente e verifica idempotência e decremento de contagem."""
    session_factory = notifications_harness["session_factory"]
    notif_id = None
    with session_factory() as session:
        notif = notification_service.create_notification(
            session=session,
            user_id=USER_ALICE_ID,
            event_type="friend_accepted",
            actor_id=USER_BOB_ID,
            payload={"message": "Bob aceitou sua solicitação."},
        )
        session.commit()
        notif_id = notif.id

    client = notifications_harness["alice"]
    assert client.get("/api/notifications/unread-count").json()["unread_count"] == 1

    # Marca como lida
    patch_resp = client.patch(f"/api/notifications/{notif_id}/read")
    assert patch_resp.status_code == 200
    read_item = patch_resp.json()
    assert read_item["read_at"] is not None

    # Contador deve zerar
    assert client.get("/api/notifications/unread-count").json()["unread_count"] == 0

    # Idempotência: marcar novamente retorna 200 com mesmo timestamp
    patch_resp2 = client.patch(f"/api/notifications/{notif_id}/read")
    assert patch_resp2.status_code == 200
    assert patch_resp2.json()["read_at"] == read_item["read_at"]


def test_mark_all_as_read(notifications_harness):
    """Verifica a ação em lote de marcar todas as notificações acumuladas como lidas."""
    session_factory = notifications_harness["session_factory"]
    with session_factory() as session:
        for i in range(5):
            notification_service.create_notification(
                session=session,
                user_id=USER_ALICE_ID,
                event_type="system_alert",
                payload={"title": f"Aviso {i}", "message": "Teste"},
            )
        session.commit()

    client = notifications_harness["alice"]
    assert client.get("/api/notifications/unread-count").json()["unread_count"] == 5

    post_resp = client.post("/api/notifications/read-all")
    assert post_resp.status_code == 200
    data = post_resp.json()
    assert data["marked_count"] == 5

    assert client.get("/api/notifications/unread-count").json()["unread_count"] == 0


def test_isolation_cannot_access_other_users_notifications(notifications_harness):
    """Garante que um leitor não pode visualizar ou marcar notificações de outro leitor (404)."""
    session_factory = notifications_harness["session_factory"]
    alice_notif_id = None
    with session_factory() as session:
        notif = notification_service.create_notification(
            session=session,
            user_id=USER_ALICE_ID,
            event_type="system_alert",
            payload={"title": "Segredo Alice", "message": "Privado"},
        )
        session.commit()
        alice_notif_id = notif.id

    client_bob = notifications_harness["bob"]
    # Bob tenta marcar como lida a notificação de Alice
    resp = client_bob.patch(f"/api/notifications/{alice_notif_id}/read")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Notificação não encontrada."

    # Bob não visualiza a notificação de Alice em sua listagem
    bob_list = client_bob.get("/api/notifications").json()
    assert bob_list["total"] == 0


def test_friend_request_and_accepted_notifications(notifications_harness):
    """Verifica que o envio de amizade gera friend_request e o aceite gera friend_accepted."""
    client_alice = notifications_harness["alice"]
    client_bob = notifications_harness["bob"]

    # Alice envia pedido para Bob
    req_resp = client_alice.post("/api/friends/request/bob")
    assert req_resp.status_code == 200

    # Bob deve ter 1 notificação não lida do tipo friend_request
    bob_count = client_bob.get("/api/notifications/unread-count").json()["unread_count"]
    assert bob_count == 1

    bob_list = client_bob.get("/api/notifications").json()
    assert len(bob_list["items"]) == 1
    item = bob_list["items"][0]
    assert item["event_type"] == "friend_request"
    assert item["actor"]["username"] == "alice"
    friendship_id = item["payload"]["friendship_id"]

    # Bob aceita o pedido
    accept_resp = client_bob.post(f"/api/friends/accept/{friendship_id}")
    assert accept_resp.status_code == 200

    # Alice agora deve receber uma notificação friend_accepted
    alice_count = client_alice.get("/api/notifications/unread-count").json()["unread_count"]
    assert alice_count == 1

    alice_list = client_alice.get("/api/notifications").json()
    assert len(alice_list["items"]) == 1
    alice_item = alice_list["items"][0]
    assert alice_item["event_type"] == "friend_accepted"
    assert alice_item["actor"]["username"] == "bob"


def test_study_shared_notification(notifications_harness):
    """Verifica que a concessão de permissão nominal sobre um estudo emite notificação study_shared."""
    session_factory = notifications_harness["session_factory"]
    study_id = None
    with session_factory() as session:
        book = Book(user_id=USER_ALICE_ID, title="Dom Casmurro", author="Machado de Assis")
        session.add(book)
        session.flush()

        chapter = Chapter(book_id=book.id, name="Capítulo 1", position=1)
        session.add(chapter)
        session.flush()

        study = Study(
            user_id=USER_ALICE_ID,
            chapter_id=chapter.id,
            title="Capitu e os Olhos de Ressaca",
            summary="Análise psicológica.",
            visibility="private",
        )
        session.add(study)
        session.commit()
        study_id = study.id

    client_alice = notifications_harness["alice"]
    client_bob = notifications_harness["bob"]

    # Alice concede acesso para Bob
    perm_resp = client_alice.post(
        f"/api/studies/{study_id}/permissions",
        json={"username": "bob"},
    )
    assert perm_resp.status_code == 201

    # Bob deve receber uma notificação do tipo study_shared
    bob_count = client_bob.get("/api/notifications/unread-count").json()["unread_count"]
    assert bob_count == 1

    bob_list = client_bob.get("/api/notifications").json()
    item = bob_list["items"][0]
    assert item["event_type"] == "study_shared"
    assert item["actor"]["username"] == "alice"
    assert item["payload"]["resource_title"] == "Capitu e os Olhos de Ressaca"
    assert item["payload"]["link"] == f"/estudos/{study_id}"


def test_admin_broadcast_system_alert(notifications_harness):
    """Verifica que o broadcast administrativo gera alertas para todos os usuários ativos e proíbe usuários comuns."""
    client_admin = notifications_harness["admin"]
    client_alice = notifications_harness["alice"]
    client_bob = notifications_harness["bob"]
    client_carlos = notifications_harness["carlos"]

    # Usuário comum tenta disparar broadcast -> 403 Forbidden
    forbidden_resp = client_alice.post(
        "/api/admin/notifications/broadcast",
        json={"title": "Hack", "message": "Tentativa indevida"},
    )
    assert forbidden_resp.status_code == 403

    # Administrador dispara broadcast oficial
    payload = {
        "title": "Manutenção Programada",
        "message": "Atualização no próximo domingo às 03:00.",
        "severity": "warning",
        "link": "/status",
    }
    broadcast_resp = client_admin.post("/api/admin/notifications/broadcast", json=payload)
    assert broadcast_resp.status_code == 201
    data = broadcast_resp.json()
    assert data["dispatched_count"] == 4  # alice, bob, carlos, admin

    # Todos os leitores recebem a notificação
    for client in [client_alice, client_bob, client_carlos]:
        assert client.get("/api/notifications/unread-count").json()["unread_count"] == 1
        notifs = client.get("/api/notifications").json()
        assert len(notifs["items"]) == 1
        item = notifs["items"][0]
        assert item["event_type"] == "system_alert"
        assert item["actor"]["username"] == "admin"
        assert item["payload"]["title"] == "Manutenção Programada"
        assert item["payload"]["severity"] == "warning"


def test_admin_purge_expired_notifications(notifications_harness):
    """Verifica que a purga remove apenas notificações lidas com mais de 60 dias."""
    session_factory = notifications_harness["session_factory"]
    now = datetime.now(timezone.utc)
    old_date = now - timedelta(days=70)
    recent_date = now - timedelta(days=10)

    with session_factory() as session:
        # 1. Antiga e lida -> DEVE SER PURGADA
        n1 = Notification(
            user_id=USER_ALICE_ID,
            event_type="system_alert",
            payload={"msg": "Antiga lida"},
            created_at=old_date,
            read_at=old_date + timedelta(hours=1),
        )
        # 2. Antiga mas NÃO lida -> NÃO DEVE SER PURGADA (preserva não lidas)
        n2 = Notification(
            user_id=USER_ALICE_ID,
            event_type="system_alert",
            payload={"msg": "Antiga não lida"},
            created_at=old_date,
            read_at=None,
        )
        # 3. Recente e lida -> NÃO DEVE SER PURGADA (ainda no período de retenção)
        n3 = Notification(
            user_id=USER_ALICE_ID,
            event_type="system_alert",
            payload={"msg": "Recente lida"},
            created_at=recent_date,
            read_at=recent_date + timedelta(hours=1),
        )
        session.add_all([n1, n2, n3])
        session.commit()

    client_admin = notifications_harness["admin"]
    client_alice = notifications_harness["alice"]

    # Usuário comum tenta purgar -> 403 Forbidden
    forbidden_resp = client_alice.post("/api/admin/notifications/purge")
    assert forbidden_resp.status_code == 403

    # Admin executa purga
    purge_resp = client_admin.post("/api/admin/notifications/purge?retention_days=60")
    assert purge_resp.status_code == 200
    data = purge_resp.json()
    assert data["purged_count"] == 1
    assert data["retention_days"] == 60

    # Verifica no banco se sobraram apenas n2 e n3
    with session_factory() as session:
        remaining = list(session.query(Notification).all())
        assert len(remaining) == 2
        messages = [r.payload.get("msg") for r in remaining]
        assert "Antiga lida" not in messages
        assert "Antiga não lida" in messages
        assert "Recente lida" in messages



