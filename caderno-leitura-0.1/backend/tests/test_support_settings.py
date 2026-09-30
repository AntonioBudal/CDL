from __future__ import annotations

from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.audit_log import AuditLog
from app.models.support_setting import SupportSetting
from app.models.user import User


@pytest.fixture
def support_client(tmp_path, monkeypatch) -> Generator[tuple[TestClient, sessionmaker, str, str], None, None]:
    """Cria um cliente de testes hermético em banco temporário com usuários admin e comum."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    db_file = tmp_path / "test_support.db"
    engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

    admin_id = DEFAULT_OWNER_ID
    regular_id = "11111111-1111-1111-1111-111111111111"

    with testing_session_local() as session:
        admin_user = User(
            id=admin_id,
            username=DEFAULT_OWNER_USERNAME,
            display_name="Proprietário Admin",
            role="admin",
            status="ativo",
        )
        regular_user = User(
            id=regular_id,
            username="leitor_comum",
            display_name="Leitor Comum",
            role="user",
            status="ativo",
        )
        session.add_all([admin_user, regular_user])
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
        yield client, testing_session_local, admin_id, regular_id

    application.dependency_overrides.clear()
    engine.dispose()


def test_public_support_endpoint_default_empty(support_client):
    client, _, _, _ = support_client
    res = client.get("/api/support")
    assert res.status_code == 200
    data = res.json()
    assert data["pix_enabled"] is False
    assert data["alternative_enabled"] is False
    assert data["has_any_method_active"] is False
    assert data["pix_key"] is None


def test_public_support_fallback_to_environment(support_client, monkeypatch):
    client, _, _, _ = support_client
    monkeypatch.setenv("SUPPORT_PIX_ENABLED", "true")
    monkeypatch.setenv("SUPPORT_PIX_KEY", "doacao@leitorum.org")
    monkeypatch.setenv("SUPPORT_PIX_RECIPIENT", "Mantenedor do Leitorum")
    monkeypatch.setenv("SUPPORT_ALTERNATIVE_ENABLED", "true")
    monkeypatch.setenv("SUPPORT_ALTERNATIVE_LABEL", "Google Pay")
    monkeypatch.setenv("SUPPORT_ALTERNATIVE_URL", "https://pay.google.com/exemplo")

    res = client.get("/api/support")
    assert res.status_code == 200
    data = res.json()
    assert data["pix_enabled"] is True
    assert data["pix_key"] == "doacao@leitorum.org"
    assert data["pix_recipient_name"] == "Mantenedor do Leitorum"
    assert data["alternative_enabled"] is True
    assert data["alternative_label"] == "Google Pay"
    assert data["alternative_url"] == "https://pay.google.com/exemplo"
    assert data["has_any_method_active"] is True


def test_admin_support_crud_and_precedence_over_env(support_client, monkeypatch):
    client, session_factory, admin_id, _ = support_client

    # Define env para validar que o banco tem precedência quando salvo
    monkeypatch.setenv("SUPPORT_PIX_KEY", "chave_do_env@leitorum.org")

    # 1. Consulta admin inicial
    res_admin_get = client.get(
        "/api/admin/support",
        headers={"X-User-Id": admin_id},
    )
    assert res_admin_get.status_code == 200
    data_admin = res_admin_get.json()
    assert data_admin["source"] in ("environment", "default")

    # 2. Atualização via PUT pelo admin
    payload = {
        "pix_enabled": True,
        "pix_key": "chave_banco@leitorum.org",
        "pix_recipient_name": "Titular Oficial do Banco",
        "pix_qr_code_url": "data:image/png;base64,sintetico",
        "alternative_enabled": True,
        "alternative_label": "Apoio Alternativo",
        "alternative_url": "https://apoie.exemplo.com",
        "custom_message": "Obrigado pelo incentivo ao desenvolvimento.",
    }
    res_put = client.put(
        "/api/admin/support",
        headers={"X-User-Id": admin_id},
        json=payload,
    )
    assert res_put.status_code == 200
    saved = res_put.json()
    assert saved["source"] == "database"
    assert saved["pix_key"] == "chave_banco@leitorum.org"
    assert saved["updated_by_name"] == "Proprietário Admin"

    # 3. Endpoint público reflete os dados do banco (sobrepondo o env)
    res_pub = client.get("/api/support")
    assert res_pub.status_code == 200
    pub_data = res_pub.json()
    assert pub_data["pix_key"] == "chave_banco@leitorum.org"
    assert pub_data["has_any_method_active"] is True


def test_admin_support_unauthorized_and_forbidden(support_client):
    client, _, _, regular_id = support_client

    # 1. Anônimo tentando acessar rotas admin
    res_anon_get = client.get("/api/admin/support")
    assert res_anon_get.status_code in (401, 403)

    res_anon_put = client.put("/api/admin/support", json={"pix_enabled": False, "alternative_enabled": False})
    assert res_anon_put.status_code in (401, 403)

    # 2. Usuário regular tentando acessar rotas admin
    res_user_get = client.get("/api/admin/support", headers={"X-User-Id": regular_id})
    assert res_user_get.status_code == 403

    res_user_put = client.put(
        "/api/admin/support",
        headers={"X-User-Id": regular_id},
        json={"pix_enabled": False, "alternative_enabled": False},
    )
    assert res_user_put.status_code == 403


def test_admin_support_audit_log_created(support_client):
    client, session_factory, admin_id, _ = support_client

    payload = {
        "pix_enabled": True,
        "pix_key": "auditoria@leitorum.org",
        "pix_recipient_name": "Audit Recipient",
        "alternative_enabled": False,
        "alternative_label": None,
        "alternative_url": None,
        "custom_message": None,
    }
    res = client.put(
        "/api/admin/support",
        headers={"X-User-Id": admin_id},
        json=payload,
    )
    assert res.status_code == 200

    with session_factory() as session:
        logs = session.execute(
            select(AuditLog).where(AuditLog.event_type == "admin.support_settings_updated")
        ).scalars().all()
        assert len(logs) >= 1
        last_log = logs[-1]
        assert last_log.user_id == admin_id
        assert "auditoria@leitorum.org" not in (last_log.details or "") or "pix_enabled" in (last_log.details or "")
