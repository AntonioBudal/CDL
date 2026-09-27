from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.local_credential import LocalCredential
from app.models.study import Study
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.user_profile import UserProfile


@pytest.fixture
def account_test_client(tmp_path, monkeypatch):
    """Cliente hermético com banco isolado e leitor para testes de ciclo de vida."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")

    db_file = tmp_path / "test_lifecycle.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with session_factory() as s:
        user = User(
            id="lifecycle-user-1111",
            username="leitor_ciclo",
            email="leitor.ciclo@exemplo.com",
            display_name="Leitor Ciclo",
            role="user",
            status="ativo",
        )
        cred = LocalCredential(
            user_id=user.id,
            password_hash=hash_password("SenhaCiclo123!"),
        )
        profile = UserProfile(
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            bio="Bio de teste",
        )
        pref = UserPreference(
            user_id=user.id,
            active_superclass="mecanica",
        )
        book = Book(
            id=1,
            user_id=user.id,
            title="Livro do Ciclo",
            author="Autor Teste",
        )
        chapter = Chapter(
            id=1,
            book_id=1,
            name="Capítulo 1",
            position=1,
        )
        study = Study(
            id=1,
            chapter_id=1,
            user_id=user.id,
            title="Estudo do Ciclo",
            summary="Conteúdo do estudo para deleção em cascata",
        )
        s.add_all([user, cred, profile, pref, book, chapter, study])
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


def test_deactivate_and_reactivate_explicit_flow(account_test_client):
    """Testa o ciclo completo: login -> desativação -> bloqueio com 403 -> reativação explícita (Opção B)."""
    client, session_factory = account_test_client

    # 1. Login inicial
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_ciclo", "password": "SenhaCiclo123!"},
    )
    assert login_res.status_code == 200

    # 2. Desativação com senha incorreta -> falha 400
    deact_fail = client.post("/api/account/deactivate", json={"password": "senha_errada"})
    assert deact_fail.status_code == 400
    assert "Senha incorreta" in deact_fail.json()["detail"]

    # 3. Desativação com senha correta -> sucesso 200
    deact_ok = client.post("/api/account/deactivate", json={"password": "SenhaCiclo123!"})
    assert deact_ok.status_code == 200
    assert deact_ok.json()["ok"] is True

    # 4. Tentativa de login após desativação -> HTTP 403 com ACCOUNT_DEACTIVATED
    login_after_deact = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_ciclo", "password": "SenhaCiclo123!"},
    )
    assert login_after_deact.status_code == 403
    err_data = login_after_deact.json()
    assert err_data.get("code") == "ACCOUNT_DEACTIVATED"

    # 5. Confirmação explícita de reativação -> POST /api/account/reactivate
    reactivate_res = client.post(
        "/api/account/reactivate",
        json={"username_or_email": "leitor_ciclo", "password": "SenhaCiclo123!"},
    )
    assert reactivate_res.status_code == 200
    assert reactivate_res.json()["user"]["status"] == "ativo"

    # 6. Novo login funciona normalmente
    login_after_react = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_ciclo", "password": "SenhaCiclo123!"},
    )
    assert login_after_react.status_code == 200


def test_delete_account_permanently_cascades_all_data(account_test_client):
    """Testa exclusão definitiva em cascata física transacional no SQLite (LGPD - Opção A)."""
    client, session_factory = account_test_client

    # 1. Login
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_ciclo", "password": "SenhaCiclo123!"},
    )
    assert login_res.status_code == 200

    # 2. Confirmação incorreta -> 400
    del_fail = client.request(
        "DELETE",
        "/api/account",
        json={"confirmation_text": "texto_incorreto", "password": "SenhaCiclo123!"},
    )
    assert del_fail.status_code == 400

    # 3. Exclusão confirmada com sucesso
    del_ok = client.request(
        "DELETE",
        "/api/account",
        json={"confirmation_text": "leitor_ciclo", "password": "SenhaCiclo123!"},
    )
    assert del_ok.status_code == 200
    assert del_ok.json()["ok"] is True

    # 4. Valida purga física em cascata no banco de dados
    with session_factory() as s:
        assert s.get(User, "lifecycle-user-1111") is None
        assert s.scalar(select(Book).where(Book.user_id == "lifecycle-user-1111")) is None
        assert s.scalar(select(Chapter).where(Chapter.id == 1)) is None
        assert s.scalar(select(Study).where(Study.user_id == "lifecycle-user-1111")) is None
        assert s.scalar(select(UserProfile).where(UserProfile.user_id == "lifecycle-user-1111")) is None
        assert s.scalar(select(UserPreference).where(UserPreference.user_id == "lifecycle-user-1111")) is None
