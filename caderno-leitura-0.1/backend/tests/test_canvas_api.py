"""Testes para persistência espacial de estudos no Canvas, batch update, isolamento e integridade."""
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import Study, StudyCanvasNode


def make_client(engine):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application)


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-canvas.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def setup_book_and_chapter(client):
    res_b = client.post("/api/books", json={"title": "Livro de Teste Espacial", "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo Espacial"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    return book_id, chapter_id


def create_study(client, chapter_id, title):
    payload = {
        "chapter_id": chapter_id,
        "title": title,
        "summary": f"Resumo conceitual de {title}",
    }
    res = client.post("/api/studies", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


def test_get_canvas_empty(api):
    client, engine, _ = api
    book_id, _ = setup_book_and_chapter(client)

    res = client.get(f"/api/books/{book_id}/canvas")
    assert res.status_code == 200
    data = res.json()
    assert data["book_id"] == book_id
    assert data["nodes"] == []


def test_batch_upsert_canvas_nodes(api):
    client, engine, _ = api
    book_id, chapter_id = setup_book_and_chapter(client)

    s1 = create_study(client, chapter_id, "Tese Alfa")
    s2 = create_study(client, chapter_id, "Antítese Beta")

    payload = {
        "nodes": [
            {"study_id": s1["id"], "pos_x": 100.5, "pos_y": 200.0, "z_index": 1, "color_tag": "blue"},
            {"study_id": s2["id"], "pos_x": 420.0, "pos_y": 200.0, "z_index": 2, "color_tag": "amber"},
        ]
    }

    res = client.put(f"/api/books/{book_id}/canvas", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert len(data["nodes"]) == 2

    node1 = next(n for n in data["nodes"] if n["study_id"] == s1["id"])
    assert node1["pos_x"] == 100.5
    assert node1["pos_y"] == 200.0
    assert node1["color_tag"] == "blue"

    # Atualizar novamente (upsert)
    payload_update = {
        "nodes": [
            {"study_id": s1["id"], "pos_x": 150.0, "pos_y": 250.0, "z_index": 5, "color_tag": "emerald"},
        ]
    }
    res_up = client.put(f"/api/books/{book_id}/canvas", json=payload_update)
    assert res_up.status_code == 200
    data_up = res_up.json()
    node1_up = next(n for n in data_up["nodes"] if n["study_id"] == s1["id"])
    assert node1_up["pos_x"] == 150.0
    assert node1_up["color_tag"] == "emerald"
    assert node1_up["z_index"] == 5


def test_batch_upsert_preserves_study_hierarchy_and_chapters(api):
    client, engine, _ = api
    book_id, chapter_id = setup_book_and_chapter(client)

    parent_study = create_study(client, chapter_id, "Estudo Pai")
    child_study = create_study(client, chapter_id, "Estudo Filho")

    # Definir parent_study_id
    res_move = client.post(
        f"/api/studies/{child_study['id']}/move",
        json={"parent_study_id": parent_study["id"], "target_position": 0},
    )
    assert res_move.status_code == 200, res_move.text

    # Mover os dois no canvas
    payload = {
        "nodes": [
            {"study_id": parent_study["id"], "pos_x": 50.0, "pos_y": 50.0},
            {"study_id": child_study["id"], "pos_x": 350.0, "pos_y": 50.0},
        ]
    }
    res = client.put(f"/api/books/{book_id}/canvas", json=payload)
    assert res.status_code == 200

    # Verificar que na tabela studies nada mudou
    with Session(engine) as session:
        c_study = session.get(Study, child_study["id"])
        assert c_study.parent_study_id == parent_study["id"]
        assert c_study.chapter_id == chapter_id


def test_batch_upsert_rejects_foreign_study(api):
    client, engine, _ = api
    book_id_1, chapter_id_1 = setup_book_and_chapter(client)
    book_id_2, chapter_id_2 = setup_book_and_chapter(client)

    s_foreign = create_study(client, chapter_id_2, "Estudo de Outro Livro")

    payload = {
        "nodes": [
            {"study_id": s_foreign["id"], "pos_x": 100.0, "pos_y": 100.0}
        ]
    }
    # Tentar enviar para book_id_1
    res = client.put(f"/api/books/{book_id_1}/canvas", json=payload)
    assert res.status_code == 400
    assert "não pertence ao livro" in res.json()["detail"]


def test_batch_upsert_rejects_non_finite_coords(api):
    client, engine, _ = api
    book_id, chapter_id = setup_book_and_chapter(client)
    s1 = create_study(client, chapter_id, "Estudo Numérico")

    # Enviar string ou valor não serializável
    res = client.put(f"/api/books/{book_id}/canvas", json={
        "nodes": [{"study_id": s1["id"], "pos_x": "inf", "pos_y": 100.0}]
    })
    assert res.status_code == 422


def test_patch_single_canvas_node(api):
    client, engine, _ = api
    book_id, chapter_id = setup_book_and_chapter(client)
    s1 = create_study(client, chapter_id, "Estudo Individual")

    res = client.patch(f"/api/studies/{s1['id']}/canvas", json={"pos_x": 77.0, "pos_y": 88.0, "color_tag": "violet"})
    assert res.status_code == 200
    node = res.json()
    assert node["pos_x"] == 77.0
    assert node["pos_y"] == 88.0
    assert node["color_tag"] == "violet"


def test_canvas_omits_trashed_studies(api):
    client, engine, _ = api
    book_id, chapter_id = setup_book_and_chapter(client)
    s1 = create_study(client, chapter_id, "Estudo para Lixeira")

    client.put(f"/api/books/{book_id}/canvas", json={"nodes": [{"study_id": s1["id"], "pos_x": 10.0, "pos_y": 10.0}]})

    # Enviar estudo para a lixeira
    res_trash = client.post(f"/api/studies/{s1['id']}/trash")
    assert res_trash.status_code == 200

    # GET canvas não deve listar o estudo na lixeira
    res = client.get(f"/api/books/{book_id}/canvas")
    assert res.status_code == 200
    assert len(res.json()["nodes"]) == 0
