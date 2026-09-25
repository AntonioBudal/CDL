from __future__ import annotations

from datetime import timedelta
import os

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME, SESSION_COOKIE_NAME
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.db.types import utc_now
from app.main import app
from app.models.local_credential import LocalCredential
from app.models.user import User
from app.models.user_session import UserSession


@pytest.fixture
def auth_client(tmp_path, monkeypatch):
    """Cria um cliente de testes hermético com banco SQLite efêmero e REQUIRE_AUTH ativado."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")

    db_file = tmp_path / "caderno_test_auth.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with testing_session_local() as db_session:
        # Provisiona proprietário canônico (sem senha inicialmente)
        owner = User(
            id=DEFAULT_OWNER_ID,
            username=DEFAULT_OWNER_USERNAME,
            display_name="Proprietário do Caderno",
            role="admin",
            status="ativo",
        )
        # Provisiona usuário leitor de teste com senha cadastrada
        leitor = User(
            id="11111111-1111-1111-1111-111111111111",
            username="leitor_teste",
            email="leitor@teste.com",
            display_name="Leitor de Teste",
            role="user",
            status="ativo",
        )
        cred = LocalCredential(
            user_id=leitor.id,
            password_hash=hash_password("SenhaValida123!"),
        )
        db_session.add_all([owner, leitor, cred])
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


def test_anonymous_access_blocked_when_auth_required(auth_client):
    client, _ = auth_client
    # Tenta acessar rotas protegidas sem cookie e sem cabeçalho X-User-Id
    resp = client.get("/api/books")
    assert resp.status_code == 401
    assert "Não autenticado" in resp.json()["detail"]

    resp_me = client.get("/api/auth/me")
    assert resp_me.status_code == 401


def test_login_invalid_credentials(auth_client):
    client, _ = auth_client

    # Usuário inexistente
    r1 = client.post(
        "/api/auth/login",
        json={"username_or_email": "fantasma", "password": "qualquer_senha"},
    )
    assert r1.status_code == 401
    assert "Credenciais incorretas" in r1.json()["detail"]

    # Senha errada
    r2 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_teste", "password": "senha_errada"},
    )
    assert r2.status_code == 401
    assert "Credenciais incorretas" in r2.json()["detail"]

    # Usuário sem credencial cadastrada (ex.: proprietário legado antes do setup)
    r3 = client.post(
        "/api/auth/login",
        json={"username_or_email": "proprietario", "password": "qualquer_senha"},
    )
    assert r3.status_code == 401


def test_login_success_and_session_cookie(auth_client):
    client, session_factory = auth_client

    # Login com username
    r = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_teste", "password": "SenhaValida123!"},
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["username"] == "leitor_teste"
    assert "session_id" in data
    assert SESSION_COOKIE_NAME in r.cookies

    # Confirma atributos do cookie
    cookie = r.cookies.get(SESSION_COOKIE_NAME)
    assert len(cookie) >= 40

    # Acesso a rota protegida com cookie de sessão
    r_me = client.get("/api/auth/me")
    assert r_me.status_code == 200
    assert r_me.json()["username"] == "leitor_teste"

    # Acesso a listagem de livros do usuário
    r_books = client.get("/api/books")
    assert r_books.status_code == 200

    # Confirma que sessão foi gravada no banco com hash e device_name amigável
    with session_factory() as db:
        session_obj = db.get(UserSession, data["session_id"])
        assert session_obj is not None
        assert session_obj.device_name == "Chrome no Windows"
        assert session_obj.session_token_hash != cookie  # Token cru não é salvo no banco


def test_login_with_email(auth_client):
    client, _ = auth_client

    # Login usando e-mail em vez de username
    r = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor@teste.com", "password": "SenhaValida123!"},
    )
    assert r.status_code == 200
    assert r.json()["user"]["username"] == "leitor_teste"


def test_session_anti_fixation(auth_client):
    client, _ = auth_client

    r1 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_teste", "password": "SenhaValida123!"},
    )
    cookie1 = r1.cookies.get(SESSION_COOKIE_NAME)

    r2 = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_teste", "password": "SenhaValida123!"},
    )
    cookie2 = r2.cookies.get(SESSION_COOKIE_NAME)

    # Novo identificador emitido a cada login
    assert cookie1 != cookie2


def test_expired_session_rejected(auth_client):
    client, session_factory = auth_client

    r = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_teste", "password": "SenhaValida123!"},
    )
    session_id = r.json()["session_id"]

    # Força a sessão a expirar no passado
    with session_factory() as db:
        s = db.get(UserSession, session_id)
        s.expires_at = utc_now() - timedelta(days=1)
        db.commit()

    # Tentativa de acesso com sessão expirada
    r_expired = client.get("/api/auth/me")
    assert r_expired.status_code == 401
    assert "expirada" in r_expired.json()["detail"].lower()


def test_auth_config_and_setup_owner(auth_client):
    client, session_factory = auth_client

    # 1. Proprietário ainda não tem senha -> owner_setup_required deve ser True
    r_config = client.get("/api/auth/config")
    assert r_config.status_code == 200
    assert r_config.json()["owner_setup_required"] is True
    assert r_config.json()["allow_registration"] is True

    # 2. Setup inicial do proprietário com senha válida
    r_setup = client.post(
        "/api/auth/setup-owner",
        json={"password": "MestraSegura2026!"},
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
    )
    assert r_setup.status_code == 200
    setup_data = r_setup.json()
    assert setup_data["user"]["username"] == DEFAULT_OWNER_USERNAME
    assert SESSION_COOKIE_NAME in r_setup.cookies

    # 3. Imediatamente autenticado como proprietário
    r_me = client.get("/api/auth/me")
    assert r_me.status_code == 200
    assert r_me.json()["username"] == DEFAULT_OWNER_USERNAME

    # 4. Config agora deve indicar que o setup não é mais necessário
    r_config_after = client.get("/api/auth/config")
    assert r_config_after.status_code == 200
    assert r_config_after.json()["owner_setup_required"] is False

    # 5. Tentativa subsequente de setup-owner deve ser rejeitada com 403
    r_repeat = client.post(
        "/api/auth/setup-owner",
        json={"password": "OutraSenha123!"},
    )
    assert r_repeat.status_code == 403
    assert "já possui senha" in r_repeat.json()["detail"]


def test_setup_owner_validation(auth_client):
    client, _ = auth_client

    # Senha curta (< 8 caracteres)
    r_short = client.post(
        "/api/auth/setup-owner",
        json={"password": "curta"},
    )
    assert r_short.status_code in (400, 422)


def test_register_new_user_success(auth_client):
    client, _ = auth_client

    payload = {
        "username": "novoleitor",
        "display_name": "Novo Leitor",
        "email": "novo@leitor.com",
        "password": "SenhaDoNovoLeitor123!",
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["username"] == "novoleitor"
    assert data["user"]["email"] == "novo@leitor.com"
    assert SESSION_COOKIE_NAME in r.cookies

    # Acesso imediato à rota protegida
    r_me = client.get("/api/auth/me")
    assert r_me.status_code == 200
    assert r_me.json()["username"] == "novoleitor"


def test_register_conflicts_and_validation(auth_client):
    client, _ = auth_client

    # Conflito de username (já existe leitor_teste)
    r_user_conflict = client.post(
        "/api/auth/register",
        json={
            "username": "leitor_teste",
            "display_name": "Outro Nome",
            "email": "outro@teste.com",
            "password": "SenhaValida123!",
        },
    )
    assert r_user_conflict.status_code == 409
    assert "Nome de usuário já está em uso" in r_user_conflict.json()["detail"]

    # Conflito de email (já existe leitor@teste.com)
    r_email_conflict = client.post(
        "/api/auth/register",
        json={
            "username": "novo_username_ok",
            "display_name": "Outro Nome",
            "email": "leitor@teste.com",
            "password": "SenhaValida123!",
        },
    )
    assert r_email_conflict.status_code == 409
    assert "E-mail já está em uso" in r_email_conflict.json()["detail"]

    # Senha curta
    r_short = client.post(
        "/api/auth/register",
        json={
            "username": "usuario_valido",
            "display_name": "Usuario Valido",
            "password": "123",
        },
    )
    assert r_short.status_code in (400, 422)


def test_register_blocked_when_disabled(auth_client, monkeypatch):
    client, _ = auth_client
    monkeypatch.setenv("ALLOW_REGISTRATION", "false")

    r = client.post(
        "/api/auth/register",
        json={
            "username": "bloqueado",
            "display_name": "Bloqueado",
            "password": "SenhaValida123!",
        },
    )
    assert r.status_code == 403
    assert "desativado" in r.json()["detail"].lower()


def test_logout_destroys_session(auth_client):
    client, session_factory = auth_client

    # 1. Login
    r_login = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_teste", "password": "SenhaValida123!"},
    )
    assert r_login.status_code == 200
    session_id = r_login.json()["session_id"]

    # Verifica que sessão existe no banco
    with session_factory() as db:
        assert db.get(UserSession, session_id) is not None

    # 2. Logout
    r_logout = client.post("/api/auth/logout")
    assert r_logout.status_code == 200
    assert r_logout.json()["ok"] is True

    # Verifica que sessão foi removida do banco
    with session_factory() as db:
        assert db.get(UserSession, session_id) is None

    # 3. Requisição subsequente deve retornar 401
    r_me = client.get("/api/auth/me")
    assert r_me.status_code == 401


def test_sliding_window_activity_update(auth_client):
    client, session_factory = auth_client

    r_login = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_teste", "password": "SenhaValida123!"},
    )
    session_id = r_login.json()["session_id"]

    # Simula última atividade ocorrida há 15 minutos (acima do throttle de 10 min)
    with session_factory() as db:
        s = db.get(UserSession, session_id)
        original_last_activity = s.last_activity
        original_expires_at = s.expires_at
        s.last_activity = utc_now() - timedelta(minutes=15)
        s.expires_at = s.last_activity + timedelta(days=30)
        db.commit()

    # Faz requisição autenticada
    r_me = client.get("/api/auth/me")
    assert r_me.status_code == 200

    # Verifica que last_activity e expires_at foram estendidos
    with session_factory() as db:
        s_updated = db.get(UserSession, session_id)
        assert s_updated.last_activity > original_last_activity - timedelta(minutes=10)
        assert s_updated.expires_at > original_expires_at - timedelta(minutes=10)

