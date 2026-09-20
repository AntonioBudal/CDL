from datetime import datetime, timedelta, timezone
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import CanvasFrame, Study


def make_client(engine):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application)


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-grouping.db"
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
    res_b = client.post("/api/books", json={"title": "Livro de Teste F05", "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1: Fundamentos"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    res_s1 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Estudo Alfa", "summary": "Resumo Alfa"})
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    res_s2 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Estudo Beta", "summary": "Resumo Beta"})
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    return book_id, chapter_id, s1_id, s2_id


def test_study_reading_status_default_and_list(api):
    client, _, _ = api
    book_id, chapter_id, s1_id, s2_id = setup_book_and_studies(client)

    # 1. Estudo criado tem status padrão 'rascunho'
    res_get = client.get(f"/api/studies/{s1_id}")
    assert res_get.status_code == 200
    assert res_get.json()["reading_status"] == "rascunho"

    # 2. Listar estudos do capítulo retorna reading_status
    res_list = client.get(f"/api/chapters/{chapter_id}/studies")
    assert res_list.status_code == 200
    studies = res_list.json()
    assert len(studies) == 2
    for s in studies:
        assert s["reading_status"] == "rascunho"


def test_study_update_status_transitions(api):
    client, _, _ = api
    _, _, s1_id, _ = setup_book_and_studies(client)

    # Ciclo editorial de 4 estados: rascunho -> em_estudo -> revisado -> concluido
    for new_status in ["em_estudo", "revisado", "concluido", "rascunho"]:
        res_patch = client.patch(f"/api/studies/{s1_id}/status", json={"reading_status": new_status})
        assert res_patch.status_code == 200
        data = res_patch.json()
        assert data["id"] == s1_id
        assert data["reading_status"] == new_status
        assert "updated_at" in data

        # Conferir no get completo
        res_get = client.get(f"/api/studies/{s1_id}")
        assert res_get.json()["reading_status"] == new_status


def test_study_update_status_invalid_value(api):
    client, _, _ = api
    _, _, s1_id, _ = setup_book_and_studies(client)

    res_patch = client.patch(f"/api/studies/{s1_id}/status", json={"reading_status": "invalido_xyz"})
    assert res_patch.status_code == 422


def test_study_update_status_concurrency_conflict(api):
    client, engine, _ = api
    _, _, s1_id, _ = setup_book_and_studies(client)

    # Pegar updated_at antigo
    res_get = client.get(f"/api/studies/{s1_id}")
    t0 = res_get.json()["updated_at"]

    # Simular alteracao remota avancando updated_at no banco
    with Session(engine) as s:
        study = s.get(Study, s1_id)
        study.updated_at = datetime.now(timezone.utc) + timedelta(seconds=5)
        s.commit()

    # Tentar atualizar com timestamp obsoleto t0 deve dar 409 Conflict
    res_patch = client.patch(
        f"/api/studies/{s1_id}/status",
        json={"reading_status": "revisado", "expected_updated_at": t0},
    )
    assert res_patch.status_code == 409
    assert "concorrência" in res_patch.json()["detail"].lower()


def test_study_update_status_in_trash_rejected(api):
    client, _, _ = api
    _, _, s1_id, _ = setup_book_and_studies(client)

    # Mover estudo para lixeira
    res_trash = client.post(f"/api/studies/{s1_id}/trash")
    assert res_trash.status_code == 200

    # Tentar alterar status deve falhar (400)
    res_patch = client.patch(f"/api/studies/{s1_id}/status", json={"reading_status": "concluido"})
    assert res_patch.status_code == 400


def test_canvas_frames_crud_and_validation(api):
    client, _, _ = api
    book_id, _, _, _ = setup_book_and_studies(client)

    # 1. Listagem inicial vazia
    res_list = client.get(f"/api/books/{book_id}/canvas/frames")
    assert res_list.status_code == 200
    assert res_list.json() == []

    # 2. Criar moldura com dimensões default
    create_payload = {
        "title": "Axiomas Centrais",
        "color": "amber",
        "pos_x": 100.0,
        "pos_y": 150.0,
        "width": 500.0,
        "height": 350.0,
    }
    res_create = client.post(f"/api/books/{book_id}/canvas/frames", json=create_payload)
    assert res_create.status_code == 201
    frame = res_create.json()
    assert frame["id"] > 0
    assert frame["book_id"] == book_id
    assert frame["title"] == "Axiomas Centrais"
    assert frame["color"] == "amber"
    assert frame["pos_x"] == 100.0
    assert frame["pos_y"] == 150.0
    assert frame["width"] == 500.0
    assert frame["height"] == 350.0
    frame_id = frame["id"]

    # 3. Listagem contém a nova moldura
    res_list2 = client.get(f"/api/books/{book_id}/canvas/frames")
    assert res_list2.status_code == 200
    assert len(res_list2.json()) == 1
    assert res_list2.json()[0]["id"] == frame_id

    # 4. Atualizar moldura (PATCH)
    patch_payload = {
        "title": "Axiomas e Postulados",
        "color": "indigo",
        "pos_x": 120.0,
        "width": 550.0,
    }
    res_patch = client.patch(f"/api/canvas/frames/{frame_id}", json=patch_payload)
    assert res_patch.status_code == 200
    updated = res_patch.json()
    assert updated["title"] == "Axiomas e Postulados"
    assert updated["color"] == "indigo"
    assert updated["pos_x"] == 120.0
    assert updated["width"] == 550.0
    assert updated["pos_y"] == 150.0  # mantido
    assert updated["height"] == 350.0  # mantido

    # 5. Validação de dimensões mínimas (width >= 100, height >= 80)
    res_bad_dim = client.patch(f"/api/canvas/frames/{frame_id}", json={"width": 50.0})
    assert res_bad_dim.status_code == 422

    res_bad_dim2 = client.post(
        f"/api/books/{book_id}/canvas/frames",
        json={"title": "Pequena", "width": 80.0, "height": 40.0},
    )
    assert res_bad_dim2.status_code == 422

    # 6. Exclusão de moldura (DELETE)
    res_del = client.delete(f"/api/canvas/frames/{frame_id}")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # Confirmar que não existe mais
    res_list3 = client.get(f"/api/books/{book_id}/canvas/frames")
    assert res_list3.status_code == 200
    assert len(res_list3.json()) == 0

    # 7. Tentar deletar inexistente dá 404
    res_del404 = client.delete(f"/api/canvas/frames/{frame_id}")
    assert res_del404.status_code == 404
