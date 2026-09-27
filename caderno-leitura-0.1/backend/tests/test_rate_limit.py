from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.rate_limiter import auth_rate_limiter, InMemoryRateLimiter
from app.db.base import Base
from app.db.session import get_session
from app.main import app


@pytest.fixture(autouse=True)
def clean_rate_limiter():
    """Garante que a memória do rate limiter esteja limpa antes e depois de cada teste."""
    auth_rate_limiter.reset()
    yield
    auth_rate_limiter.reset()


def test_in_memory_rate_limiter_unit():
    """Testa a lógica da janela deslizante e retry-after do InMemoryRateLimiter."""
    limiter = InMemoryRateLimiter(max_attempts=3, window_seconds=10)

    # 3 requisições permitidas
    allowed, retry = limiter.check_rate_limit("user1")
    assert allowed is True
    assert retry == 0

    allowed, retry = limiter.check_rate_limit("user1")
    assert allowed is True
    assert retry == 0

    allowed, retry = limiter.check_rate_limit("user1")
    assert allowed is True
    assert retry == 0

    # 4ª requisição deve ser bloqueada
    allowed, retry = limiter.check_rate_limit("user1")
    assert allowed is False
    assert retry > 0

    # Chave diferente não deve ser afetada
    allowed_other, retry_other = limiter.check_rate_limit("user2")
    assert allowed_other is True
    assert retry_other == 0

    # Reset limpa a chave
    limiter.reset("user1")
    allowed, retry = limiter.check_rate_limit("user1")
    assert allowed is True


def test_rate_limit_on_login_endpoint(tmp_path, monkeypatch):
    """Testa se o endpoint de login retorna HTTP 429 com cabeçalho Retry-After após exceder tentativas."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("RATE_LIMIT_MAX_ATTEMPTS", "5")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "300")

    db_file = tmp_path / "test_rate_limit.db"
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

    try:
        with TestClient(app) as client:
            # 5 tentativas permitidas (mesmo que com credenciais inválidas)
            for _ in range(5):
                resp = client.post(
                    "/api/auth/login",
                    json={"username_or_email": "usuario_teste", "password": "senha_incorreta_123"},
                    headers={"X-Forwarded-For": "192.168.1.100"},
                )
                assert resp.status_code != 429

            # 6ª tentativa deve estourar o limite (HTTP 429)
            resp = client.post(
                "/api/auth/login",
                json={"username_or_email": "usuario_teste", "password": "senha_incorreta_123"},
                headers={"X-Forwarded-For": "192.168.1.100"},
            )
            assert resp.status_code == 429
            assert "Retry-After" in resp.headers
            assert int(resp.headers["Retry-After"]) > 0
            data = resp.json()
            assert "Muitas tentativas" in data.get("detail", "")

            # Outro IP ainda consegue tentar
            resp_diff_ip = client.post(
                "/api/auth/login",
                json={"username_or_email": "usuario_teste", "password": "senha_incorreta_123"},
                headers={"X-Forwarded-For": "192.168.1.200"},
            )
            assert resp_diff_ip.status_code != 429
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
