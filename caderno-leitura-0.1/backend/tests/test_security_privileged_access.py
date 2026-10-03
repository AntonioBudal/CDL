from datetime import timedelta
from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME, SESSION_COOKIE_NAME
from app.core.security import generate_session_token, hash_password, hash_session_token
from app.db.base import Base
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.local_credential import LocalCredential
from app.models.user import User
from app.models.user_session import UserSession
from app.db.types import utc_now


@pytest.fixture
def rbac_client(tmp_path, monkeypatch) -> Generator[tuple[TestClient, sessionmaker, str, str], None, None]:
    """Cria ambiente isolado com usuário comum e administrador para testes de RBAC."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")

    db_file = tmp_path / "test_rbac.db"
    engine = create_sqlite_engine(db_file)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

    admin_token = generate_session_token()
    user_token = generate_session_token()

    with session_factory() as session:
        # Administrador
        admin = User(
            id="admin-uuid-1",
            username="admin_user",
            display_name="Admin",
            role="admin",
            status="ativo",
        )
        session.add(admin)
        admin_session = UserSession(
            user_id=admin.id,
            session_token_hash=hash_session_token(admin_token),
            device_name="Admin Device",
            ip_address="127.0.0.1",
            user_agent="pytest",
            created_at=utc_now(),
            last_activity=utc_now(),
            expires_at=utc_now() + timedelta(days=30),
        )
        session.add(admin_session)

        # Usuário regular (leitor)
        regular = User(
            id="user-uuid-2",
            username="regular_user",
            display_name="Leitor",
            role="user",
            status="ativo",
        )
        session.add(regular)
        regular_session = UserSession(
            user_id=regular.id,
            session_token_hash=hash_session_token(user_token),
            device_name="User Device",
            ip_address="127.0.0.1",
            user_agent="pytest",
            created_at=utc_now(),
            last_activity=utc_now(),
            expires_at=utc_now() + timedelta(days=30),
        )
        session.add(regular_session)
        session.commit()

    application = create_app()

    def override_session():
        with session_factory() as s:
            yield s

    application.dependency_overrides[get_session] = override_session

    with TestClient(application) as client:
        yield client, session_factory, admin_token, user_token


def test_anonymous_access_to_backups_is_blocked_with_401(rbac_client):
    """Visitantes não autenticados recebem 401 ao tentar acessar qualquer rota de backup."""
    client, _, _, _ = rbac_client

    res_backup = client.get("/api/backup")
    assert res_backup.status_code == 401

    res_bundle = client.get("/api/backup/bundle")
    assert res_bundle.status_code == 401

    res_restore = client.post("/api/backup/restore", files={"file": ("dump.db", b"dummy")})
    assert res_restore.status_code == 401


def test_regular_user_access_to_backups_is_forbidden_with_403(rbac_client):
    """Usuários autenticados com papel comum (role='user') recebem 403 Forbidden ao tentar acessar backups."""
    client, _, _, user_token = rbac_client
    auth_headers = {"Cookie": f"{SESSION_COOKIE_NAME}={user_token}"}

    res_backup = client.get("/api/backup", headers=auth_headers)
    assert res_backup.status_code == 403
    assert "Acesso restrito a administradores" in res_backup.json()["detail"]

    res_bundle = client.get("/api/backup/bundle", headers=auth_headers)
    assert res_bundle.status_code == 403

    res_restore = client.post("/api/backup/restore", files={"file": ("dump.db", b"dummy")}, headers=auth_headers)
    assert res_restore.status_code == 403


def test_admin_user_has_authorized_access_to_backups(rbac_client):
    """Usuários com papel de administrador têm acesso autorizado a backups."""
    client, _, admin_token, _ = rbac_client
    auth_headers = {"Cookie": f"{SESSION_COOKIE_NAME}={admin_token}"}

    res_backup = client.get("/api/backup", headers=auth_headers)
    assert res_backup.status_code == 200
    assert "caderno-" in res_backup.headers.get("content-disposition", "")

    res_bundle = client.get("/api/backup/bundle", headers=auth_headers)
    assert res_bundle.status_code == 200
    assert ".zip" in res_bundle.headers.get("content-disposition", "")
