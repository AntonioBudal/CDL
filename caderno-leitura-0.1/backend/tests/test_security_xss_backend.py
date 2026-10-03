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
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.user import User


@pytest.fixture
def xss_backend_client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    """Cria um cliente de testes hermético com banco SQLite descartável em tmp_path."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    db_file = tmp_path / "test_xss_backend.db"
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
        book = Book(id=1, title="Livro Seguro", user_id=user.id)
        session.add(book)
        chapter = Chapter(id=1, book_id=1, name="Capítulo 1")
        session.add(chapter)
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


def test_import_parser_treats_script_tags_as_literal_text(xss_backend_client):
    """Garante que a prévia e parsing de importação com tags de script não causem execução no backend."""
    malicious_content = """# Resumo
Texto com <script>alert("xss")</script> e <img src=x onerror=alert(1)>

# Explicação
Explicação contendo [link](javascript:alert(1))

# Conceitos
- Termo 1: Conceito seguro

# Referências
- Fonte: Estudo de caso
"""
    response = xss_backend_client.post(
        "/api/imports/preview",
        json={"source_response": malicious_content},
    )
    assert response.status_code == 200
    data = response.json()
    # O backend armazena o texto fornecido sem executar nem falhar
    assert "<script>" in data["summary"]
    assert "javascript:alert(1)" in data["explanation"]


def test_create_study_with_xss_payload_persists_safely_as_data(xss_backend_client):
    """Garante que payloads XSS submetidos ao endpoint de criação de estudo são persistidos como dados literais."""
    payload = {
        "chapter_id": 1,
        "title": "Estudo com <script>alert(1)</script>",
        "summary": "Resumo <svg/onload=alert('svg')>",
        "explanation": "Explicação normal",
        "concepts": "Conceito <iframe src=javascript:alert(2)>",
        "references": "Ref segura",
        "notes": "Nota com link [evil](javascript:steal())",
    }
    response = xss_backend_client.post("/api/studies", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] is not None

    # Leitura do estudo via GET
    get_res = xss_backend_client.get(f"/api/studies/{created['id']}")
    assert get_res.status_code == 200
    study = get_res.json()
    assert study["title"] == "Estudo com <script>alert(1)</script>"
    assert "<svg/onload=" in study["summary"]
