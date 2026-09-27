from __future__ import annotations

import io
import json
import zipfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.audit_log import AuditLog
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.local_credential import LocalCredential
from app.models.study import Study
from app.models.user import User
from app.models.user_profile import UserProfile


@pytest.fixture
def export_test_client(tmp_path, monkeypatch):
    """Cliente hermético com banco isolado e leitor para testes de exportação do acervo."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")

    db_file = tmp_path / "test_export.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with session_factory() as s:
        user = User(
            id="export-user-2222",
            username="leitor_exportador",
            email="exportador@exemplo.com",
            display_name="Leitor Exportador",
            role="user",
            status="ativo",
        )
        cred = LocalCredential(
            user_id=user.id,
            password_hash=hash_password("SenhaExport123!"),
        )
        profile = UserProfile(
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            bio="Bio de teste de exportação",
        )
        book = Book(
            id=10,
            user_id=user.id,
            title="Livro de Ouro",
            author="Filósofo Clássico",
            subtitle="Uma introdução à sabedoria",
            year=2024,
        )
        chapter = Chapter(
            id=20,
            book_id=10,
            name="Capítulo I - Princípios",
            position=1,
        )
        study = Study(
            id=30,
            chapter_id=20,
            user_id=user.id,
            title="Estudo da Virtude",
            location="Página 42",
            summary="Resumo essencial sobre as virtudes cardeais.",
            notes="Minhas notas de reflexão pessoal.",
        )
        s.add_all([user, cred, profile, book, chapter, study])
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


def test_export_account_data_requires_auth(export_test_client):
    """Garante que requisição não autenticada a /api/account/export retorne 401."""
    client, _ = export_test_client
    res = client.get("/api/account/export")
    assert res.status_code == 401


def test_export_account_data_zip_structure_and_audit(export_test_client):
    """Garante compilação e integridade do pacote ZIP com pastas e dados_acervo.json."""
    client, session_factory = export_test_client

    # 1. Login
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": "leitor_exportador", "password": "SenhaExport123!"},
    )
    assert login_res.status_code == 200

    # 2. Requisição de exportação
    res = client.get("/api/account/export")
    assert res.status_code == 200
    assert "zip" in res.headers.get("content-type", "").lower()
    disposition = res.headers.get("content-disposition", "")
    assert "caderno-dados-leitor_exportador" in disposition
    assert disposition.endswith('.zip"') or disposition.endswith(".zip")

    # 3. Validação do arquivo ZIP
    zip_bytes = io.BytesIO(res.content)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        # Verifica integridade (testzip retorna None se ok)
        assert zf.testzip() is None

        file_list = zf.namelist()
        assert "dados_acervo.json" in file_list

        # Verifica conteúdo do JSON
        json_data = json.loads(zf.read("dados_acervo.json").decode("utf-8"))
        assert json_data["user"]["username"] == "leitor_exportador"
        assert json_data["user"]["email"] == "exportador@exemplo.com"
        assert json_data["total_books"] == 1
        assert json_data["total_chapters"] == 1
        assert json_data["total_studies"] == 1
        assert len(json_data["books"]) == 1
        assert json_data["books"][0]["title"] == "Livro de Ouro"

        # Verifica árvore de pastas e arquivo Markdown do estudo
        md_files = [f for f in file_list if f.endswith(".md")]
        assert len(md_files) == 1
        md_path = md_files[0]
        # Deve ter estrutura [Livro]/[Capítulo]/[Estudo].md
        parts = md_path.split("/")
        assert len(parts) == 3
        md_content = zf.read(md_path).decode("utf-8")
        assert "Estudo da Virtude" in md_content
        assert "Resumo essencial sobre as virtudes cardeais." in md_content
        assert "Minhas notas de reflexão pessoal." in md_content

    # 4. Verifica registro de auditoria
    with session_factory() as s:
        audit_log = s.scalar(
            select(AuditLog)
            .where(AuditLog.user_id == "export-user-2222")
            .where(AuditLog.event_type == "account_exported")
        )
        assert audit_log is not None
        assert audit_log.actor_username == "leitor_exportador"
