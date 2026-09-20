import uuid

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.user import User


@pytest.fixture
def isolation_env(tmp_path):
    path = tmp_path / "multiuser-isolation-test.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)

    # Cria dois usuários para os testes: Usuário A (proprietário padrão) e Usuário B
    user_b_id = str(uuid.uuid4())
    with Session(engine) as session:
        user_b = User(
            id=user_b_id,
            username="leitor_b",
            display_name="Leitor B",
            status="ativo",
        )
        session.add(user_b)
        session.commit()

    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session

    with TestClient(application) as client:
        yield client, engine, DEFAULT_OWNER_ID, user_b_id

    engine.dispose()


def test_book_list_isolation(isolation_env):
    client, _, user_a_id, user_b_id = isolation_env

    # Usuário A cria livro
    client.post("/api/books", json={"title": "Livro Exclusivo de A", "author": "Autor A"})

    # Usuário B cria livro
    client.post(
        "/api/books",
        json={"title": "Livro Secreto de B", "author": "Autor B"},
        headers={"X-User-Id": user_b_id},
    )

    # Consulta de A
    resp_a = client.get("/api/books")
    assert resp_a.status_code == 200
    titles_a = [b["title"] for b in resp_a.json()]
    assert "Livro Exclusivo de A" in titles_a
    assert "Livro Secreto de B" not in titles_a

    # Consulta de B
    resp_b = client.get("/api/books", headers={"X-User-Id": user_b_id})
    assert resp_b.status_code == 200
    titles_b = [b["title"] for b in resp_b.json()]
    assert "Livro Secreto de B" in titles_b
    assert "Livro Exclusivo de A" not in titles_b


def test_category_hybrid_isolation(isolation_env):
    client, _, _, user_b_id = isolation_env

    # B cria categoria pessoal
    client.post(
        "/api/categories",
        json={"id": "privada-de-b", "name": "Categoria Privada de B"},
        headers={"X-User-Id": user_b_id},
    )

    # A lista categorias -> não deve ver a de B, mas vê as globais
    resp_a = client.get("/api/categories")
    cat_ids_a = [c["id"] for c in resp_a.json()]
    assert "privada-de-b" not in cat_ids_a

    # B lista categorias -> vê a sua categoria privada e as globais
    resp_b = client.get("/api/categories", headers={"X-User-Id": user_b_id})
    cat_ids_b = [c["id"] for c in resp_b.json()]
    assert "privada-de-b" in cat_ids_b


def test_search_and_history_isolation(isolation_env):
    client, _, _, user_b_id = isolation_env

    # B cria livro, capítulo e estudo com texto específico
    r_book_b = client.post("/api/books", json={"title": "Física Quântica"}, headers={"X-User-Id": user_b_id})
    b_id = r_book_b.json()["id"]
    r_chap_b = client.post(f"/api/books/{b_id}/chapters", json={"name": "Cap 1"}, headers={"X-User-Id": user_b_id})
    ch_id = r_chap_b.json()["id"]
    client.post(
        "/api/studies",
        json={"chapter_id": ch_id, "title": "Emaranhamento Quântico", "summary": "Partículas entrelaçadas"},
        headers={"X-User-Id": user_b_id},
    )

    # A busca por "Emaranhamento" -> 0 resultados
    r_search_a = client.get("/api/search?q=Emaranhamento")
    assert r_search_a.status_code == 200
    assert len(r_search_a.json()["results"]) == 0

    # B busca por "Emaranhamento" -> 1 resultado
    r_search_b = client.get("/api/search?q=Emaranhamento", headers={"X-User-Id": user_b_id})
    assert r_search_b.status_code == 200
    assert len(r_search_b.json()["results"]) == 1

    # Histórico de pesquisas de A deve estar vazio
    r_hist_a = client.get("/api/search/recent")
    assert r_hist_a.status_code == 200
    queries_a = [h["query"] for h in r_hist_a.json()["items"]]
    assert "Emaranhamento" not in queries_a


def test_dashboard_metrics_isolation(isolation_env):
    client, _, _, user_b_id = isolation_env

    # A cria 1 livro
    client.post("/api/books", json={"title": "Livro do Usuário A"})

    # B cria 2 livros
    client.post("/api/books", json={"title": "Livro 1 de B"}, headers={"X-User-Id": user_b_id})
    client.post("/api/books", json={"title": "Livro 2 de B"}, headers={"X-User-Id": user_b_id})

    # Dashboard de A deve reportar 1 livro
    dash_a = client.get("/api/dashboard").json()
    assert dash_a["summary"]["total_books"] == 1

    # Dashboard de B deve reportar 2 livros
    dash_b = client.get("/api/dashboard", headers={"X-User-Id": user_b_id}).json()
    assert dash_b["summary"]["total_books"] == 2


def test_trash_list_isolation(isolation_env):
    client, _, _, user_b_id = isolation_env

    # A cria livro e move para lixeira
    r_a = client.post("/api/books", json={"title": "Livro Descartado por A"})
    b_id_a = r_a.json()["id"]
    client.post(f"/api/books/{b_id_a}/trash")

    # B consulta lixeira -> não vê o livro de A
    trash_b = client.get("/api/trash", headers={"X-User-Id": user_b_id}).json()
    trash_b_books = [item["id"] for item in trash_b["books"]]
    assert b_id_a not in trash_b_books

    # A consulta lixeira -> vê seu livro
    trash_a = client.get("/api/trash").json()
    trash_a_books = [item["id"] for item in trash_a["books"]]
    assert b_id_a in trash_a_books


def test_unauthorized_edit_delete_restore(isolation_env):
    client, _, _, user_b_id = isolation_env

    # 1. Usuário A cria livro, capítulo e estudo
    r_book_a = client.post("/api/books", json={"title": "Obra Magna de A", "author": "Autor A"})
    b_id_a = r_book_a.json()["id"]

    r_chap_a = client.post(f"/api/books/{b_id_a}/chapters", json={"name": "Capítulo 1"})
    ch_id_a = r_chap_a.json()["id"]

    r_study_a = client.post(
        "/api/studies",
        json={
            "chapter_id": ch_id_a,
            "title": "Estudo Original de A",
            "summary": "Resumo do estudo",
            "notes": "Notas confidenciais",
        },
    )
    assert r_study_a.status_code == 201
    s_id_a = r_study_a.json()["id"]

    # 2. Usuário B tenta editar livro de A -> 404
    r_patch_book = client.patch(
        f"/api/books/{b_id_a}",
        json={"title": "Título Modificado por B"},
        headers={"X-User-Id": user_b_id},
    )
    assert r_patch_book.status_code == 404
    assert r_patch_book.json()["detail"] == "Livro não encontrado."

    # Verifica que título não mudou
    assert client.get(f"/api/books/{b_id_a}").json()["title"] == "Obra Magna de A"

    # 3. Usuário B tenta mover livro de A para lixeira -> 404
    r_trash_book = client.post(f"/api/books/{b_id_a}/trash", headers={"X-User-Id": user_b_id})
    assert r_trash_book.status_code == 404

    # 4. Usuário B tenta excluir permanentemente livro de A -> 404
    r_perm_book = client.delete(f"/api/books/{b_id_a}/permanent", headers={"X-User-Id": user_b_id})
    assert r_perm_book.status_code == 404

    # 5. Usuário B tenta editar estudo de A -> 404
    r_patch_study = client.patch(
        f"/api/studies/{s_id_a}",
        json={"title": "Estudo Invadido por B", "summary": "Alterado"},
        headers={"X-User-Id": user_b_id},
    )
    assert r_patch_study.status_code == 404
    assert r_patch_study.json()["detail"] == "Estudo não encontrado."

    # 6. Usuário B tenta mover estudo de A para lixeira -> 404
    r_trash_study = client.post(f"/api/studies/{s_id_a}/trash", headers={"X-User-Id": user_b_id})
    assert r_trash_study.status_code == 404

    # 7. Usuário B tenta excluir permanentemente estudo de A -> 404
    r_perm_study = client.delete(f"/api/studies/{s_id_a}/permanent", headers={"X-User-Id": user_b_id})
    assert r_perm_study.status_code == 404

    # 8. Usuário A descarta seu próprio livro e estudo
    client.post(f"/api/studies/{s_id_a}/trash")
    client.post(f"/api/books/{b_id_a}/trash")

    # 9. Usuário B tenta restaurar o livro e o estudo de A -> 404 em ambas as rotas
    assert client.post(f"/api/books/{b_id_a}/restore", headers={"X-User-Id": user_b_id}).status_code == 404
    assert client.post(f"/api/trash/books/{b_id_a}/restore", headers={"X-User-Id": user_b_id}).status_code == 404
    assert client.post(f"/api/studies/{s_id_a}/restore", headers={"X-User-Id": user_b_id}).status_code == 404
    assert client.post(f"/api/trash/studies/{s_id_a}/restore", headers={"X-User-Id": user_b_id}).status_code == 404


def test_category_deletion_protection(isolation_env):
    client, _, _, user_b_id = isolation_env

    # 1. Tentativa de excluir categoria padrão global do sistema -> 403 Forbidden
    r_del_global = client.delete("/api/categories/filosofia")
    assert r_del_global.status_code == 403
    assert "Categorias padrão do sistema não podem ser excluídas." in r_del_global.json()["detail"]

    # 2. Usuário B cria categoria personalizada
    client.post(
        "/api/categories",
        json={"id": "custom-cat-b", "name": "Minha Categoria B"},
        headers={"X-User-Id": user_b_id},
    )

    # 3. Usuário A tenta excluir categoria de B -> 404
    r_del_other = client.delete("/api/categories/custom-cat-b")
    assert r_del_other.status_code == 404
    assert r_del_other.json()["detail"] == "Categoria não encontrada."

    # 4. Usuário B exclui sua própria categoria -> 204 No Content
    r_del_own = client.delete("/api/categories/custom-cat-b", headers={"X-User-Id": user_b_id})
    assert r_del_own.status_code == 204


def test_anti_idor_uniform_404(isolation_env):
    client, _, _, user_b_id = isolation_env

    # Usuário A cria um livro e estudo
    r_book = client.post("/api/books", json={"title": "Livro Privado", "author": "Autor Privado"})
    book_id = r_book.json()["id"]

    r_chap = client.post(f"/api/books/{book_id}/chapters", json={"name": "Cap 1"})
    chap_id = r_chap.json()["id"]

    r_study = client.post(
        "/api/studies",
        json={"chapter_id": chap_id, "title": "Estudo Privado", "summary": "Resumo privado"},
    )
    assert r_study.status_code == 201
    study_id = r_study.json()["id"]

    # Validação da uniformidade da resposta (ID existente de outro vs ID inexistente)
    # 1. Livro
    r_nonexistent_book = client.get("/api/books/999999")
    r_foreign_book = client.get(f"/api/books/{book_id}", headers={"X-User-Id": user_b_id})

    assert r_nonexistent_book.status_code == 404
    assert r_foreign_book.status_code == 404
    assert r_nonexistent_book.json() == r_foreign_book.json() == {"detail": "Livro não encontrado."}

    # 2. Estudo
    r_nonexistent_study = client.get("/api/studies/999999")
    r_foreign_study = client.get(f"/api/studies/{study_id}", headers={"X-User-Id": user_b_id})

    assert r_nonexistent_study.status_code == 404
    assert r_foreign_study.status_code == 404
    assert r_nonexistent_study.json() == r_foreign_study.json() == {"detail": "Estudo não encontrado."}

    # 3. Exportações
    assert client.get(f"/api/books/{book_id}/export", headers={"X-User-Id": user_b_id}).status_code == 404
    assert client.get(f"/api/studies/{study_id}/export", headers={"X-User-Id": user_b_id}).status_code == 404

    # 4. Capas
    assert client.delete(f"/api/books/{book_id}/cover", headers={"X-User-Id": user_b_id}).status_code == 404
