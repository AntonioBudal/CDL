from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.db.types import utc_now
from app.main import create_app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.local_credential import LocalCredential
from app.models.study import Study
from app.models.user import User
from app.models.user_session import UserSession

ADMIN_ID = "00000000-0000-0000-0000-000000000001"
ADMIN_2_ID = "00000000-0000-0000-0000-000000000002"
USER_REGULAR_ID = "00000000-0000-0000-0000-000000000003"
USER_REGULAR_2_ID = "00000000-0000-0000-0000-000000000004"


@pytest.fixture
def admin_harness(tmp_path: Path, monkeypatch):
    """Fixture hermética com banco SQLite temporário isolado para testes de administração."""
    avatars_dir = tmp_path / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CADERNO_AVATARS_DIR", str(avatars_dir))
    monkeypatch.setenv("REQUIRE_AUTH", "true")

    db_path = tmp_path / "admin_test.db"
    db_url = f"sqlite:///{db_path.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with testing_session_local() as db_session:
        admin = User(
            id=ADMIN_ID,
            username="superadmin",
            email="admin@caderno.local",
            display_name="Super Administrador",
            role="admin",
            status="ativo",
        )
        admin2 = User(
            id=ADMIN_2_ID,
            username="secondadmin",
            email="admin2@caderno.local",
            display_name="Segundo Administrador",
            role="admin",
            status="ativo",
        )
        user_reg = User(
            id=USER_REGULAR_ID,
            username="leitorcomum",
            email="leitor@exemplo.com",
            display_name="Leitor Comum",
            role="user",
            status="ativo",
        )
        user_reg2 = User(
            id=USER_REGULAR_2_ID,
            username="outroestudioso",
            email="estudos@exemplo.com",
            display_name="Outro Estudioso",
            role="user",
            status="ativo",
        )
        db_session.add_all([admin, admin2, user_reg, user_reg2])
        db_session.flush()

        c1 = LocalCredential(user_id=admin.id, password_hash=hash_password("AdminSecret123"))
        c2 = LocalCredential(user_id=admin2.id, password_hash=hash_password("AdminSecret456"))
        c3 = LocalCredential(user_id=user_reg.id, password_hash=hash_password("LeitorSecret123"))
        c4 = LocalCredential(user_id=user_reg2.id, password_hash=hash_password("LeitorSecret456"))
        db_session.add_all([c1, c2, c3, c4])

        # Adiciona estudos e livros para teste de métricas
        book = Book(
            title="Livro de Teste",
            author="Autor Teste",
            user_id=USER_REGULAR_ID,
        )
        db_session.add(book)
        db_session.flush()

        chapter = Chapter(
            book_id=book.id,
            name="Capítulo 1",
        )
        db_session.add(chapter)
        db_session.flush()

        study = Study(
            title="Estudo do Leitor",
            chapter_id=chapter.id,
            user_id=USER_REGULAR_ID,
            summary="Resumo de teste para análise de leitura.",
        )
        db_session.add(study)

        # Adiciona sessões ativas
        now = utc_now()
        s1 = UserSession(
            user_id=USER_REGULAR_ID,
            session_token_hash="hash_s1",
            device_name="Chrome no Windows",
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 Windows",
            expires_at=now + timedelta(days=30),
        )
        s2 = UserSession(
            user_id=USER_REGULAR_ID,
            session_token_hash="hash_s2",
            device_name="Chrome no Android",
            ip_address="192.168.1.50",
            user_agent="Mozilla/5.0 Android",
            expires_at=now + timedelta(days=30),
        )
        db_session.add_all([s1, s2])
        db_session.commit()

    app = create_app()

    def override_get_session():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)

    yield {
        "client": client,
        "session_factory": testing_session_local,
        "engine": engine,
    }

    app.dependency_overrides.clear()


# ==============================================================================
# Phase 2 / US1: Painel de Gestão e Blindagem 403
# ==============================================================================

def test_regular_user_forbidden_from_admin_endpoints(admin_harness: dict[str, Any]):
    """Usuário convencional com role='user' recebe 403 Forbidden em todos os endpoints /api/admin."""
    client: TestClient = admin_harness["client"]
    headers = {"X-User-Id": USER_REGULAR_ID}

    res = client.get("/api/admin/users", headers=headers)
    assert res.status_code == 403
    assert res.json()["detail"] == "Acesso restrito a administradores."

    res = client.get("/api/admin/stats", headers=headers)
    assert res.status_code == 403

    res = client.post(f"/api/admin/users/{USER_REGULAR_2_ID}/suspend", headers=headers)
    assert res.status_code == 403


def test_anonymous_unauthorized_from_admin_endpoints(admin_harness: dict[str, Any]):
    """Requisição anônima sem credenciais recebe 401 Unauthorized."""
    client: TestClient = admin_harness["client"]
    res = client.get("/api/admin/users")
    assert res.status_code == 401


def test_admin_can_list_users_with_filters_and_pagination(admin_harness: dict[str, Any]):
    """Administrador autenticado lista usuários, aplica filtros por status/role e busca textual."""
    client: TestClient = admin_harness["client"]
    headers = {"X-User-Id": ADMIN_ID}

    # Listagem geral
    res = client.get("/api/admin/users", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4

    # Busca por texto no username
    res = client.get("/api/admin/users?q=leitorcomum", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["username"] == "leitorcomum"
    assert data["items"][0]["studies_count"] == 1
    assert data["items"][0]["books_count"] == 1
    assert data["items"][0]["active_sessions_count"] == 2

    # Filtro por role=admin
    res = client.get("/api/admin/users?role=admin", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert all(item["role"] == "admin" for item in data["items"])

    # Filtro por status=ativo
    res = client.get("/api/admin/users?status=ativo", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] == 4


def test_admin_stats_summary(admin_harness: dict[str, Any]):
    """Endpoint de estatísticas retorna agregações globais da base."""
    client: TestClient = admin_harness["client"]
    headers = {"X-User-Id": ADMIN_ID}

    res = client.get("/api/admin/stats", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_users"] == 4
    assert data["active_users"] == 4
    assert data["suspended_users"] == 0
    assert data["admin_users"] == 2
    assert data["total_studies"] == 1


# ==============================================================================
# Phase 3 / US2: Moderação, Suspensão Atômica e Reativação
# ==============================================================================

def test_suspend_user_atomically_revokes_sessions(admin_harness: dict[str, Any]):
    """Suspender usuário marca status='suspenso' e revoga imediatamente todas as sessões ativas."""
    client: TestClient = admin_harness["client"]
    session_factory = admin_harness["session_factory"]
    headers = {"X-User-Id": ADMIN_ID}

    # Verifica que o leitor possui 2 sessões ativas
    with session_factory() as session:
        sessions = session.scalars(
            select(UserSession).where(UserSession.user_id == USER_REGULAR_ID)
        ).all()
        assert len(sessions) == 2

    # Suspende o usuário
    res = client.post(
        f"/api/admin/users/{USER_REGULAR_ID}/suspend",
        headers=headers,
        json={"reason": "Violação de regras de uso"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "suspenso"
    assert data["sessions_revoked"] == 2

    # Verifica banco de dados: status suspenso e 0 sessões
    with session_factory() as session:
        user = session.get(User, USER_REGULAR_ID)
        assert user.status == "suspenso"
        remaining_sessions = session.scalars(
            select(UserSession).where(UserSession.user_id == USER_REGULAR_ID)
        ).all()
        assert len(remaining_sessions) == 0

    # O usuário suspenso não consegue mais fazer chamadas autenticadas (HTTP 401)
    res = client.get("/api/books", headers={"X-User-Id": USER_REGULAR_ID})
    assert res.status_code == 401
    assert "inativo" in res.json()["detail"].lower() or "não autenticado" in res.json()["detail"].lower()


def test_reactivate_suspended_user(admin_harness: dict[str, Any]):
    """Reativar usuário devolve status='ativo', permitindo novas requisições."""
    client: TestClient = admin_harness["client"]
    session_factory = admin_harness["session_factory"]
    admin_headers = {"X-User-Id": ADMIN_ID}

    # Suspende
    client.post(f"/api/admin/users/{USER_REGULAR_ID}/suspend", headers=admin_headers)

    # Reativa
    res = client.post(f"/api/admin/users/{USER_REGULAR_ID}/reactivate", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "ativo"

    # Confirma status ativo no banco
    with session_factory() as session:
        user = session.get(User, USER_REGULAR_ID)
        assert user.status == "ativo"

    # Usuário volta a ter acesso com X-User-Id
    res = client.get("/api/books", headers={"X-User-Id": USER_REGULAR_ID})
    assert res.status_code == 200


def test_revoke_all_sessions_endpoint(admin_harness: dict[str, Any]):
    """Endpoint de desconexão forçada remove todas as sessões sem suspender a conta."""
    client: TestClient = admin_harness["client"]
    session_factory = admin_harness["session_factory"]
    admin_headers = {"X-User-Id": ADMIN_ID}

    res = client.post(
        f"/api/admin/users/{USER_REGULAR_ID}/sessions/revoke-all",
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["sessions_revoked"] == 2

    # Verifica que a conta continua 'ativo', mas as sessões foram zeradas
    with session_factory() as session:
        user = session.get(User, USER_REGULAR_ID)
        assert user.status == "ativo"
        sessions = session.scalars(
            select(UserSession).where(UserSession.user_id == USER_REGULAR_ID)
        ).all()
        assert len(sessions) == 0


# ==============================================================================
# Phase 4 / US3: Gestão de Papéis e Salvaguardas Anti-Lockout
# ==============================================================================

def test_admin_cannot_suspend_self(admin_harness: dict[str, Any]):
    """Administrador não pode suspender a própria conta (400 Bad Request)."""
    client: TestClient = admin_harness["client"]
    headers = {"X-User-Id": ADMIN_ID}

    res = client.post(f"/api/admin/users/{ADMIN_ID}/suspend", headers=headers)
    assert res.status_code == 400
    assert "própria conta" in res.json()["detail"].lower()


def test_cannot_suspend_only_active_admin(admin_harness: dict[str, Any]):
    """Não é possível suspender o único administrador ativo do sistema."""
    client: TestClient = admin_harness["client"]
    admin_headers = {"X-User-Id": ADMIN_ID}

    # Rebaixa admin2 para user
    client.put(
        f"/api/admin/users/{ADMIN_2_ID}/role",
        headers=admin_headers,
        json={"role": "user"},
    )

    # Agora ADMIN_ID é o único admin ativo. Tentar suspendê-lo via requisição autenticada
    # (ou por outro meio) falharia por auto-suspensão. Mas se outro tentar suspender o único admin:
    # Vamos rebaixar ADMIN_ID e deixar ADMIN_2_ID como único admin, e ADMIN_ID tenta suspender ADMIN_2_ID:
    # Mais simples: admin2 agora é user. Vamos promover admin2 de volta para admin e desativar admin:
    # Testamos update_user_role direto ou suspend_user:
    from app.services.admin_service import suspend_user
    session_factory = admin_harness["session_factory"]
    with session_factory() as session:
        # Agora só existe 1 admin ativo (ADMIN_ID)
        admin_user = session.get(User, ADMIN_ID)
        # Tenta suspender ADMIN_ID passando um pseudo-current-user diferente para testar a salvaguarda
        other_user = session.get(User, USER_REGULAR_ID)
        with pytest.raises(Exception) as exc_info:
            suspend_user(session, target_user_id=ADMIN_ID, current_user=other_user)
        assert "único administrador" in str(exc_info.value.detail).lower()


def test_role_change_and_last_admin_demotion_prevention(admin_harness: dict[str, Any]):
    """Promover usuário a admin funciona; rebaixar o único admin é rejeitado com 400."""
    client: TestClient = admin_harness["client"]
    admin_headers = {"X-User-Id": ADMIN_ID}

    # 1. Promove leitor comum a admin
    res = client.put(
        f"/api/admin/users/{USER_REGULAR_ID}/role",
        headers=admin_headers,
        json={"role": "admin"},
    )
    assert res.status_code == 200
    assert res.json()["role"] == "admin"

    # 2. Rebaixa admin2 a user (há ADMIN_ID e USER_REGULAR_ID como admins, então é permitido)
    res = client.put(
        f"/api/admin/users/{ADMIN_2_ID}/role",
        headers=admin_headers,
        json={"role": "user"},
    )
    assert res.status_code == 200
    assert res.json()["role"] == "user"

    # 3. Rebaixa leitor comum de volta a user (ADMIN_ID ainda é admin, então é permitido)
    res = client.put(
        f"/api/admin/users/{USER_REGULAR_ID}/role",
        headers=admin_headers,
        json={"role": "user"},
    )
    assert res.status_code == 200
    assert res.json()["role"] == "user"

    # 4. Agora ADMIN_ID é o ÚNICO admin restante. Tentar rebaixá-lo deve retornar 400!
    res = client.put(
        f"/api/admin/users/{ADMIN_ID}/role",
        headers=admin_headers,
        json={"role": "user"},
    )
    assert res.status_code == 400
    assert "único administrador" in res.json()["detail"].lower()


# ==============================================================================
# Phase 5 / US4: CLI de Provisionamento do Primeiro Administrador
# ==============================================================================

def test_cli_create_admin_script(admin_harness: dict[str, Any], monkeypatch):
    """Testa a lógica do script create_admin.py para criar novo admin ou promover existente."""
    try:
        from backend.scripts.create_admin import run_create_admin
    except ImportError:
        from scripts.create_admin import run_create_admin
    session_factory = admin_harness["session_factory"]

    # 1. Cria novo admin via CLI
    with session_factory() as session:
        new_admin = run_create_admin(
            session=session,
            username="cli_admin",
            email="cli@caderno.local",
            password="CliStrongPassword123!",
            display_name="Admin do CLI",
        )
        assert new_admin.username == "cli_admin"
        assert new_admin.role == "admin"
        assert new_admin.status == "ativo"
        assert new_admin.has_password is True

    # 2. Promove leitor existente via CLI
    with session_factory() as session:
        promoted = run_create_admin(
            session=session,
            target_username="outroestudioso",
        )
        assert promoted.username == "outroestudioso"
        assert promoted.role == "admin"
