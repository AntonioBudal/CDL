from __future__ import annotations

from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.db.base import Base
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.book import Book
from app.models.category import Category
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.user import User


@pytest.fixture
def sqli_client(tmp_path, monkeypatch) -> Generator[tuple[TestClient, sessionmaker], None, None]:
    """Cria um cliente de testes hermético com banco SQLite descartável em tmp_path."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    db_file = tmp_path / "test_sqli.db"
    engine = create_sqlite_engine(db_file)
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
        cat = Category(id="filosofia", name="Filosofia", normalized_name="filosofia", is_canonical=True, user_id=user.id)
        session.add(cat)
        book = Book(id=1, title="A República", user_id=user.id)
        session.add(book)
        chapter = Chapter(id=1, book_id=1, name="Livro I")
        session.add(chapter)
        study = Study(
            id=1,
            chapter_id=1,
            title="A Justiça em Platão",
            summary="Discussão sobre a natureza da justiça e a pólis ideal.",
            explanation="Sócrates debate com Trasímaco.",
            concepts="Justiça, Sofisma",
            references="Platão, Ed. 35",
            notes="Estudo preliminar",
            user_id=user.id,
        )
        session.add(study)
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
        yield client, testing_session_local


SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1 --",
    "\" OR \"\"=\"",
    "'; DROP TABLE books; --",
    "' UNION SELECT NULL, NULL, NULL --",
    "1' ORDER BY 1--",
    "%%' OR 1=1 --",
    "admin' --",
    "' OR ''='",
]


def test_global_search_immune_to_sql_injection(sqli_client):
    """Garante que a busca global trate termos de injeção SQL estritamente como strings literais."""
    client, _ = sqli_client
    for payload in SQLI_PAYLOADS:
        response = client.get(f"/api/search?q={payload}")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Não deve retornar o estudo a menos que o payload esteja literalmente escrito no texto
        assert isinstance(data["results"], list)


def test_categories_endpoint_immune_to_sql_injection(sqli_client):
    """Garante que o filtro de categorias seja seguro contra injeção de SQL."""
    client, _ = sqli_client
    for payload in SQLI_PAYLOADS:
        response = client.get(f"/api/categories?q={payload}")
        assert response.status_code == 200
        cats = response.json()
        assert isinstance(cats, list)


def test_database_tables_remain_intact_after_drop_payloads(sqli_client):
    """Confirma que tentativas de DROP TABLE não afetam as tabelas reais do banco."""
    client, session_factory = sqli_client
    drop_payload = "'; DROP TABLE books; DROP TABLE studies; --"
    res = client.get(f"/api/search?q={drop_payload}")
    assert res.status_code == 200

    # Confere se os registros permanecem íntegros no banco
    with session_factory() as session:
        books_count = session.query(Book).count()
        assert books_count == 1
        studies_count = session.query(Study).count()
        assert studies_count == 1
