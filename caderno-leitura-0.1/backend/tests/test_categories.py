"""Testes para taxonomia, categorias canônicas e sincronização idempotente."""
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
from app.models.category import Category, book_categories
from app.services.category_service import (
    get_descendant_category_ids,
    load_canonical_categories_from_file,
    sync_canonical_categories,
    validate_and_build_hierarchy,
)


@pytest.fixture
def client_and_db(tmp_path, monkeypatch):
    """Configura ambiente hermético com banco SQLite efêmero em tmp_path."""
    db_path = tmp_path / "categories_test" / "caderno.db"
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


def test_canonical_catalogue_integrity():
    """Valida que o arquivo canonical_categories.json contém mais de 100 categorias válidas e acíclicas."""
    categories = load_canonical_categories_from_file()
    assert len(categories) >= 100

    ids = [c["id"] for c in categories]
    assert len(ids) == len(set(ids)), "IDs não são únicos"

    # Verificar que todos os caminhos foram construídos
    for c in categories:
        assert c["path"], f"Path vazio para {c['id']}"
        assert c["name"] in c["path"], f"Nome não está no path para {c['id']}"


def test_validate_and_build_hierarchy_rejects_cycles():
    """Valida que ciclos hierárquicos são rejeitados com ValueError."""
    # Criar 100 categorias válidas + um ciclo
    entries = [{"id": f"cat-{i}", "name": f"Categoria {i}", "parent_id": None} for i in range(100)]
    entries.append({"id": "ciclo-a", "name": "Ciclo A", "parent_id": "ciclo-b"})
    entries.append({"id": "ciclo-b", "name": "Ciclo B", "parent_id": "ciclo-a"})

    with pytest.raises(ValueError, match="Ciclo hierárquico detectado"):
        validate_and_build_hierarchy(entries)


def test_validate_and_build_hierarchy_rejects_duplicates():
    """Valida que IDs duplicados são rejeitados com ValueError."""
    entries = [{"id": f"cat-{i}", "name": f"Categoria {i}", "parent_id": None} for i in range(100)]
    entries.append({"id": "cat-0", "name": "Duplicado", "parent_id": None})

    with pytest.raises(ValueError, match="Identificador duplicado"):
        validate_and_build_hierarchy(entries)


def test_sync_categories_is_idempotent(client_and_db):
    """Valida que a sincronização do catálogo é idempotente e preserva a quantidade."""
    _, engine = client_and_db

    with Session(engine) as session:
        # A migração inicial já inseriu as categorias canônicas
        count_initial = session.scalar(select(func.count()).select_from(Category))
        assert count_initial >= 100

        # Executar sync explicitamente
        sync_count = sync_canonical_categories(session)
        assert sync_count == count_initial

        count_after = session.scalar(select(func.count()).select_from(Category))
        assert count_after == count_initial

        # Executar uma segunda vez consecutiva
        sync_count_2 = sync_canonical_categories(session)
        assert sync_count_2 == count_initial
        assert session.scalar(select(func.count()).select_from(Category)) == count_initial


def test_get_descendant_category_ids_cte(client_and_db):
    """Valida a resolução recursiva de IDs via CTE no SQLite."""
    _, engine = client_and_db

    with Session(engine) as session:
        descendants = get_descendant_category_ids(session, "filosofia")
        assert "filosofia" in descendants
        assert "filosofia-etica" in descendants
        assert "filosofia-politica" in descendants
        assert len(descendants) > 5

        # Categoria folha retorna apenas ela mesma
        leaf_descendants = get_descendant_category_ids(session, "filosofia-etica")
        assert leaf_descendants == {"filosofia-etica"}


def test_book_categories_crud_and_patch_preservation(client_and_db):
    """Valida CRUD de livros com categorias e preservação em edição parcial."""
    client, _ = client_and_db

    # 1. Cadastrar livro com múltiplas categorias
    res = client.post(
        "/api/books",
        json={
            "title": "Ética a Nicômaco",
            "author": "Aristóteles",
            "category_ids": ["filosofia-etica", "filosofia-antiga"],
        },
    )
    assert res.status_code == 201
    created = res.json()
    book_id = created["id"]
    cat_ids = {c["id"] for c in created["categories"]}
    assert cat_ids == {"filosofia-etica", "filosofia-antiga"}

    # 2. Consultar livro por ID
    get_res = client.get(f"/api/books/{book_id}")
    assert get_res.status_code == 200
    assert len(get_res.json()["categories"]) == 2

    # 3. PATCH apenas de outro metadado (título/ano) sem enviar category_ids -> PRESERVA categorias
    patch_res = client.patch(
        f"/api/books/{book_id}",
        json={"title": "Ética a Nicômaco (Edição Clássica)"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Ética a Nicômaco (Edição Clássica)"
    cat_ids_after = {c["id"] for c in patch_res.json()["categories"]}
    assert cat_ids_after == {"filosofia-etica", "filosofia-antiga"}, "Categorias devem ser preservadas"

    # 4. PATCH enviando nova lista de categorias -> ATUALIZA
    patch_res_2 = client.patch(
        f"/api/books/{book_id}",
        json={"category_ids": ["filosofia"]},
    )
    assert patch_res_2.status_code == 200
    cat_ids_updated = {c["id"] for c in patch_res_2.json()["categories"]}
    assert cat_ids_updated == {"filosofia"}

    # 5. PATCH com lista vazia -> REMOVE categorias
    patch_res_3 = client.patch(
        f"/api/books/{book_id}",
        json={"category_ids": []},
    )
    assert patch_res_3.status_code == 200
    assert patch_res_3.json()["categories"] == []

    # 6. Rejeitar categoria inexistente
    err_res = client.post(
        "/api/books",
        json={"title": "Livro com Erro", "category_ids": ["categoria-inexistente-123"]},
    )
    assert err_res.status_code == 400
    assert "não existem no catálogo" in err_res.json()["detail"]


def test_category_lifecycle_with_trash(client_and_db):
    """Valida que soft delete preserva vínculos taxonômicos e exclusão definitiva expurga associações."""
    client, engine = client_and_db

    # Cadastrar livro com categoria
    res = client.post(
        "/api/books",
        json={
            "title": "A República",
            "author": "Platão",
            "category_ids": ["filosofia-politica"],
        },
    )
    assert res.status_code == 201
    book_id = res.json()["id"]

    # 1. Enviar para a lixeira
    trash_res = client.post(f"/api/books/{book_id}/trash")
    assert trash_res.status_code == 200
    assert trash_res.json()["deleted_at"] is not None

    # Verificar que na tabela associativa o vínculo continua existindo
    with Session(engine) as session:
        link_count = session.scalar(
            select(func.count()).select_from(book_categories).where(book_categories.c.book_id == book_id)
        )
        assert link_count == 1, "Vínculo de categoria deve ser mantido durante soft delete"

    # Livro na lixeira não aparece no acervo ativo
    list_res = client.get("/api/books")
    assert not any(b["id"] == book_id for b in list_res.json())

    # 2. Restaurar livro
    restore_res = client.post(f"/api/books/{book_id}/restore")
    assert restore_res.status_code == 200
    restored = restore_res.json()
    assert restored["deleted_at"] is None
    assert len(restored["categories"]) == 1
    assert restored["categories"][0]["id"] == "filosofia-politica"

    # 3. Exclusão definitiva (permanent delete)
    # Primeiro mover para a lixeira novamente
    client.post(f"/api/books/{book_id}/trash")
    perm_res = client.delete(f"/api/books/{book_id}/permanent")
    assert perm_res.status_code == 204

    # Verificar que a tabela associativa expurgou os vínculos em CASCADE
    with Session(engine) as session:
        link_count_after = session.scalar(
            select(func.count()).select_from(book_categories).where(book_categories.c.book_id == book_id)
        )
        assert link_count_after == 0, "Vínculos de book_categories devem ser expurgados em CASCADE"

        # A categoria em si no catálogo NÃO foi removida
        cat = session.get(Category, "filosofia-politica")
        assert cat is not None, "Categoria canônica não pode ser removida ao excluir livro"


def test_books_filter_by_recursive_category(client_and_db):
    """Valida o filtro recursivo/inclusivo por categoria na listagem de livros."""
    client, _ = client_and_db

    # Hierarquia canônica em canonical_categories.json:
    # Root: historia
    #   ├── historia-brasil (parent)
    #   │     ├── historia-brasil-colonia (leaf)
    #   │     └── historia-brasil-imperio (leaf)
    #   └── historia-antiga (leaf irmão)
    # Outro root: filosofia -> filosofia-etica
    b1 = client.post(
        "/api/books",
        json={"title": "Raízes do Brasil Colônia", "author": "Sérgio Buarque", "category_ids": ["historia-brasil-colonia"]},
    ).json()

    b2 = client.post(
        "/api/books",
        json={"title": "O Império das Américas", "author": "Laurentino Gomes", "category_ids": ["historia-brasil-imperio"]},
    ).json()

    b3 = client.post(
        "/api/books",
        json={"title": "História do Mundo Antigo", "author": "Susan Wise", "category_ids": ["historia-antiga"]},
    ).json()

    b4 = client.post(
        "/api/books",
        json={"title": "Ética a Nicômaco", "author": "Aristóteles", "category_ids": ["filosofia-etica"]},
    ).json()

    b5 = client.post(
        "/api/books",
        json={"title": "Livro Sem Categoria", "author": "Autor Anônimo", "category_ids": []},
    ).json()

    # 1. Filtro por categoria folha ("historia-brasil-colonia"): deve retornar apenas b1
    res_leaf = client.get("/api/books?category=historia-brasil-colonia")
    assert res_leaf.status_code == 200
    leaf_ids = [b["id"] for b in res_leaf.json()]
    assert leaf_ids == [b1["id"]]

    # 2. Filtro por categoria intermediária ("historia-brasil"): deve retornar b1 e b2
    res_parent = client.get("/api/books?category=historia-brasil")
    assert res_parent.status_code == 200
    parent_ids = {b["id"] for b in res_parent.json()}
    assert parent_ids == {b1["id"], b2["id"]}

    # 3. Filtro por categoria raiz ("historia"): deve incluir descendentes b1, b2 e b3, mas não b4 ou b5
    res_root = client.get("/api/books?category=historia")
    assert res_root.status_code == 200
    root_ids = {b["id"] for b in res_root.json()}
    assert b1["id"] in root_ids
    assert b2["id"] in root_ids
    assert b3["id"] in root_ids
    assert b4["id"] not in root_ids
    assert b5["id"] not in root_ids

    # 4. Combinação com busca textual: "category=historia-brasil" e "q=laurentino"
    res_combo = client.get("/api/books?category=historia-brasil&q=laurentino")
    assert res_combo.status_code == 200
    combo_ids = [b["id"] for b in res_combo.json()]
    assert combo_ids == [b2["id"]]

    # 5. Categoria inexistente: retorna lista vazia
    res_none = client.get("/api/books?category=categoria-fantasma-xyz")
    assert res_none.status_code == 200
    assert res_none.json() == []

    # 6. Livro movido para a lixeira não deve aparecer no filtro por categoria
    client.post(f"/api/books/{b1['id']}/trash")
    res_after_trash = client.get("/api/books?category=historia-brasil")
    assert res_after_trash.status_code == 200
    after_trash_ids = [b["id"] for b in res_after_trash.json()]
    assert b1["id"] not in after_trash_ids
    assert b2["id"] in after_trash_ids

