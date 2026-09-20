"""Testes automatizados isolados para busca e ordenação de livros no backend (/api/books)."""
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.book import Book


@pytest.fixture
def client_and_db(tmp_path, monkeypatch):
    """Configura ambiente hermético com banco SQLite efêmero em tmp_path."""
    db_path = tmp_path / "acervo_test" / "caderno.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(db_path))

    # Executa todas as migrações no banco temporário
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.attributes["database_path"] = db_path
    command.upgrade(alembic_cfg, "head")

    engine = create_sqlite_engine(db_path)
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session

    try:
        with TestClient(application) as client:
            yield client, engine
    finally:
        engine.dispose()


def test_list_books_default_order(client_and_db):
    """Testa que listagem padrão de livros funciona sem parâmetros."""
    client, _ = client_and_db

    # Cria dois livros
    client.post("/api/books", json={"title": "Livro B", "author": "Autor B"})
    client.post("/api/books", json={"title": "Livro A", "author": "Autor A"})

    res = client.get("/api/books")
    assert res.status_code == 200
    books = res.json()
    assert len(books) == 2


def test_list_books_query_filter(client_and_db):
    """Testa busca textual no backend via parâmetro ?q=."""
    client, _ = client_and_db

    client.post("/api/books", json={"title": "A Arte da Guerra", "author": "Sun Tzu", "subtitle": "Estrategia Militar"})
    client.post("/api/books", json={"title": "Dom Casmurro", "author": "Machado de Assis"})

    # Busca por título
    res_title = client.get("/api/books?q=Guerra")
    assert res_title.status_code == 200
    assert len(res_title.json()) == 1
    assert res_title.json()[0]["title"] == "A Arte da Guerra"

    # Busca por autor
    res_author = client.get("/api/books?q=machado")
    assert res_author.status_code == 200
    assert len(res_author.json()) == 1
    assert res_author.json()[0]["author"] == "Machado de Assis"

    # Busca por subtítulo
    res_sub = client.get("/api/books?q=estrategia")
    assert res_sub.status_code == 200
    assert len(res_sub.json()) == 1


def test_list_books_sorting(client_and_db):
    """Testa ordenação por título A-Z e Z-A via ?sort= e ?order=."""
    client, _ = client_and_db

    client.post("/api/books", json={"title": "Zadig", "author": "Voltaire"})
    client.post("/api/books", json={"title": "Antígona", "author": "Sófocles"})

    # Título ASC
    res_asc = client.get("/api/books?sort=title&order=asc")
    assert res_asc.status_code == 200
    assert res_asc.json()[0]["title"] == "Antígona"
    assert res_asc.json()[1]["title"] == "Zadig"

    # Título DESC
    res_desc = client.get("/api/books?sort=title&order=desc")
    assert res_desc.status_code == 200
    assert res_desc.json()[0]["title"] == "Zadig"
    assert res_desc.json()[1]["title"] == "Antígona"


def test_list_books_filters_out_trash_items(client_and_db):
    """Garante que itens na lixeira nunca aparecem na listagem mesmo com busca ou ordenação."""
    client, _ = client_and_db

    res1 = client.post("/api/books", json={"title": "Livro Ativo"})
    res2 = client.post("/api/books", json={"title": "Livro Excluido"})
    trash_id = res2.json()["id"]

    # Envia para a lixeira
    client.post(f"/api/books/{trash_id}/trash")

    # Busca que combinaria com o livro excluído
    res_search = client.get("/api/books?q=Excluido")
    assert res_search.status_code == 200
    assert len(res_search.json()) == 0

    # Listagem geral
    res_all = client.get("/api/books")
    assert len(res_all.json()) == 1
    assert res_all.json()[0]["title"] == "Livro Ativo"
