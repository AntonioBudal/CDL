from __future__ import annotations

from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.user import User


@pytest.fixture
def security_client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    """Cria um cliente de testes hermético com banco SQLite descartável em tmp_path."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    db_file = tmp_path / "test_security.db"
    engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

    with testing_session_local() as session:
        user = User(
            id=DEFAULT_OWNER_ID,
            username=DEFAULT_OWNER_USERNAME,
            display_name="Proprietário Teste",
            role="admin",
            status="ativo",
        )
        session.add(user)
        session.commit()

    application = create_app()

    def override_get_session():
        session = testing_session_local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    application.dependency_overrides[get_session] = override_get_session

    with TestClient(application) as client:
        yield client


def test_mandatory_security_headers_present_on_api_endpoints(security_client):
    """Valida se 100% das respostas da API possuem os cabeçalhos de segurança consagrados."""
    response = security_client.get("/api/health")
    assert response.status_code == 200

    headers = response.headers
    # OWASP Core Security Headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert headers.get("Permissions-Policy") == "camera=(), microphone=(), geolocation=()"
    assert headers.get("X-Frame-Options") == "SAMEORIGIN"

    # CSP em modo Enforce
    csp = headers.get("Content-Security-Policy")
    assert csp is not None
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'self'" in csp
    assert "https://accounts.google.com" in csp
    assert "https://fonts.googleapis.com" in csp
    assert "https://fonts.gstatic.com" in csp


def test_security_headers_present_on_public_routes(security_client):
    """Valida se rotas públicas institucionais e de busca contêm os cabeçalhos de segurança."""
    response = security_client.get("/robots.txt")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert "Content-Security-Policy" in headers


def test_private_routes_retain_noindex_and_security_headers(security_client):
    """Valida se rotas internas privadas mantêm X-Robots-Tag aliado a todos os cabeçalhos de proteção."""
    response = security_client.get("/api/books")
    assert response.status_code == 200
    assert response.headers.get("X-Robots-Tag") == "noindex, nofollow"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("Content-Security-Policy") is not None
