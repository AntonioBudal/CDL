from __future__ import annotations

from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.rate_limiter import auth_rate_limiter
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.db.types import utc_now
from app.main import app
from app.models.local_credential import LocalCredential
from app.models.user import User


@pytest.fixture(autouse=True)
def clean_rate_limiter():
    auth_rate_limiter.reset()
    yield
    auth_rate_limiter.reset()


def test_anti_enumeration_same_error_for_existing_and_non_existing_users(tmp_path, monkeypatch):
    """Garante que a mensagem de erro é idêntica para usuário existente com senha errada e usuário inexistente."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")

    db_file = tmp_path / "test_anti_enumeration.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with session_factory() as s:
        user = User(
            id="11111111-1111-1111-1111-111111111111",
            username="leitor_existente",
            email="leitor@exemplo.com",
            display_name="Leitor Existente",
            status="ativo",
        )
        cred = LocalCredential(
            user_id=user.id,
            password_hash=hash_password("SenhaCorreta123!"),
        )
        s.add_all([user, cred])
        s.commit()

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
            # 1. Usuário existente, senha incorreta
            resp1 = client.post(
                "/api/auth/login",
                json={"username_or_email": "leitor_existente", "password": "SenhaIncorreta999!"},
                headers={"X-Forwarded-For": "10.0.0.1"},
            )
            assert resp1.status_code == 401

            # 2. Usuário que não existe
            resp2 = client.post(
                "/api/auth/login",
                json={"username_or_email": "usuario_fantasma_inexistente", "password": "QualquerSenha123!"},
                headers={"X-Forwarded-For": "10.0.0.2"},
            )
            assert resp2.status_code == 401

            # As mensagens e estruturas de erro devem ser rigorosamente idênticas
            assert resp1.json() == resp2.json()
            assert "Credenciais inválidas" in resp1.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_account_lockout_after_consecutive_failures(tmp_path, monkeypatch):
    """Valida que após 5 falhas consecutivas para a mesma conta, ela é bloqueada temporariamente (locked_until)."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("RATE_LIMIT_MAX_ATTEMPTS", "5")
    monkeypatch.setenv("LOCKOUT_DURATION_SECONDS", "900")

    db_file = tmp_path / "test_lockout.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with session_factory() as s:
        user = User(
            id="22222222-2222-2222-2222-222222222222",
            username="alvo_forca_bruta",
            email="alvo@exemplo.com",
            display_name="Alvo Força Bruta",
            status="ativo",
            failed_login_attempts=0,
        )
        cred = LocalCredential(
            user_id=user.id,
            password_hash=hash_password("SenhaSuperSecreta123!"),
        )
        s.add_all([user, cred])
        s.commit()

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
            # Dispara 5 falhas vindas de IPs diferentes para contornar o rate limit de IP e testar o lockout de conta
            for i in range(5):
                resp = client.post(
                    "/api/auth/login",
                    json={"username_or_email": "alvo_forca_bruta", "password": "SenhaErrada!"},
                    headers={"X-Forwarded-For": f"10.0.1.{i}"},
                )
                assert resp.status_code == 401

            # Verifica se o usuário no banco agora tem 5 falhas e locked_until definido
            with session_factory() as s:
                db_user = s.get(User, "22222222-2222-2222-2222-222222222222")
                assert db_user.failed_login_attempts >= 5
                assert db_user.locked_until is not None
                assert db_user.locked_until > utc_now()

            # 6ª tentativa mesmo com a SENHA CORRETA deve ser bloqueada por conta travada
            resp_locked = client.post(
                "/api/auth/login",
                json={"username_or_email": "alvo_forca_bruta", "password": "SenhaSuperSecreta123!"},
                headers={"X-Forwarded-For": "10.0.2.1"},
            )
            assert resp_locked.status_code == 401
            assert "bloqueada" in resp_locked.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
