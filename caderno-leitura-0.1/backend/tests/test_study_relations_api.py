"""Testes de integração da API de relações entre estudos, resolução de backlinks e integridade."""
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
    path = tmp_path / "test-relations.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def setup_book_and_studies(client):
    res_b = client.post("/api/books", json={"title": "Livro de Epistemologia", "author": "Filósofo Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1: Fundamentos"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    res_s1 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Tese Principal A", "summary": "Premissa fundamental"})
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    res_s2 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Contra-argumento B", "summary": "Objeção crítica"})
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    res_s3 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Síntese C", "summary": "Resolução dialética"})
    assert res_s3.status_code == 201
    s3_id = res_s3.json()["id"]

    return book_id, chapter_id, s1_id, s2_id, s3_id


def test_create_and_get_study_relations_bidirectional(api):
    client, engine, _ = api
    book_id, chapter_id, s1_id, s2_id, s3_id = setup_book_and_studies(client)

    # 1. Estudo 1 contradiz Estudo 2
    res_create = client.post(
        f"/api/studies/{s1_id}/relations",
        json={
            "target_study_id": s2_id,
            "relation_type": "contradiz",
            "description": "A premissa em A contesta o ponto de B.",
        },
    )
    assert res_create.status_code == 201, res_create.text
    created = res_create.json()
    assert created["source_study_id"] == s1_id
    assert created["target_study_id"] == s2_id
    assert created["relation_type"] == "contradiz"
    assert created["description"] == "A premissa em A contesta o ponto de B."
    assert created["connected_study"]["id"] == s2_id
    assert created["connected_study"]["title"] == "Contra-argumento B"

    # 2. Consultar relações do Estudo 1: deve ter 1 outbound e 0 inbound
    res_s1_rel = client.get(f"/api/studies/{s1_id}/relations")
    assert res_s1_rel.status_code == 200
    s1_data = res_s1_rel.json()
    assert len(s1_data["outbound"]) == 1
    assert len(s1_data["inbound"]) == 0
    assert s1_data["outbound"][0]["relation_type"] == "contradiz"
    assert s1_data["outbound"][0]["connected_study"]["id"] == s2_id

    # 3. Consultar relações do Estudo 2: deve ter 0 outbound e 1 inbound (backlink)
    res_s2_rel = client.get(f"/api/studies/{s2_id}/relations")
    assert res_s2_rel.status_code == 200
    s2_data = res_s2_rel.json()
    assert len(s2_data["outbound"]) == 0
    assert len(s2_data["inbound"]) == 1
    assert s2_data["inbound"][0]["relation_type"] == "contradiz"
    assert s2_data["inbound"][0]["connected_study"]["id"] == s1_id
    assert s2_data["inbound"][0]["connected_study"]["title"] == "Tese Principal A"


def test_reject_self_relation(api):
    client, _, _ = api
    _, _, s1_id, _, _ = setup_book_and_studies(client)

    res = client.post(
        f"/api/studies/{s1_id}/relations",
        json={"target_study_id": s1_id, "relation_type": "mesmo_tema"},
    )
    assert res.status_code == 400
    assert "não pode ser relacionado a si mesmo" in res.json()["detail"]


def test_reject_duplicate_relation(api):
    client, _, _ = api
    _, _, s1_id, s2_id, _ = setup_book_and_studies(client)

    res1 = client.post(
        f"/api/studies/{s1_id}/relations",
        json={"target_study_id": s2_id, "relation_type": "complementa"},
    )
    assert res1.status_code == 201

    # Segunda tentativa idêntica
    res2 = client.post(
        f"/api/studies/{s1_id}/relations",
        json={"target_study_id": s2_id, "relation_type": "complementa"},
    )
    assert res2.status_code == 400
    assert "já existe" in res2.json()["detail"]


def test_reject_invalid_relation_type(api):
    client, _, _ = api
    _, _, s1_id, s2_id, _ = setup_book_and_studies(client)

    res = client.post(
        f"/api/studies/{s1_id}/relations",
        json={"target_study_id": s2_id, "relation_type": "tipo_inexistente"},
    )
    assert res.status_code == 422


def test_update_and_delete_relation(api):
    client, _, _ = api
    _, _, s1_id, s2_id, _ = setup_book_and_studies(client)

    res_c = client.post(
        f"/api/studies/{s1_id}/relations",
        json={"target_study_id": s2_id, "relation_type": "relacionado_com", "description": "Nota inicial"},
    )
    assert res_c.status_code == 201
    relation_id = res_c.json()["id"]

    # Atualizar nota e tipo
    res_u = client.patch(
        f"/api/relations/{relation_id}",
        json={"relation_type": "desdobramento_de", "description": "Nota revisada"},
    )
    assert res_u.status_code == 200
    updated = res_u.json()
    assert updated["relation_type"] == "desdobramento_de"
    assert updated["description"] == "Nota revisada"

    # Excluir relação
    res_d = client.delete(f"/api/relations/{relation_id}")
    assert res_d.status_code == 200
    assert res_d.json()["success"] is True

    # Confirmar que a listagem agora está vazia
    res_check = client.get(f"/api/studies/{s1_id}/relations")
    assert len(res_check.json()["outbound"]) == 0


def test_search_candidate_studies(api):
    client, _, _ = api
    book_id, chapter_id, s1_id, s2_id, s3_id = setup_book_and_studies(client)

    # Buscar candidatos excluindo s1
    res = client.get(f"/api/studies/search-candidates?exclude_study_id={s1_id}&query=Contra")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["id"] == s2_id
    assert data[0]["title"] == "Contra-argumento B"

    # Buscar candidatos sem query (deve trazer s2 e s3, mas não s1)
    res_all = client.get(f"/api/studies/search-candidates?exclude_study_id={s1_id}")
    assert res_all.status_code == 200
    all_data = res_all.json()
    ids = [item["id"] for item in all_data]
    assert s1_id not in ids
    assert s2_id in ids
    assert s3_id in ids


def test_get_book_canvas_relations(api):
    client, _, _ = api
    book_id, chapter_id, s1_id, s2_id, s3_id = setup_book_and_studies(client)

    # Criar 2 relações dentro do mesmo livro
    client.post(f"/api/studies/{s1_id}/relations", json={"target_study_id": s2_id, "relation_type": "contradiz"})
    client.post(f"/api/studies/{s2_id}/relations", json={"target_study_id": s3_id, "relation_type": "desdobramento_de"})

    res = client.get(f"/api/books/{book_id}/relations")
    assert res.status_code == 200
    rels = res.json()
    assert len(rels) == 2
    types = {r["relation_type"] for r in rels}
    assert "contradiz" in types
    assert "desdobramento_de" in types
