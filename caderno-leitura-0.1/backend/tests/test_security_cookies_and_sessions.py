from __future__ import annotations

from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME, SESSION_COOKIE_NAME
from app.core.rate_limiter import auth_failure_tracker, auth_rate_limiter
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.local_credential import LocalCredential
from app.models.user import User


@pytest.fixture
def session_client(tmp_path, monkeypatch) -> Generator[tuple[TestClient, sessionmaker], None, None]:
    """Cria ambiente isolado para testes de cookies de sessão e logout."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)

    auth_rate_limiter.reset()
    auth_failure_tracker.reset_all()

    db_file = tmp_path / "test_session_security.db"
    engine = create_sqlite_engine(db_file)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

    with session_factory() as session:
        user = User(
            id=DEFAULT_OWNER_ID,
            username=DEFAULT_OWNER_USERNAME,
            display_name="Proprietário Teste",
            role="admin",
            status="ativo",
        )
        session.add(user)
        cred = LocalCredential(
            user_id=user.id,
            password_hash=hash_password("SenhaSegura123!"),
        )
        session.add(cred)
        session.commit()

    application = create_app()

    def override_session():
        with session_factory() as s:
            yield s

    application.dependency_overrides[get_session] = override_session

    with TestClient(application) as client:
        yield client, session_factory

    auth_rate_limiter.reset()
    auth_failure_tracker.reset_all()


def test_cookie_security_flags_in_local_http(session_client):
    """Em ambiente local HTTP sem proxy, o cookie deve ter HttpOnly, SameSite=Lax e Secure=False."""
    client, _ = session_client
    res = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaSegura123!"},
    )
    assert res.status_code == 200
    set_cookie = res.headers.get("set-cookie", "")
    assert SESSION_COOKIE_NAME in set_cookie
    assert "httponly" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()
    # Em HTTP puro, Secure NÃO deve estar presente no header
    cookie_parts = [part.strip().lower() for part in set_cookie.split(";")]
    assert "secure" not in cookie_parts


def test_cookie_security_flags_behind_https_proxy(session_client):
    """Quando o proxy informa X-Forwarded-Proto: https, o cookie deve incluir Secure=True."""
    client, _ = session_client
    res = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaSegura123!"},
        headers={"X-Forwarded-Proto": "https"},
    )
    assert res.status_code == 200
    set_cookie = res.headers.get("set-cookie", "")
    cookie_parts = [part.strip().lower() for part in set_cookie.split(";")]
    assert "secure" in cookie_parts
    assert "httponly" in cookie_parts
    assert "samesite=lax" in cookie_parts


def test_cookie_security_flags_with_cloudflare_visitor(session_client):
    """Quando Cloudflare envia CF-Visitor com https, o cookie deve incluir Secure=True."""
    client, _ = session_client
    res = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaSegura123!"},
        headers={"CF-Visitor": '{"scheme":"https"}'},
    )
    assert res.status_code == 200
    set_cookie = res.headers.get("set-cookie", "")
    cookie_parts = [part.strip().lower() for part in set_cookie.split(";")]
    assert "secure" in cookie_parts


def test_session_invalidation_on_logout(session_client):
    """Logout revoga o token no servidor e novas requisições com o mesmo cookie recebem 401."""
    client, _ = session_client

    # 1. Login
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaSegura123!"},
    )
    assert login_res.status_code == 200
    token_cookie = client.cookies.get(SESSION_COOKIE_NAME)
    assert token_cookie is not None

    # 2. Verifica acesso autenticado
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["username"] == DEFAULT_OWNER_USERNAME

    # 3. Logout
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200
    logout_set_cookie = logout_res.headers.get("set-cookie", "")
    # Cookie deve ser expirado
    assert "max-age=0" in logout_set_cookie.lower() or 'expires=' in logout_set_cookie.lower()

    # 4. Tenta reutilizar o token anterior em uma nova requisição manual
    res_reuse = client.get("/api/auth/me", headers={"Cookie": f"{SESSION_COOKIE_NAME}={token_cookie}"})
    assert res_reuse.status_code == 401


def test_session_fixation_protection_generates_new_token(session_client):
    """Cada login bem-sucedido gera um token novo e exclusivo, prevenindo fixação de sessão."""
    client, _ = session_client

    res1 = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaSegura123!"},
    )
    token1 = client.cookies.get(SESSION_COOKIE_NAME)

    res2 = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaSegura123!"},
    )
    token2 = client.cookies.get(SESSION_COOKIE_NAME)

    assert token1 is not None
    assert token2 is not None
    assert token1 != token2
