from __future__ import annotations

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME, SESSION_COOKIE_NAME
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.local_credential import LocalCredential
from app.models.user import User
from app.models.user_session import UserSession


@pytest.fixture
def device_client(tmp_path, monkeypatch):
    """Fixture com banco efêmero e REQUIRE_AUTH habilitado para testes de dispositivos."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")

    db_file = tmp_path / "caderno_test_devices.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with testing_session_local() as db_session:
        # Usuário 1: Leitor Principal
        user1 = User(
            id="11111111-1111-1111-1111-111111111111",
            username="leitor_um",
            email="um@teste.com",
            display_name="Leitor Um",
            role="user",
            status="ativo",
        )
        cred1 = LocalCredential(
            user_id=user1.id,
            password_hash=hash_password("SenhaValida123!"),
        )
        # Usuário 2: Outro Leitor (para validação anti-IDOR)
        user2 = User(
            id="22222222-2222-2222-2222-222222222222",
            username="leitor_dois",
            email="dois@teste.com",
            display_name="Leitor Dois",
            role="user",
            status="ativo",
        )
        cred2 = LocalCredential(
            user_id=user2.id,
            password_hash=hash_password("SenhaValida123!"),
        )
        db_session.add_all([user1, cred1, user2, cred2])
        db_session.commit()

    def override_get_session():
        session = testing_session_local()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client, testing_session_local
    app.dependency_overrides.clear()


def test_list_active_sessions_with_friendly_names(device_client):
    client, _ = device_client

    # Login 1: Desktop Chrome no Windows
    r1 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_um", "password": "SenhaValida123!"},
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"},
    )
    cookie1 = r1.cookies.get(SESSION_COOKIE_NAME)
    session1_id = r1.json()["session_id"]

    # Login 2: Celular iPhone com Safari
    client.cookies.clear()
    r2 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_um", "password": "SenhaValida123!"},
        headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"},
    )
    cookie2 = r2.cookies.get(SESSION_COOKIE_NAME)
    session2_id = r2.json()["session_id"]

    # Consulta lista de sessões a partir do Dispositivo 2 (iPhone)
    client.cookies.set(SESSION_COOKIE_NAME, cookie2)
    resp = client.get("/api/auth/sessions")
    assert resp.status_code == 200
    sessions = resp.json()

    assert len(sessions) == 2
    # Verifica que session2 é is_current=True e session1 é is_current=False
    s2 = next(s for s in sessions if s["id"] == session2_id)
    s1 = next(s for s in sessions if s["id"] == session1_id)

    assert s2["is_current"] is True
    assert "iPhone" in s2["device_name"]
    assert s1["is_current"] is False
    assert "Windows" in s1["device_name"]


def test_revoke_remote_session_and_immediate_invalidation(device_client):
    client, _ = device_client

    # Sessão 1 (Dispositivo A)
    client.cookies.clear()
    r1 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_um", "password": "SenhaValida123!"},
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    cookie1 = r1.cookies.get(SESSION_COOKIE_NAME)
    session1_id = r1.json()["session_id"]

    # Sessão 2 (Dispositivo B)
    client.cookies.clear()
    r2 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_um", "password": "SenhaValida123!"},
        headers={"User-Agent": "Mozilla/5.0 (Android 14; Mobile)"},
    )
    cookie2 = r2.cookies.get(SESSION_COOKIE_NAME)
    session2_id = r2.json()["session_id"]

    # No Dispositivo B, revoga remotamente a Sessão 1
    client.cookies.set(SESSION_COOKIE_NAME, cookie2)
    del_resp = client.delete(f"/api/auth/sessions/{session1_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["ok"] is True

    # Comprova que o Dispositivo A tem seu acesso imediatamente revogado
    client.cookies.set(SESSION_COOKIE_NAME, cookie1)
    r_check = client.get("/api/auth/me")
    assert r_check.status_code == 401

    # Enquanto o Dispositivo B permanece conectado
    client.cookies.set(SESSION_COOKIE_NAME, cookie2)
    r_check2 = client.get("/api/auth/me")
    assert r_check2.status_code == 200


def test_anti_idor_session_revocation(device_client):
    client, _ = device_client

    # Leitor Dois faz login
    client.cookies.clear()
    r_user2 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_dois", "password": "SenhaValida123!"},
    )
    user2_session_id = r_user2.json()["session_id"]

    # Leitor Um faz login
    client.cookies.clear()
    r_user1 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_um", "password": "SenhaValida123!"},
    )
    cookie1 = r_user1.cookies.get(SESSION_COOKIE_NAME)

    # Leitor Um tenta deletar a sessão do Leitor Dois -> 404 Not Found (anti-IDOR)
    client.cookies.set(SESSION_COOKIE_NAME, cookie1)
    r_idor = client.delete(f"/api/auth/sessions/{user2_session_id}")
    assert r_idor.status_code == 404


def test_logout_all_revokes_all_other_sessions(device_client):
    client, _ = device_client

    # Cria 3 sessões para o Leitor Um
    cookies = []
    session_ids = []
    for ua in ["Device1", "Device2", "Device3"]:
        client.cookies.clear()
        r = client.post(
            "/api/auth/login",
            json={"username_or_email": "leitor_um", "password": "SenhaValida123!"},
            headers={"User-Agent": ua},
        )
        cookies.append(r.cookies.get(SESSION_COOKIE_NAME))
        session_ids.append(r.json()["session_id"])

    # Estando no Device3 (cookies[2]), executa logout-all
    client.cookies.set(SESSION_COOKIE_NAME, cookies[2])
    r_all = client.post("/api/auth/logout-all")
    assert r_all.status_code == 200
    assert r_all.json()["revoked_count"] == 2

    # Device3 continua ativo
    client.cookies.set(SESSION_COOKIE_NAME, cookies[2])
    assert client.get("/api/auth/me").status_code == 200

    # Device1 e Device2 agora são rejeitados com 401
    client.cookies.set(SESSION_COOKIE_NAME, cookies[0])
    assert client.get("/api/auth/me").status_code == 401

    client.cookies.set(SESSION_COOKIE_NAME, cookies[1])
    assert client.get("/api/auth/me").status_code == 401
