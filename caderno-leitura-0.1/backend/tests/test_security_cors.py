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
def cors_client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    """Cria um cliente de testes isolado com configuração padrão de CORS."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    db_file = tmp_path / "test_cors.db"
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


def test_cors_preflight_allows_authorized_origins(cors_client):
    """Garante que origens locais de desenvolvimento autorizadas recebam resposta favorável ao preflight."""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Authorization, Content-Type",
    }
    response = cors_client.options("/api/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_preflight_blocks_unauthorized_origins(cors_client):
    """Garante que origens arbitrárias e potencialmente maliciosas não recebam cabeçalho de liberação."""
    headers = {
        "Origin": "https://atacante-malicioso.com",
        "Access-Control-Request-Method": "POST",
    }
    response = cors_client.options("/api/health", headers=headers)
    assert response.headers.get("access-control-allow-origin") is None


def test_cors_custom_origins_from_environment(tmp_path, monkeypatch):
    """Garante que a variável de ambiente CADERNO_CORS_ORIGINS configure corretamente as origens permitidas."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    monkeypatch.setenv("CADERNO_CORS_ORIGINS", "https://app.leitorum.com, https://estudos.meu-dominio.com")

    db_file = tmp_path / "test_cors_custom.db"
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
        # Origem customizada 1 permitida
        res1 = client.options(
            "/api/health",
            headers={"Origin": "https://app.leitorum.com", "Access-Control-Request-Method": "GET"},
        )
        assert res1.status_code == 200
        assert res1.headers.get("access-control-allow-origin") == "https://app.leitorum.com"

        # Origem não configurada rejeitada
        res2 = client.options(
            "/api/health",
            headers={"Origin": "https://outro-site.com", "Access-Control-Request-Method": "GET"},
        )
        assert res2.headers.get("access-control-allow-origin") is None
