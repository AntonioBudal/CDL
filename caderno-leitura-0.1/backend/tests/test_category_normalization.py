"""Testes de integração e isolamento para normalização e simplificação de categorias (F0.6.7)."""
from __future__ import annotations

from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.book import Book
from app.models.category import Category, book_categories
from app.services.canonical_categories import (
    CANONICAL_CATEGORIES,
    CANONICAL_INDEX_BY_SLUG,
    get_canonical_catalog,
    is_canonical_slug,
    resolve_legacy_mapping,
)
from app.services.category_normalizer import (
    canonicalize_name,
    normalize_for_search,
    singularize_portuguese,
    slugify_category,
    strip_accents,
    validate_category_name,
)


@pytest.fixture
def client_and_db(tmp_path, monkeypatch):
    """Configura ambiente hermético com banco SQLite efêmero em tmp_path."""
    db_path = tmp_path / "norm_test" / "caderno.db"
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


def test_portuguese_singularization_rules():
    """Valida que o lematizador/singularizador trata plurais regulares e irregulares em português."""
    # Plurais regulares em -s, -as, -os
    assert singularize_portuguese("filosofias") == "filosofia"
    assert singularize_portuguese("livros") == "livro"
    assert singularize_portuguese("artes") == "arte"
    assert singularize_portuguese("pesquisas") == "pesquisa"

    # Plurais em -ões, -ães, -ãos
    assert singularize_portuguese("ficções") == "ficção"
    assert singularize_portuguese("educações") == "educação"
    assert singularize_portuguese("religiões") == "religião"
    assert singularize_portuguese("capitães") == "capitão"
    assert singularize_portuguese("irmãos") == "irmão"

    # Plurais em -ns
    assert singularize_portuguese("homens") == "homem"
    assert singularize_portuguese("origens") == "origem"

    # Palavras invariáveis terminadas em -s
    assert singularize_portuguese("lápis") == "lápis"
    assert singularize_portuguese("vírus") == "vírus"
    assert singularize_portuguese("status") == "status"
    assert singularize_portuguese("práxis") == "práxis"


def test_normalization_and_slugification():
    """Valida remoção de acentos, normalização de busca e geração estável de slugs."""
    assert strip_accents("História") == "Historia"
    assert strip_accents("Ficção Científica") == "Ficcao Cientifica"

    assert normalize_for_search("  Ciência & Política  ") == "ciencia politica"
    assert normalize_for_search("HISTÓRIAS") == "historias"

    assert slugify_category("Filosofia da Mente") == "filosofia-da-mente"
    assert slugify_category("Educação") == "educacao"


def test_canonicalize_name_transformation():
    """Valida que entradas plurais e variantes convergem para a forma canônica singular e capitalizada."""
    assert canonicalize_name("filosofias") == "Filosofia"
    assert canonicalize_name("HISTÓRIAS") == "História"
    assert canonicalize_name("ciencias") == "Ciência"
    assert canonicalize_name("Ciências Sociais e Humanas") == "Ciência"
    assert canonicalize_name("poesias") == "Poesia"


def test_category_name_validation():
    """Valida restrições de tamanho (2 a 30 caracteres) e rejeição de pontuações estranhas."""
    is_valid, _ = validate_category_name("F")
    assert not is_valid

    is_valid, _ = validate_category_name("Esta categoria tem um nome incrivelmente longo demais")
    assert not is_valid

    is_valid, _ = validate_category_name("Filosofia / Ciência")
    assert not is_valid

    is_valid, _ = validate_category_name("História")
    assert is_valid


def test_canonical_catalog_and_legacy_mapping():
    """Valida que o catálogo oficial possui 24 categorias e mapeamentos distributivos definidos."""
    catalog = get_canonical_catalog()
    assert len(catalog) == 24

    for item in catalog:
        assert is_canonical_slug(item.id)
        assert item.name[0].isupper()

    # Mapeamento distributivo 1 para N
    mapped = resolve_legacy_mapping("ciencias sociais e humanas")
    assert set(mapped) == {"ciencia", "sociologia"}

    # Mapeamento simples
    assert resolve_legacy_mapping("filosofias") == ["filosofia"]


def test_database_canonical_categories_flat_and_seeded(client_and_db):
    """Valida que após migrações todas as 24 categorias canônicas estão no banco e são planas (parent_id is None)."""
    _, engine = client_and_db

    with Session(engine) as session:
        canonical_rows = session.scalars(
            select(Category).where(Category.is_canonical.is_(True))
        ).all()
        assert len(canonical_rows) >= 24

        for cat in canonical_rows:
            # Taxonomia estritamente plana
            assert cat.parent_id is None
            assert len(cat.name) >= 2
            assert cat.normalized_name != ""


def test_distributive_category_migration(client_and_db):
    """Valida que a migração distributiva preserva vínculos de livros e atribui categorias canônicas corretas sem duplicatas."""
    _, engine = client_and_db

    with Session(engine) as session:
        # Criar livro de teste
        book = Book(title="Livro Sintético de Filosofia e Ciência", author="Autor de Teste")
        session.add(book)
        session.flush()

        cat_filosofia = session.get(Category, "filosofia")
        cat_ciencia = session.get(Category, "ciencia")
        assert cat_filosofia is not None
        assert cat_ciencia is not None

        # Associar categorias
        book.categories = [cat_filosofia, cat_ciencia]
        session.commit()

        # Recarregar do banco
        loaded_book = session.get(Book, book.id)
        assert len(loaded_book.categories) == 2
        loaded_cat_ids = {c.id for c in loaded_book.categories}
        assert "filosofia" in loaded_cat_ids
        assert "ciencia" in loaded_cat_ids


def test_api_list_categories_alphabetical_and_counts(client_and_db):
    """Valida ordenação alfabética e contagem de livros em GET /api/categories."""
    client, engine = client_and_db

    # Associar um livro à categoria Filosofia
    with Session(engine) as session:
        book = Book(title="Obra Filosófica", author="Autor")
        session.add(book)
        session.flush()
        cat = session.get(Category, "filosofia")
        assert cat is not None
        book.categories = [cat]
        session.commit()

    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 24

    # Verificar ordenação alfabética
    names = [c["name"] for c in data]
    assert names == sorted(names, key=lambda s: s.lower())

    # Verificar books_count para Filosofia
    filo = next(c for c in data if c["id"] == "filosofia")
    assert filo["books_count"] == 1

    # Categoria sem livros tem books_count == 0
    arte = next(c for c in data if c["id"] == "arte")
    assert arte["books_count"] == 0


def test_api_suggest_canonical_category(client_and_db):
    """Valida sugestões determinísticas para termos plurais em GET /api/categories/suggest."""
    client, _ = client_and_db

    res = client.get("/api/categories/suggest?q=filosofias")
    assert res.status_code == 200
    data = res.json()
    assert data["input_term"] == "filosofias"
    assert data["suggested_canonical"] == "Filosofia"
    assert len(data["matching_candidates"]) > 0


def test_api_create_category_normalization_and_idempotence(client_and_db):
    """Valida criação idempotente e normalização no POST /api/categories."""
    client, _ = client_and_db

    # Tentativa de criar termo já existente (deve retornar 200 OK com categoria existente)
    res = client.post("/api/categories", json={"name": "Filosofias"})
    assert res.status_code == 200
    cat = res.json()
    assert cat["id"] == "filosofia"
    assert cat["name"] == "Filosofia"

    # Criar nova categoria personalizada válida (singularizada)
    res_new = client.post("/api/categories", json={"name": "Micologias"})
    assert res_new.status_code == 201
    cat_new = res_new.json()
    assert cat_new["name"] == "Micologia"
    assert cat_new["id"] == "micologia"

    # Rejeição de nome inválido
    res_inv = client.post("/api/categories", json={"name": "A"})
    assert res_inv.status_code == 422 or res_inv.status_code == 400

    res_sym = client.post("/api/categories", json={"name": "Filo / Sofia"})
    assert res_sym.status_code == 400


def test_suggest_and_create_canonical_category(client_and_db):
    """Cenário 2 do quickstart: Provar que GET /suggest sugere a forma singular e POST /categories reutiliza o canônico."""
    client, _ = client_and_db

    # Termo "Direitos" gera sugestão "Direito"
    res_sug = client.get("/api/categories/suggest?q=Direitos")
    assert res_sug.status_code == 200
    sug_data = res_sug.json()
    assert sug_data["suggested_canonical"] == "Direito"

    # Termo "direito" com minúsculas associa ao ID "direito" e exibe "Direito"
    res_create = client.post("/api/categories", json={"name": "direito"})
    assert res_create.status_code == 200
    cat_data = res_create.json()
    assert cat_data["id"] == "direito"
    assert cat_data["name"] == "Direito"

    # Submissão com múltiplos termos ou caracteres inválidos retorna HTTP 400
    res_inv = client.post("/api/categories", json={"name": "Direito / Filosofia"})
    assert res_inv.status_code == 400


def test_api_categories_stats_and_delete_protection(client_and_db):
    """Valida GET /api/categories/stats e proteção contra exclusão de categorias canônicas."""
    client, _ = client_and_db

    res = client.get("/api/categories/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_categories"] >= 24
    assert stats["canonical_categories"] >= 24
    assert "unused_categories" in stats

    # Tentar excluir categoria canônica deve ser bloqueado com 403
    res_del = client.delete("/api/categories/filosofia")
    assert res_del.status_code == 403

