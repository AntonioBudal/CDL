from __future__ import annotations

from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.core.rate_limiter import auth_failure_tracker, auth_rate_limiter
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.local_credential import LocalCredential
from app.models.user import User


@pytest.fixture
def auth_client(tmp_path, monkeypatch) -> Generator[tuple[TestClient, sessionmaker], None, None]:
    """Cria ambiente hermético para testes de autenticação e rate limit com banco em tmp_path."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("CADERNO_AUTH_MAX_ATTEMPTS_PER_MINUTE", "30")
    monkeypatch.setenv("CADERNO_AUTH_MAX_CONSECUTIVE_FAILURES", "5")
    monkeypatch.setenv("CADERNO_AUTH_FAILURE_LOCKOUT_SECONDS", "60")

    # Reseta o estado global dos limitadores para cada teste
    auth_rate_limiter.reset()
    auth_failure_tracker.reset_all()

    db_file = tmp_path / "test_rate_limit.db"
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
            password_hash=hash_password("SenhaCorreta123!"),
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


def test_consecutive_failed_logins_trigger_lockout_429(auth_client):
    """5 falhas consecutivas de autenticação a partir do mesmo IP disparam HTTP 429 com Retry-After."""
    client, _ = auth_client
    ip_headers = {"X-Forwarded-For": "203.0.113.10"}

    # Tentativas 1 a 4: credenciais inválidas -> 401
    for _ in range(4):
        res = client.post(
            "/api/auth/login",
            json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "senha_errada"},
            headers=ip_headers,
        )
        assert res.status_code == 401
        assert "Credenciais inválidas." in res.json()["detail"]

    # 5ª tentativa: atinge o limiar e bloqueia -> 429
    res5 = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "senha_errada"},
        headers=ip_headers,
    )
    assert res5.status_code == 429
    assert "Retry-After" in res5.headers
    retry_after = int(res5.headers["Retry-After"])
    assert 1 <= retry_after <= 60
    assert "Muitas tentativas incorretas" in res5.json()["detail"]

    # Tentativa seguinte imediata (mesmo com senha correta) deve ser rejeitada pelo lockout ativo
    res_bloqueado = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaCorreta123!"},
        headers=ip_headers,
    )
    assert res_bloqueado.status_code == 429


def test_successful_login_resets_failure_counter(auth_client):
    """Login bem-sucedido zera as falhas acumuladas antes de atingir o bloqueio."""
    client, _ = auth_client
    ip_headers = {"X-Forwarded-For": "203.0.113.20"}

    # 3 falhas
    for _ in range(3):
        res = client.post(
            "/api/auth/login",
            json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "senha_errada"},
            headers=ip_headers,
        )
        assert res.status_code == 401

    # 1 sucesso
    res_ok = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaCorreta123!"},
        headers=ip_headers,
    )
    assert res_ok.status_code == 200

    # Mais 4 falhas: não deve travar na 2ª tentativa, pois o contador foi zerado
    for _ in range(4):
        res = client.post(
            "/api/auth/login",
            json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "senha_errada"},
            headers=ip_headers,
        )
        assert res.status_code == 401


def test_reading_and_health_endpoints_are_not_affected_by_auth_lockout(auth_client):
    """Lockout de autenticação não impede chamadas em endpoints públicos de saúde ou leitura."""
    client, _ = auth_client
    ip_headers = {"X-Forwarded-For": "203.0.113.30"}

    # Força bloqueio de autenticação para este IP
    for _ in range(5):
        client.post(
            "/api/auth/login",
            json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "senha_errada"},
            headers=ip_headers,
        )

    # Health check deve continuar respondendo 200 normalmente para o mesmo IP
    health_res = client.get("/api/health", headers=ip_headers)
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "ok"


def test_volumetric_rate_limit_exceeded(auth_client):
    """Exceder o teto volumétrico de 30 requisições/minuto aciona HTTP 429."""
    client, _ = auth_client
    ip_headers = {"X-Forwarded-For": "203.0.113.40"}

    # Simula 30 requisições em rota de auth
    for _ in range(30):
        auth_rate_limiter.check_rate_limit(f"203.0.113.40:auth_volumetric", max_attempts=30, window_seconds=60)

    # A 31ª requisição deve ser bloqueada por cota volumétrica
    res = client.post(
        "/api/auth/login",
        json={"username_or_email": DEFAULT_OWNER_USERNAME, "password": "SenhaCorreta123!"},
        headers=ip_headers,
    )
    assert res.status_code == 429
    assert "Muitas requisições" in res.json()["detail"]
