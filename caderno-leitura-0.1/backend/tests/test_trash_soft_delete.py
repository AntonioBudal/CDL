"""Testes automatizados isolados de lixeira, soft delete, restauração e purga temporal."""
from datetime import UTC, datetime, timedelta
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from sqlalchemy.orm import Session


@pytest.fixture
def client_and_db(tmp_path):
    """Configura base SQLite temporária e TestClient 100% isolado."""
    db_path = tmp_path / "acervo_lixeira" / "caderno.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Executa migrações no banco temporário
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
            yield client, db_path
    finally:
        engine.dispose()


def create_sample_book_with_studies(client) -> dict:
    """Helper sintético para criar livro, capítulo e estudos."""
    # 1. Cria livro
    res_book = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autor Sintético"})
    assert res_book.status_code == 201
    book_id = res_book.json()["id"]

    # 2. Cria capítulo
    res_chap = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_chap.status_code == 201
    chapter_id = res_chap.json()["id"]

    # 3. Cria estudos
    res_study1 = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo 1",
            "summary": "Resumo sintético do estudo 1.",
            "location": "p. 10",
        },
    )
    assert res_study1.status_code == 201
    study1_id = res_study1.json()["id"]

    res_study2 = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo 2",
            "summary": "Resumo sintético do estudo 2.",
            "location": "p. 20",
        },
    )
    assert res_study2.status_code == 201
    study2_id = res_study2.json()["id"]

    return {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "study1_id": study1_id,
        "study2_id": study2_id,
    }


def test_trash_book_hides_from_active_queries(client_and_db):
    """T008 [US1]: Mover livro para lixeira oculta o livro do acervo ativo."""
    client, _ = client_and_db
    sample = create_sample_book_with_studies(client)
    book_id = sample["book_id"]

    # Descarte do livro
    res = client.post(f"/api/books/{book_id}/trash")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == book_id
    assert data["deleted_at"] is not None

    # Verifica se sumiu de /api/books
    list_res = client.get("/api/books")
    assert list_res.status_code == 200
    books = list_res.json()
    assert not any(b["id"] == book_id for b in books)

    # Verifica se detalhe retorna 404
    detail_res = client.get(f"/api/books/{book_id}")
    assert detail_res.status_code == 404

    # Descartar novamente retorna 400
    res_repeat = client.post(f"/api/books/{book_id}/trash")
    assert res_repeat.status_code == 400


def test_trash_individual_study_hides_from_book(client_and_db):
    """T008 [US1]: Mover estudo individual para a lixeira oculta apenas ele do capítulo."""
    client, _ = client_and_db
    sample = create_sample_book_with_studies(client)
    book_id = sample["book_id"]
    study1_id = sample["study1_id"]
    study2_id = sample["study2_id"]

    # Descarte do estudo 1
    res = client.post(f"/api/studies/{study1_id}/trash")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == study1_id
    assert data["deleted_at"] is not None

    # Livro continua ativo
    detail_res = client.get(f"/api/books/{book_id}")
    assert detail_res.status_code == 200

    # Capítulo lista apenas o estudo 2 (estudo 1 está na lixeira)
    chap_res = client.get(f"/api/chapters/{sample['chapter_id']}/studies")
    assert chap_res.status_code == 200
    all_studies = [s["id"] for s in chap_res.json()]
    assert study1_id not in all_studies
    assert study2_id in all_studies

    # Consulta direta ao estudo retorna 404
    study_res = client.get(f"/api/studies/{study1_id}")
    assert study_res.status_code == 404

    # Descartar novamente retorna 400
    res_repeat = client.post(f"/api/studies/{study1_id}/trash")
    assert res_repeat.status_code == 400


def test_get_trash_lists_books_and_studies(client_and_db):
    """T014 [US2]: GET /api/trash retorna resumo agregado e itens descartados com dias restantes."""
    client, _ = client_and_db
    sample1 = create_sample_book_with_studies(client)
    sample2 = create_sample_book_with_studies(client)

    # Descarta livro 1 inteiro (com 2 estudos)
    client.post(f"/api/books/{sample1['book_id']}/trash")

    # Descarta apenas o estudo 1 do livro 2
    client.post(f"/api/studies/{sample2['study1_id']}/trash")

    res = client.get("/api/trash")
    assert res.status_code == 200
    data = res.json()

    assert "total_items" in data
    assert "books" in data
    assert "studies" in data
    assert data["total_items"] == 2

    # Livro 1 deve estar em books
    book_ids = [b["id"] for b in data["books"]]
    assert sample1["book_id"] in book_ids

    # O estudo avulso descartado do livro 2 deve estar em studies
    study_ids = [s["id"] for s in data["studies"]]
    assert sample2["study1_id"] in study_ids

    # Verifica metadados do estudo na lixeira
    trash_study = next(s for s in data["studies"] if s["id"] == sample2["study1_id"])
    assert trash_study["book_title"] == "Livro de Teste"
    assert trash_study["chapter_name"] == "Capítulo 1"
    assert trash_study["days_until_purge"] <= 30


def test_restore_book_makes_it_active_again(client_and_db):
    """T014 [US2]: POST /api/books/{id}/restore reativa livro descartado no acervo."""
    client, _ = client_and_db
    sample = create_sample_book_with_studies(client)
    book_id = sample["book_id"]

    client.post(f"/api/books/{book_id}/trash")
    assert client.get(f"/api/books/{book_id}").status_code == 404

    # Restaura livro
    res_restore = client.post(f"/api/books/{book_id}/restore")
    assert res_restore.status_code == 200
    assert res_restore.json()["deleted_at"] is None

    # Livro reaparece no acervo ativo
    assert client.get(f"/api/books/{book_id}").status_code == 200

    # Tentar restaurar novamente retorna 400
    assert client.post(f"/api/books/{book_id}/restore").status_code == 400


def test_restore_study_with_cascading_book_restoration(client_and_db):
    """T014 [US2]: POST /api/studies/{id}/restore com livro pai na lixeira reativa livro e estudo (cascata ascendente)."""
    client, _ = client_and_db
    sample = create_sample_book_with_studies(client)
    book_id = sample["book_id"]
    study1_id = sample["study1_id"]

    # Descarta livro pai
    client.post(f"/api/books/{book_id}/trash")
    assert client.get(f"/api/books/{book_id}").status_code == 404
    assert client.get(f"/api/studies/{study1_id}").status_code == 404

    # Restaura o estudo diretamente
    res_restore = client.post(f"/api/studies/{study1_id}/restore")
    assert res_restore.status_code == 200
    assert res_restore.json()["deleted_at"] is None

    # Livro pai e estudo devem estar reativados no acervo ativo
    res_book = client.get(f"/api/books/{book_id}")
    assert res_book.status_code == 200
    assert res_book.json()["deleted_at"] is None

    res_study = client.get(f"/api/studies/{study1_id}")
    assert res_study.status_code == 200
    assert res_study.json()["deleted_at"] is None


def test_permanent_delete_book_cascades_safely(client_and_db):
    """T021 [US3]: DELETE /api/books/{id}/permanent expurga livro, capítulos e estudos sem violar FKs."""
    client, _ = client_and_db
    sample = create_sample_book_with_studies(client)
    book_id = sample["book_id"]
    study1_id = sample["study1_id"]

    # Descarta livro
    client.post(f"/api/books/{book_id}/trash")

    # Exclusão permanente
    res_del = client.delete(f"/api/books/{book_id}/permanent")
    assert res_del.status_code == 204

    # Confirma que não existe mais em nenhuma consulta nem na lixeira
    assert client.get(f"/api/books/{book_id}").status_code == 404
    assert client.get(f"/api/studies/{study1_id}").status_code == 404

    trash_res = client.get("/api/trash")
    book_ids = [b["id"] for b in trash_res.json()["books"]]
    assert book_id not in book_ids


def test_permanent_delete_individual_study(client_and_db):
    """T021 [US3]: DELETE /api/studies/{id}/permanent expurga estudo sem afetar o capítulo ou livro."""
    client, _ = client_and_db
    sample = create_sample_book_with_studies(client)
    book_id = sample["book_id"]
    study1_id = sample["study1_id"]
    study2_id = sample["study2_id"]

    # Descarta apenas o estudo 1
    client.post(f"/api/studies/{study1_id}/trash")

    # Exclui permanentemente
    res_del = client.delete(f"/api/studies/{study1_id}/permanent")
    assert res_del.status_code == 204

    # Estudo 1 sumiu, livro e estudo 2 continuam intactos
    assert client.get(f"/api/studies/{study1_id}").status_code == 404
    assert client.get(f"/api/books/{book_id}").status_code == 200

    trash_res = client.get("/api/trash")
    study_ids = [s["id"] for s in trash_res.json()["studies"]]
    assert study1_id not in study_ids


def test_empty_trash_purges_all_discarded_items(client_and_db):
    """T021 [US3]: POST /api/trash/empty expurga todos os itens da lixeira e mantém acervo ativo."""
    client, _ = client_and_db
    sample1 = create_sample_book_with_studies(client)
    sample2 = create_sample_book_with_studies(client)

    # Descarta livro 1 e estudo 1 do livro 2
    client.post(f"/api/books/{sample1['book_id']}/trash")
    client.post(f"/api/studies/{sample2['study1_id']}/trash")

    # Esvazia a lixeira
    res_empty = client.post("/api/trash/empty")
    assert res_empty.status_code == 200
    data = res_empty.json()
    assert data["purged_books"] >= 1
    assert data["purged_studies"] >= 1

    # Lixeira agora está 100% vazia
    trash_res = client.get("/api/trash")
    assert trash_res.json()["total_items"] == 0

    # Livro 2 continua ativo
    res_book2 = client.get(f"/api/books/{sample2['book_id']}")
    assert res_book2.status_code == 200


def test_purge_expired_trash_respects_30_days_threshold(client_and_db):
    """T021 [US3]: POST /api/trash/purge-expired expurga apenas itens com mais de 30 dias de descarte."""
    client, _ = client_and_db
    sample1 = create_sample_book_with_studies(client)
    sample2 = create_sample_book_with_studies(client)
    book1_id = sample1["book_id"]
    book2_id = sample2["book_id"]

    # Descarta ambos os livros
    client.post(f"/api/books/{book1_id}/trash")
    client.post(f"/api/books/{book2_id}/trash")

    # Manupula a data de livro 1 diretamente na base efêmera para simular 35 dias atrás
    # Acessa a sessão do app de teste
    from sqlalchemy import update
    from app.models import Book
    from app.db.session import create_sqlite_engine, Session

    old_date = datetime.now(UTC) - timedelta(days=35)
    with Session(create_sqlite_engine(client_and_db[1])) as s:
        s.execute(update(Book).where(Book.id == book1_id).values(deleted_at=old_date))
        s.commit()

    # Aciona purga de expirados
    res_purge = client.post("/api/trash/purge-expired")
    assert res_purge.status_code == 200
    data = res_purge.json()
    assert data["purged_books"] == 1

    # Livro 1 (antigo) foi purgado; Livro 2 (recente) ainda está na lixeira
    trash_res = client.get("/api/trash")
    trash_books = [b["id"] for b in trash_res.json()["books"]]
    assert book1_id not in trash_books
    assert book2_id in trash_books


