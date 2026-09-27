from __future__ import annotations

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import SESSION_COOKIE_NAME
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.user import User
from app.services.google_auth_service import GoogleTokenPayload


@pytest.fixture
def google_web_client(tmp_path, monkeypatch):
    """Cliente hermético para testes do fluxo OAuth 2.0 Web do Google."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")

    db_file = tmp_path / "test_google_oauth_web.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_session():
        s = session_factory()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    app.dependency_overrides[get_session] = override_session

    with TestClient(app, follow_redirects=False) as client:
        yield client, session_factory

    app.dependency_overrides.clear()
    engine.dispose()


def test_google_login_redirect_url(google_web_client):
    """Testa se GET /api/auth/google/login redireciona para a página de autorização do Google com status 307."""
    client, _ = google_web_client

    response = client.get("/api/auth/google/login")
    assert response.status_code == 307
    location = response.headers.get("location", "")
    assert "https://accounts.google.com/o/oauth2/v2/auth" in location
    assert "client_id=test-client-id.apps.googleusercontent.com" in location
    assert "redirect_uri=" in location
    assert "scope=" in location
    assert "state=" in location


def test_google_callback_creates_new_user(google_web_client):
    """Testa se o callback OAuth provisiona automaticamente um novo usuário sem senha e cria sessão 302."""
    client, session_factory = google_web_client

    mock_payload = GoogleTokenPayload(
        sub="google-web-sub-101",
        email="novo.web.oauth@exemplo.com",
        email_verified=True,
        name="Novo Web Leitor",
    )

    with patch("app.services.google_auth_service.exchange_google_code_for_token", return_value=mock_payload):
        response = client.get("/api/auth/google/callback?code=fake-auth-code&state=fake-state")
        assert response.status_code == 302
        assert response.headers.get("location") == "/"
        assert SESSION_COOKIE_NAME in response.cookies

        # Valida criação do usuário no banco
        with session_factory() as s:
            user = s.query(User).filter(User.email == "novo.web.oauth@exemplo.com").first()
            assert user is not None
            assert user.display_name == "Novo Web Leitor"
            assert user.status == "ativo"
            assert user.has_google is True
            assert user.has_password is False


def test_google_callback_auto_links_existing_user(google_web_client):
    """Testa se o callback vincula automaticamente a conta Google a um usuário local existente."""
    client, session_factory = google_web_client

    with session_factory() as s:
        user = User(
            id="88888888-8888-8888-8888-888888888888",
            username="leitor_ja_existente",
            email="ja.existe@exemplo.com",
            display_name="Leitor Já Existente",
            status="ativo",
        )
        s.add(user)
        s.commit()

    mock_payload = GoogleTokenPayload(
        sub="google-web-sub-202",
        email="ja.existe@exemplo.com",
        email_verified=True,
        name="Leitor Já Existente",
    )

    with patch("app.services.google_auth_service.exchange_google_code_for_token", return_value=mock_payload):
        response = client.get("/api/auth/google/callback?code=another-fake-code&state=another-state")
        assert response.status_code == 302
        assert response.headers.get("location") == "/"
        assert SESSION_COOKIE_NAME in response.cookies

        with session_factory() as s:
            db_user = s.get(User, "88888888-8888-8888-8888-888888888888")
            assert db_user.has_google is True
