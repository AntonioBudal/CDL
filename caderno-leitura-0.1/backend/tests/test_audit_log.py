from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.local_credential import LocalCredential
from app.models.user import User
from app.services.audit_service import log_event, sanitize_details
from app.services.session_service import create_session, set_session_cookie


def test_sanitize_details_redacts_sensitive_keys():
    """Valida se a função sanitize_details mascara recursivamente segredos e tokens."""
    payload = {
        "username": "leitor_alvo",
        "password": "SenhaSuperSecreta123!",
        "password_hash": "$argon2id$...hash...",
        "token": "bearer-token-123",
        "api_key": "key-secret-999",
        "profile": {
            "name": "Maria",
            "access_token": "token-nested",
            "nested_dict": {
                "credential": "cred-secret",
                "normal_field": "valor_normal",
            },
        },
        "list_items": [
            {"password": "outra-senha", "item": "livro1"},
            "texto simples",
        ],
    }

    sanitized = sanitize_details(payload)

    assert sanitized["username"] == "leitor_alvo"
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["password_hash"] == "[REDACTED]"
    assert sanitized["token"] == "[REDACTED]"
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["profile"]["name"] == "Maria"
    assert sanitized["profile"]["access_token"] == "[REDACTED]"
    assert sanitized["profile"]["nested_dict"]["credential"] == "[REDACTED]"
    assert sanitized["profile"]["nested_dict"]["normal_field"] == "valor_normal"
    assert sanitized["list_items"][0]["password"] == "[REDACTED]"
    assert sanitized["list_items"][0]["item"] == "livro1"


@pytest.fixture
def audit_test_client(tmp_path, monkeypatch):
    """Cliente hermético com banco isolado, usuário admin e usuário comum."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")

    db_file = tmp_path / "test_audit.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with session_factory() as s:
        admin_user = User(
            id="admin-1111-1111-1111-111111111111",
            username="admin_auditor",
            display_name="Admin Auditor",
            role="admin",
            status="ativo",
        )
        admin_cred = LocalCredential(
            user_id=admin_user.id,
            password_hash=hash_password("AdminPass123!"),
        )
        normal_user = User(
            id="user-2222-2222-2222-222222222222",
            username="leitor_comum",
            display_name="Leitor Comum",
            role="user",
            status="ativo",
        )
        normal_cred = LocalCredential(
            user_id=normal_user.id,
            password_hash=hash_password("UserPass123!"),
        )
        s.add_all([admin_user, admin_cred, normal_user, normal_cred])
        s.commit()

        # Insere alguns logs de auditoria iniciais
        log_event(
            session=s,
            event_type="test_event_1",
            user_id=normal_user.id,
            actor_username="leitor_comum",
            details={"action": "test", "password": "should_be_redacted"},
        )
        log_event(
            session=s,
            event_type="test_event_2",
            user_id=admin_user.id,
            actor_username="admin_auditor",
            details={"action": "admin_action"},
        )
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

    with TestClient(app) as client:
        yield client, session_factory

    app.dependency_overrides.clear()
    engine.dispose()


def test_audit_logs_endpoint_rbac_and_filters(audit_test_client):
    """Testa restrição RBAC (403 para usuários não-admin) e filtros de listagem."""
    client, session_factory = audit_test_client

    # 1. Usuário comum tentando acessar -> HTTP 403 Forbidden
    login_user = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_comum", "password": "UserPass123!"},
    )
    assert login_user.status_code == 200

    resp_forbidden = client.get("/api/admin/audit-logs")
    assert resp_forbidden.status_code == 403

    # 2. Login como Admin -> HTTP 200 OK
    login_admin = client.post(
        "/api/auth/login",
        json={"username_or_email": "admin_auditor", "password": "AdminPass123!"},
    )
    assert login_admin.status_code == 200

    resp_admin = client.get("/api/admin/audit-logs")
    assert resp_admin.status_code == 200
    data = resp_admin.json()
    assert "items" in data
    assert data["total"] >= 2
    # Verifica que a senha foi sanitizada no log
    first_item = next(i for i in data["items"] if i["event_type"] == "test_event_1")
    assert first_item["details"]["password"] == "[REDACTED]"

    # 3. Filtro por event_type
    resp_filtered = client.get("/api/admin/audit-logs?event_type=test_event_2")
    assert resp_filtered.status_code == 200
    data_filtered = resp_filtered.json()
    assert all(i["event_type"] == "test_event_2" for i in data_filtered["items"])
