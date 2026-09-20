"""Testes automatizados isolados para Busca Global Contextual (F08).

Valida busca transversal com insensibilidade a acentos, geração de snippets destacados,
combinação AND/OR, filtros de livro e categoria, exclusão de soft delete e histórico de buscas.
"""
from datetime import UTC, datetime, timedelta
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.book import Book
from app.models.category import Category
from app.models.chapter import Chapter
from app.models.study import Study


@pytest.fixture
def client_and_db(tmp_path):
    """Configura base SQLite temporária e TestClient 100% isolado em tmp_path."""
    db_path = tmp_path / "acervo_search_test" / "caderno.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

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


def test_search_validation_and_empty(client_and_db):
    """Valida rejeição de consultas curtas e resposta vazia."""
    client, _ = client_and_db

    # Consulta com menos de 2 caracteres -> 422
    res = client.get("/api/search", params={"q": "a"})
    assert res.status_code == 422

    # Consulta com 2 caracteres em base vazia -> 200 com lista vazia
    res = client.get("/api/search", params={"q": "ab"})
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "ab"
    assert data["total"] == 0
    assert data["results"] == []
    assert data["suggest_or"] is False


def test_search_accent_insensitive_and_snippets(client_and_db):
    """Valida busca com insensibilidade a acentos (UDF unaccent) e realce em snippets."""
    client, engine = client_and_db

    with Session(engine) as session:
        b1 = Book(title="Crítica da Razão Pura", author="Immanuel Kant")
        session.add(b1)
        session.flush()

        c1 = Chapter(book=b1, name="Estética Transcendental", position=1)
        session.add(c1)
        session.flush()

        s1 = Study(
            chapter=c1,
            title="A Lógica Transcendental e o Juízo Sintético a Priori",
            summary="Uma investigação aprofundada sobre a lógica formal e a intuição pura do tempo.",
            explanation="O desdobramento das categorias do entendimento na constituição da experiência empírica.",
            concepts="Juízo sintético a priori, intuição sensível, lógica transcendental.",
            references="Kant, B130.",
            notes="Minhas reflexões sobre a dialética das ilusões da metafísica dogmática.",
            reading_status="revisado",
        )
        session.add(s1)
        session.commit()

    # Busca termo sem acento: "logica" deve achar "lógica"
    res = client.get("/api/search", params={"q": "logica"})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    item = data["results"][0]
    assert item["study_title"] == "A Lógica Transcendental e o Juízo Sintético a Priori"
    assert item["book_title"] == "Crítica da Razão Pura"
    assert item["chapter_name"] == "Estética Transcendental"
    assert item["reading_status"] == "revisado"
    assert '<mark class="search-highlight">' in item["snippet"]
    assert "lógica" in item["snippet"].lower()

    # Busca termo acentuado: "dialética" deve achar "dialética" nas anotações
    res2 = client.get("/api/search", params={"q": "dialética"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["total"] == 1
    assert data2["results"][0]["matched_field"] == "Anotações"
    assert '<mark class="search-highlight">dialética</mark>' in data2["results"][0]["snippet"]


def test_search_multi_terms_and_or_modes(client_and_db):
    """Valida conjunção AND, disjunção OR e sugestão assistida suggest_or."""
    client, engine = client_and_db

    with Session(engine) as session:
        b = Book(title="Filosofia Sistemática", author="Autor A")
        session.add(b)
        session.flush()

        c = Chapter(book=b, name="Capítulo 1", position=1)
        session.add(c)
        session.flush()

        s1 = Study(
            chapter=c,
            title="Razão Pura e Epistemologia",
            summary="Trabalha a ideia de razão pura na filosofia.",
            reading_status="em_estudo",
        )
        s2 = Study(
            chapter=c,
            title="Razão Prática e Ética",
            summary="Trabalha a ideia de razão prática e o imperativo categórico.",
            reading_status="concluido",
        )
        session.add_all([s1, s2])
        session.commit()

    # 1. Termo compartilhado: "razão" encontra ambos
    res = client.get("/api/search", params={"q": "razão", "mode": "and"})
    assert res.status_code == 200
    assert res.json()["total"] == 2

    # 2. Conjunção estrita (AND): "razão pura" encontra apenas s1
    res_and = client.get("/api/search", params={"q": "razão pura", "mode": "and"})
    assert res_and.status_code == 200
    assert res_and.json()["total"] == 1
    assert res_and.json()["results"][0]["study_title"] == "Razão Pura e Epistemologia"

    # 3. Termos disjuntos ("pura prática") em modo AND: 0 resultados, mas suggest_or deve ser True
    res_empty = client.get("/api/search", params={"q": "pura prática", "mode": "and"})
    assert res_empty.status_code == 200
    assert res_empty.json()["total"] == 0
    assert res_empty.json()["suggest_or"] is True

    # 4. Modo OR para "pura prática": encontra ambos
    res_or = client.get("/api/search", params={"q": "pura prática", "mode": "or"})
    assert res_or.status_code == 200
    assert res_or.json()["total"] == 2


def test_search_filters_book_and_category(client_and_db):
    """Valida filtros contextuais por book_id e category_id."""
    client, engine = client_and_db

    with Session(engine) as session:
        cat_filo = session.execute(
            Category.__table__.select().where(Category.id == "filosofia")
        ).first()

        b1 = Book(title="Tratado Teológico-Político", author="Spinoza")
        b2 = Book(title="Tratado da Natureza Humana", author="Hume")
        session.add_all([b1, b2])
        session.flush()

        if cat_filo:
            b1.categories.append(session.get(Category, cat_filo.id))

        c1 = Chapter(book=b1, name="Capítulo 1", position=1)
        c2 = Chapter(book=b2, name="Capítulo 1", position=1)
        session.add_all([c1, c2])
        session.flush()

        s1 = Study(chapter=c1, title="Conceito de Substância em Spinoza", summary="Análise de substância.")
        s2 = Study(chapter=c2, title="Conceito de Substância em Hume", summary="Crítica da substância.")
        session.add_all([s1, s2])
        session.commit()
        b1_id, b2_id = b1.id, b2.id
        cat_id = cat_filo.id if cat_filo else None

    # Busca geral "substancia" encontra os 2
    res = client.get("/api/search", params={"q": "substancia"})
    assert res.json()["total"] == 2

    # Filtrar por Livro 1
    res_b1 = client.get("/api/search", params={"q": "substancia", "book_id": b1_id})
    assert res_b1.json()["total"] == 1
    assert res_b1.json()["results"][0]["book_id"] == b1_id

    # Filtrar por Categoria (se houver categoria semeada)
    if cat_id:
        res_cat = client.get("/api/search", params={"q": "substancia", "category_id": cat_id})
        assert res_cat.json()["total"] == 1
        assert res_cat.json()["results"][0]["book_id"] == b1_id


def test_search_ignores_soft_deleted_items(client_and_db):
    """Valida que estudos ou livros na lixeira são omitidos da busca."""
    client, engine = client_and_db
    now = datetime.now(UTC)

    with Session(engine) as session:
        b_active = Book(title="Livro Ativo", author="Autor")
        b_deleted = Book(title="Livro Excluído", author="Autor", deleted_at=now)
        session.add_all([b_active, b_deleted])
        session.flush()

        c_active = Chapter(book=b_active, name="Cap 1", position=1)
        c_deleted_book = Chapter(book=b_deleted, name="Cap 1", position=1)
        session.add_all([c_active, c_deleted_book])
        session.flush()

        # Estudo ativo em livro ativo
        s_ok = Study(chapter=c_active, title="Estudo Visível sobre Epistemologia", summary="Texto válido.")
        # Estudo deletado em livro ativo
        s_trash = Study(chapter=c_active, title="Estudo Lixeira sobre Epistemologia", summary="Texto lixeira.", deleted_at=now)
        # Estudo ativo em livro deletado
        s_in_deleted_book = Study(chapter=c_deleted_book, title="Estudo Orfão sobre Epistemologia", summary="Livro deletado.")

        session.add_all([s_ok, s_trash, s_in_deleted_book])
        session.commit()

    # Busca por "Epistemologia" deve retornar exclusivamente s_ok
    res = client.get("/api/search", params={"q": "epistemologia"})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["results"][0]["study_title"] == "Estudo Visível sobre Epistemologia"


def test_search_history_lifecycle(client_and_db):
    """Valida o registro, listagem, retenção e limpeza do histórico de buscas."""
    client, engine = client_and_db

    with Session(engine) as session:
        b = Book(title="Livro de Teste", author="Autor")
        session.add(b)
        session.flush()
        c = Chapter(book=b, name="Cap 1", position=1)
        session.add(c)
        session.flush()
        s = Study(chapter=c, title="Estudo com Palavra Chave", summary="Conteúdo.")
        session.add(s)
        session.commit()

    # Histórico inicial vazio
    res = client.get("/api/search/history")
    assert res.status_code == 200
    assert res.json()["items"] == []

    # Executa busca que encontra resultado -> registra no histórico
    client.get("/api/search", params={"q": "palavra chave"})
    res2 = client.get("/api/search/history")
    items = res2.json()["items"]
    assert len(items) == 1
    assert items[0]["query"] == "palavra chave"
    history_id = items[0]["id"]

    # Re-pesquisa termo existente -> atualiza timestamp, não duplica
    client.get("/api/search", params={"q": "palavra chave"})
    res3 = client.get("/api/search/history")
    items3 = res3.json()["items"]
    assert len(items3) == 1
    assert items3[0]["id"] == history_id

    # Remover termo individual
    del_res = client.delete(f"/api/search/history/{history_id}")
    assert del_res.status_code == 200
    assert client.get("/api/search/history").json()["items"] == []

    # Remover termo inexistente -> 404
    del_404 = client.delete(f"/api/search/history/{history_id}")
    assert del_404.status_code == 404

    # Limpar todo o histórico
    client.get("/api/search", params={"q": "palavra chave"})
    assert len(client.get("/api/search/history").json()["items"]) == 1
    clear_res = client.delete("/api/search/history")
    assert clear_res.status_code == 200
    assert client.get("/api/search/history").json()["items"] == []
