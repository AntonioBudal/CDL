"""Testes de preservação latente de relações sob lixeira (soft delete) e expurgo definitivo (cascade)."""
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import StudyRelation


def make_client(engine):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application)


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-relations-trash.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def setup_test_studies(client):
    res_b = client.post("/api/books", json={"title": "Livro de Epistemologia", "author": "Autor de Teste"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    res_s1 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Estudo Alfa", "summary": "Primeiro estudo"})
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    res_s2 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Estudo Beta", "summary": "Segundo estudo"})
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    res_s3 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Estudo Gama", "summary": "Terceiro estudo"})
    assert res_s3.status_code == 201
    s3_id = res_s3.json()["id"]

    return book_id, chapter_id, s1_id, s2_id, s3_id


def test_latent_relations_under_soft_delete_and_restore(api):
    client, engine, _ = api
    book_id, chapter_id, s1_id, s2_id, s3_id = setup_test_studies(client)

    # 1. Criar relação s1 -> s2 (Alfa complementa Beta)
    res_rel1 = client.post(
        f"/api/studies/{s1_id}/relations",
        json={
            "target_study_id": s2_id,
            "relation_type": "complementa",
            "description": "Alfa fundamenta os axiomas de Beta.",
        },
    )
    assert res_rel1.status_code == 201
    rel1_id = res_rel1.json()["id"]

    # Criar relação s3 -> s1 (Gama depende de Alfa)
    res_rel2 = client.post(
        f"/api/studies/{s3_id}/relations",
        json={
            "target_study_id": s1_id,
            "relation_type": "depende_de",
            "description": "Gama requer as conclusões de Alfa.",
        },
    )
    assert res_rel2.status_code == 201
    rel2_id = res_rel2.json()["id"]

    # 2. Verificar estado ativo inicial
    res_s1_init = client.get(f"/api/studies/{s1_id}/relations")
    assert res_s1_init.status_code == 200
    data_s1 = res_s1_init.json()
    assert len(data_s1["outbound"]) == 1
    assert data_s1["outbound"][0]["id"] == rel1_id
    assert len(data_s1["inbound"]) == 1
    assert data_s1["inbound"][0]["id"] == rel2_id

    # Canvas inicial do livro deve ter 2 arestas
    res_canvas_init = client.get(f"/api/books/{book_id}/relations")
    assert len(res_canvas_init.json()) == 2

    # 3. Mover Estudo Beta (s2) para a lixeira (Soft Delete)
    res_trash_s2 = client.post(f"/api/studies/{s2_id}/trash")
    assert res_trash_s2.status_code == 200
    assert res_trash_s2.json()["deleted_at"] is not None

    # 4. Verificar que a relação Alfa -> Beta fica LATENTE (oculta nas telas ativas)
    res_s1_after_trash = client.get(f"/api/studies/{s1_id}/relations")
    assert res_s1_after_trash.status_code == 200
    data_s1_after = res_s1_after_trash.json()
    assert len(data_s1_after["outbound"]) == 0, "Relação com estudo na lixeira deve ser ocultada"
    assert len(data_s1_after["inbound"]) == 1, "Inbound de Gama (ativo) deve continuar visível"

    # No Canvas, a aresta para Beta também deve sumir
    res_canvas_after = client.get(f"/api/books/{book_id}/relations")
    assert len(res_canvas_after.json()) == 1
    assert res_canvas_after.json()[0]["id"] == rel2_id

    # Na busca por candidatos, Beta não deve aparecer
    res_search = client.get(f"/api/studies/search-candidates?exclude_study_id={s1_id}&query=Beta")
    assert res_search.status_code == 200
    assert len(res_search.json()) == 0

    # No banco de dados físico, o registro em study_relations continua INTACTO
    with Session(engine) as session:
        rel_db = session.get(StudyRelation, rel1_id)
        assert rel_db is not None
        assert rel_db.source_study_id == s1_id
        assert rel_db.target_study_id == s2_id
        assert rel_db.relation_type == "complementa"
        assert rel_db.description == "Alfa fundamenta os axiomas de Beta."

    # 5. Restaurar Estudo Beta da lixeira
    res_restore = client.post(f"/api/studies/{s2_id}/restore")
    assert res_restore.status_code == 200

    # 6. Constatar reaparecimento intacto da relação
    res_s1_restored = client.get(f"/api/studies/{s1_id}/relations")
    assert res_s1_restored.status_code == 200
    data_s1_restored = res_s1_restored.json()
    assert len(data_s1_restored["outbound"]) == 1
    assert data_s1_restored["outbound"][0]["id"] == rel1_id
    assert data_s1_restored["outbound"][0]["connected_study"]["id"] == s2_id
    assert data_s1_restored["outbound"][0]["description"] == "Alfa fundamenta os axiomas de Beta."

    # Canvas restaurado tem as 2 conexões novamente
    res_canvas_restored = client.get(f"/api/books/{book_id}/relations")
    assert len(res_canvas_restored.json()) == 2


def test_permanent_deletion_cascades_relations(api):
    client, engine, _ = api
    book_id, chapter_id, s1_id, s2_id, s3_id = setup_test_studies(client)

    # Criar relação s3 -> s1
    res_rel = client.post(
        f"/api/studies/{s3_id}/relations",
        json={"target_study_id": s1_id, "relation_type": "depende_de"},
    )
    assert res_rel.status_code == 201
    rel_id = res_rel.json()["id"]

    # Confirmar existência
    with Session(engine) as session:
        assert session.get(StudyRelation, rel_id) is not None

    # Excluir permanentemente o estudo s3 (expurgo definitivo)
    res_perm = client.delete(f"/api/studies/{s3_id}/permanent")
    assert res_perm.status_code == 204

    # Confirmar que a relação foi removida em cascata
    with Session(engine) as session:
        rel_in_db = session.get(StudyRelation, rel_id)
        assert rel_in_db is None, "Relação deve ser purgada em cascata na exclusão permanente do estudo"

    # Consultar relações de s1: inbound agora é vazio
    res_s1 = client.get(f"/api/studies/{s1_id}/relations")
    assert res_s1.status_code == 200
    assert len(res_s1.json()["inbound"]) == 0
