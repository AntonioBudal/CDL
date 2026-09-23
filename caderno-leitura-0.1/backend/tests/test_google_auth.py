from __future__ import annotations

from unittest.mock import patch

from app.core.config import SESSION_COOKIE_NAME
from app.services.google_auth_service import InvalidGoogleTokenError, verify_google_id_token


def test_login_with_google_success(google_auth_client):
    """Testa autenticação bem-sucedida de usuário com conta Google vinculada."""
    client, session_maker, mock_verify = google_auth_client

    response = client.post(
        "/api/auth/google",
        json={"credential": "valid-jwt-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == "leitor_google"
    assert data["user"]["email"] == "leitor.google@exemplo.com"
    assert data["user"]["has_google"] is True
    assert SESSION_COOKIE_NAME in response.cookies


def test_login_with_google_invalid_token(google_auth_client):
    """Testa rejeição com 401 Unauthorized quando o token fornecido é inválido."""
    client, session_maker, mock_verify = google_auth_client
    mock_verify.side_effect = ValueError("Token signature verification failed")

    response = client.post(
        "/api/auth/google",
        json={"credential": "forged-or-expired-token"},
    )

    assert response.status_code == 401
    assert "Token do Google inválido" in response.json()["detail"]


def test_login_with_google_suspended_user(google_auth_client):
    """Testa rejeição de usuário suspenso vinculado ao Google com 403 Forbidden."""
    client, session_maker, mock_verify = google_auth_client
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-sub-suspended-999",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "suspenso@exemplo.com",
        "email_verified": True,
        "name": "Leitor Suspenso",
    }

    response = client.post(
        "/api/auth/google",
        json={"credential": "valid-token-suspended-user"},
    )

    assert response.status_code == 403
    assert "Conta de usuário suspensa ou inativa" in response.json()["detail"]


def test_login_with_google_wrong_issuer(google_auth_client):
    """Testa rejeição quando o emissor do token não é o Google."""
    client, session_maker, mock_verify = google_auth_client
    mock_verify.return_value = {
        "iss": "https://attacker.com",
        "sub": "google-user-sub-12345",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "leitor.google@exemplo.com",
    }

    response = client.post(
        "/api/auth/google",
        json={"credential": "token-with-bad-issuer"},
    )

    assert response.status_code == 401
    assert "Emissor inválido" in response.json()["detail"]


def test_auto_register_new_google_user(google_auth_client):
    """Testa provisionamento automático de novo usuário via Google quando auto-registro está ativo."""
    client, session_maker, mock_verify = google_auth_client
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-brand-new-sub-777",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "novo.leitor@exemplo.com",
        "email_verified": True,
        "name": "Novo Leitor Exemplo",
    }

    response = client.post(
        "/api/auth/google",
        json={"credential": "valid-token-new-user"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["display_name"] == "Novo Leitor Exemplo"
    assert data["user"]["email"] == "novo.leitor@exemplo.com"
    assert data["user"]["status"] == "ativo"
    assert data["user"]["has_google"] is True
    assert data["user"]["has_password"] is False
    assert SESSION_COOKIE_NAME in response.cookies


def test_reject_new_google_user_when_registration_closed(google_auth_client, monkeypatch):
    """Testa rejeição de usuário inédito com 403 quando ALLOW_REGISTRATION=false."""
    client, session_maker, mock_verify = google_auth_client
    monkeypatch.setenv("ALLOW_REGISTRATION", "false")
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-brand-new-sub-888",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "desconhecido@exemplo.com",
        "email_verified": True,
        "name": "Desconhecido",
    }

    response = client.post(
        "/api/auth/google",
        json={"credential": "valid-token-blocked-new-user"},
    )

    assert response.status_code == 403
    assert "desativados" in response.json()["detail"]


def test_auto_link_verified_email_to_existing_local_user(google_auth_client):
    """Testa vinculação automática quando e-mail verificado coincide com usuário local existente."""
    client, session_maker, mock_verify = google_auth_client
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-new-sub-for-local-user",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "leitor.local@exemplo.com",
        "email_verified": True,
        "name": "Leitor Local Atualizado",
    }

    response = client.post(
        "/api/auth/google",
        json={"credential": "valid-token-local-email"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == "leitor_local"
    assert data["user"]["email"] == "leitor.local@exemplo.com"
    assert data["user"]["has_google"] is True
    assert data["user"]["has_password"] is True


def test_reject_unverified_email_for_new_registration(google_auth_client):
    """Testa rejeição de nova conta quando o e-mail não foi verificado pelo Google."""
    client, session_maker, mock_verify = google_auth_client
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-unverified-sub-111",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "unverified@exemplo.com",
        "email_verified": False,
        "name": "Leitor Não Verificado",
    }

    response = client.post(
        "/api/auth/google",
        json={"credential": "valid-token-unverified-email"},
    )

    assert response.status_code == 400
    assert "deve estar confirmado/verificado" in response.json()["detail"]


def test_link_google_account_success(google_auth_client):
    """Testa vinculação manual bem-sucedida de conta Google em usuário com senha local."""
    client, session_maker, mock_verify = google_auth_client

    # Faz login com usuário local
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_local", "password": "SenhaValidaLocal123!"},
    )
    assert login_res.status_code == 200

    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-sub-to-link-manually",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "vinculo.manual@exemplo.com",
        "email_verified": True,
        "name": "Vinculo Manual",
    }

    link_res = client.post(
        "/api/auth/google/link",
        json={"credential": "valid-token-for-linking"},
    )
    assert link_res.status_code == 200
    data = link_res.json()
    assert data["provider"] == "google"
    assert data["email_at_link"] == "vinculo.manual@exemplo.com"

    # Confere que o perfil agora tem has_google = True
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["has_google"] is True


def test_link_google_account_duplicate_conflict(google_auth_client):
    """Testa rejeição com 409 Conflict ao tentar vincular conta Google já pertencente a outro usuário."""
    client, session_maker, mock_verify = google_auth_client

    # Login como leitor_local
    client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_local", "password": "SenhaValidaLocal123!"},
    )

    # Tenta vincular o sub que já pertence a 'leitor_google' (google-user-sub-12345)
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-user-sub-12345",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "leitor.google@exemplo.com",
        "email_verified": True,
        "name": "Leitor Google",
    }

    res = client.post(
        "/api/auth/google/link",
        json={"credential": "token-sub-belonging-to-other"},
    )
    assert res.status_code == 409
    assert "já está vinculada a outro leitor" in res.json()["detail"]


def test_unlink_google_account_lockout_prevention(google_auth_client):
    """Testa bloqueio de desvinculação (400 Bad Request) se o usuário não possuir senha local."""
    client, session_maker, mock_verify = google_auth_client

    # Faz login com usuário que só tem Google (leitor_google não tem LocalCredential cadastrada)
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-user-sub-12345",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "leitor.google@exemplo.com",
        "email_verified": True,
        "name": "Leitor Google",
    }
    login_res = client.post("/api/auth/google", json={"credential": "valid-token"})
    assert login_res.status_code == 200
    assert login_res.json()["user"]["has_password"] is False

    # Tenta desvincular Google
    unlink_res = client.delete("/api/auth/google/unlink")
    assert unlink_res.status_code == 400
    assert "definir uma senha local antes de desvincular" in unlink_res.json()["detail"]


def test_unlink_google_account_success_with_password(google_auth_client):
    """Testa desvinculação bem-sucedida quando o usuário possui senha local cadastrada."""
    client, session_maker, mock_verify = google_auth_client

    # 1. Login como leitor_local (que possui senha local)
    client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_local", "password": "SenhaValidaLocal123!"},
    )

    # 2. Vincula Google
    mock_verify.return_value = {
        "iss": "https://accounts.google.com",
        "sub": "google-sub-temporary-link",
        "aud": "test-client-id.apps.googleusercontent.com",
        "email": "temp.link@exemplo.com",
        "email_verified": True,
        "name": "Temp Link",
    }
    link_res = client.post("/api/auth/google/link", json={"credential": "temp-token"})
    assert link_res.status_code == 200

    # 3. Desvincula Google com sucesso
    unlink_res = client.delete("/api/auth/google/unlink")
    assert unlink_res.status_code == 200
    assert unlink_res.json()["ok"] is True

    # 4. Confere que has_google agora é False
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["has_google"] is False


def test_google_auth_disabled_when_client_id_empty(google_auth_client, monkeypatch):
    """Testa degradação graciosa: ausência de GOOGLE_CLIENT_ID desativa Google no config e rejeita rotas com 400."""
    client, session_maker, mock_verify = google_auth_client
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "")

    # Config pública indica que Google está desabilitado
    config_res = client.get("/api/auth/config")
    assert config_res.status_code == 200
    config_data = config_res.json()
    assert config_data["google_auth_enabled"] is False
    assert config_data["google_client_id"] is None

    # Tentativa de login via Google retorna 400 Bad Request
    login_res = client.post("/api/auth/google", json={"credential": "some-token"})
    assert login_res.status_code == 400
    assert "Autenticação com Google não está habilitada" in login_res.json()["detail"]

    # Tentativa de vinculação via Google retorna 400 Bad Request
    client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_local", "password": "SenhaValidaLocal123!"},
    )
    link_res = client.post("/api/auth/google/link", json={"credential": "some-token"})
    assert link_res.status_code == 400
    assert "Autenticação com Google não está habilitada" in link_res.json()["detail"]


def test_local_auth_fully_functional_when_google_disabled(google_auth_client, monkeypatch):
    """Testa que a autenticação local e sessão continuam 100% operacionais sem GOOGLE_CLIENT_ID."""
    client, session_maker, mock_verify = google_auth_client
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)

    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_local", "password": "SenhaValidaLocal123!"},
    )
    assert login_res.status_code == 200
    assert login_res.json()["user"]["username"] == "leitor_local"
    assert SESSION_COOKIE_NAME in login_res.cookies

    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "leitor_local"


