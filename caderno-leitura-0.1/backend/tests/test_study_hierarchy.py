"""Testes para hierarquia de estudos, ordenação, integridade DAG e cascata na lixeira."""
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import Study


def make_client(engine):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application)


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-hierarchy.db"
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
    res_b = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    return book_id, chapter_id


def create_study(client, chapter_id, title, parent_study_id=None, position=0):
    payload = {
        "chapter_id": chapter_id,
        "title": title,
        "summary": f"Resumo de {title}",
    }
    res = client.post("/api/studies", json=payload)
    assert res.status_code == 201, res.text
    study = res.json()
    if parent_study_id is not None or position != 0:
        move_res = client.post(
            f"/api/studies/{study['id']}/move",
            json={"parent_study_id": parent_study_id, "target_position": position},
        )
        assert move_res.status_code == 200, move_res.text
        # Busca o estudo atualizado
        study = client.get(f"/api/studies/{study['id']}").json()
    return study


def test_list_studies_includes_hierarchy_fields(api):
    client, _, _ = api
    _, chapter_id = setup_book_and_chapter(client)

    s1 = create_study(client, chapter_id, "Estudo Raiz 1")
    s2 = create_study(client, chapter_id, "Estudo Raiz 2")

    res = client.get(f"/api/chapters/{chapter_id}/studies")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 2
    assert "parent_study_id" in items[0]
    assert "position" in items[0]
    assert items[0]["parent_study_id"] is None


def test_move_study_nesting_and_reordering(api):
    client, _, _ = api
    _, chapter_id = setup_book_and_chapter(client)

    s1 = create_study(client, chapter_id, "Estudo A")
    s2 = create_study(client, chapter_id, "Estudo B")
    s3 = create_study(client, chapter_id, "Estudo C")

    # Aninha Estudo B dentro de Estudo A
    res_move = client.post(
        f"/api/studies/{s2['id']}/move",
        json={"parent_study_id": s1["id"], "target_position": 0},
    )
    assert res_move.status_code == 200

    s2_updated = client.get(f"/api/studies/{s2['id']}").json()
    assert s2_updated["parent_study_id"] == s1["id"]
    assert s2_updated["position"] == 0

    # Aninha Estudo C dentro de Estudo A na posição 1
    res_move2 = client.post(
        f"/api/studies/{s3['id']}/move",
        json={"parent_study_id": s1["id"], "target_position": 1},
    )
    assert res_move2.status_code == 200
    s3_updated = client.get(f"/api/studies/{s3['id']}").json()
    assert s3_updated["parent_study_id"] == s1["id"]
    assert s3_updated["position"] == 1

    # Reordena Estudo C para posição 0 (antes de B)
    res_reorder = client.post(
        f"/api/studies/{s3['id']}/move",
        json={"parent_study_id": s1["id"], "target_position": 0},
    )
    assert res_reorder.status_code == 200
    s3_re = client.get(f"/api/studies/{s3['id']}").json()
    s2_re = client.get(f"/api/studies/{s2['id']}").json()
    assert s3_re["position"] == 0
    assert s2_re["position"] == 1


def test_promote_study_to_root(api):
    client, _, _ = api
    _, chapter_id = setup_book_and_chapter(client)

    s1 = create_study(client, chapter_id, "Pai")
    s2 = create_study(client, chapter_id, "Filho", parent_study_id=s1["id"])

    assert s2["parent_study_id"] == s1["id"]

    # Promove para raiz
    res = client.post(
        f"/api/studies/{s2['id']}/move",
        json={"parent_study_id": None, "target_position": 1},
    )
    assert res.status_code == 200
    s2_promoted = client.get(f"/api/studies/{s2['id']}").json()
    assert s2_promoted["parent_study_id"] is None


def test_dag_cycle_prevention(api):
    client, _, _ = api
    _, chapter_id = setup_book_and_chapter(client)

    s1 = create_study(client, chapter_id, "Pai")
    s2 = create_study(client, chapter_id, "Filho", parent_study_id=s1["id"])
    s3 = create_study(client, chapter_id, "Neto", parent_study_id=s2["id"])

    # Tentativa 1: Auto-referência (Pai -> Pai)
    res_self = client.post(
        f"/api/studies/{s1['id']}/move",
        json={"parent_study_id": s1["id"], "target_position": 0},
    )
    assert res_self.status_code == 422
    assert "Auto-referência" in res_self.json()["detail"]

    # Tentativa 2: Ciclo direto (Pai dentro de seu Filho)
    res_child = client.post(
        f"/api/studies/{s1['id']}/move",
        json={"parent_study_id": s2["id"], "target_position": 0},
    )
    assert res_child.status_code == 422
    assert "Ciclo hierárquico" in res_child.json()["detail"]

    # Tentativa 3: Ciclo indireto (Pai dentro de seu Neto)
    res_grandchild = client.post(
        f"/api/studies/{s1['id']}/move",
        json={"parent_study_id": s3["id"], "target_position": 0},
    )
    assert res_grandchild.status_code == 422
    assert "Ciclo hierárquico" in res_grandchild.json()["detail"]


def test_max_hierarchy_depth_limit(api):
    client, _, _ = api
    _, chapter_id = setup_book_and_chapter(client)

    # Cria cadeia de 5 níveis: Nível 0 -> Nível 1 -> Nível 2 -> Nível 3 -> Nível 4
    n0 = create_study(client, chapter_id, "N0")
    n1 = create_study(client, chapter_id, "N1", parent_study_id=n0["id"])
    n2 = create_study(client, chapter_id, "N2", parent_study_id=n1["id"])
    n3 = create_study(client, chapter_id, "N3", parent_study_id=n2["id"])
    n4 = create_study(client, chapter_id, "N4", parent_study_id=n3["id"])

    # Cria outro nó N5 solto
    n5 = create_study(client, chapter_id, "N5")

    # Tentativa de mover N5 para dentro de N4 (criaria nível 5, total 6 níveis) -> DEVE REJEITAR 422
    res = client.post(
        f"/api/studies/{n5['id']}/move",
        json={"parent_study_id": n4["id"], "target_position": 0},
    )
    assert res.status_code == 422
    assert "Limite de profundidade" in res.json()["detail"]


def test_optimistic_concurrency_conflict(api):
    client, _, _ = api
    _, chapter_id = setup_book_and_chapter(client)

    s1 = create_study(client, chapter_id, "Pai")
    s2 = create_study(client, chapter_id, "Filho")

    # Move com timestamp defasado
    res = client.post(
        f"/api/studies/{s2['id']}/move",
        json={
            "parent_study_id": s1["id"],
            "target_position": 0,
            "expected_updated_at": "2020-01-01T00:00:00Z",
        },
    )
    assert res.status_code == 409
    assert "Conflito de concorrência" in res.json()["detail"]


def test_trash_cascade_and_restore(api):
    client, _, _ = api
    _, chapter_id = setup_book_and_chapter(client)

    pai = create_study(client, chapter_id, "Estudo Pai")
    filho = create_study(client, chapter_id, "Estudo Filho", parent_study_id=pai["id"])
    neto = create_study(client, chapter_id, "Estudo Neto", parent_study_id=filho["id"])

    # 1. Envia pai para lixeira
    res_trash = client.post(f"/api/studies/{pai['id']}/trash")
    assert res_trash.status_code == 200

    # Verifica se pai, filho e neto não constam na listagem ativa do capítulo
    list_active = client.get(f"/api/chapters/{chapter_id}/studies").json()
    active_ids = [s["id"] for s in list_active]
    assert pai["id"] not in active_ids
    assert filho["id"] not in active_ids
    assert neto["id"] not in active_ids

    # 2. Restaura pai da lixeira
    res_restore = client.post(f"/api/studies/{pai['id']}/restore")
    assert res_restore.status_code == 200

    # Verifica se pai, filho e neto retornaram juntos
    list_restored = client.get(f"/api/chapters/{chapter_id}/studies").json()
    restored_ids = [s["id"] for s in list_restored]
    assert pai["id"] in restored_ids
    assert filho["id"] in restored_ids
    assert neto["id"] in restored_ids
