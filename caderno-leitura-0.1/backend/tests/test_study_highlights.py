"""Testes de integração para API de destaques e anotações contextuais de estudos."""
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.study_highlight import StudyHighlight


def make_client(engine, user_id: str = DEFAULT_OWNER_ID):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application, headers={"X-User-Id": user_id})


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-highlights.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def setup_study(client):
    res_b = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo de Teste",
            "summary": "O texto de resumo do estudo de teste.",
            "explanation": "Explicação detalhada sobre a teoria.",
            "concepts": "Conceito A; Conceito B",
            "references": "Fonte Primária",
        },
    )
    assert res_s.status_code == 201
    return res_s.json()["id"]


def test_create_and_list_highlights(api):
    client, engine, _ = api
    study_id = setup_study(client)

    payload = {
        "section": "summary",
        "start_offset": 2,
        "end_offset": 17,
        "selected_text": "texto de resumo",
        "prefix": "O ",
        "suffix": " do estudo",
        "color": "green",
        "kind": "highlight",
        "note": "",
    }
    res_create = client.post(f"/api/studies/{study_id}/highlights", json=payload)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["id"] > 0
    assert created["study_id"] == study_id
    assert created["section"] == "summary"
    assert created["selected_text"] == "texto de resumo"
    assert created["color"] == "green"
    assert created["kind"] == "highlight"

    # Listar destaques
    res_list = client.get(f"/api/studies/{study_id}/highlights")
    assert res_list.status_code == 200
    items = res_list.json()
    assert len(items) == 1
    assert items[0]["id"] == created["id"]

    # Filtro por seção
    res_summary = client.get(f"/api/studies/{study_id}/highlights?section=summary")
    assert res_summary.status_code == 200
    assert len(res_summary.json()) == 1

    res_other = client.get(f"/api/studies/{study_id}/highlights?section=explanation")
    assert res_other.status_code == 200
    assert len(res_other.json()) == 0


def test_update_highlight(api):
    client, _, _ = api
    study_id = setup_study(client)

    res_create = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "explanation",
            "start_offset": 0,
            "end_offset": 10,
            "selected_text": "Explicação",
            "color": "yellow",
            "kind": "highlight",
        },
    )
    assert res_create.status_code == 201
    highlight_id = res_create.json()["id"]

    # Atualizar cor e nota
    res_patch = client.patch(
        f"/api/studies/{study_id}/highlights/{highlight_id}",
        json={
            "color": "blue",
            "kind": "note",
            "note": "Reflexão importante para a tese.",
        },
    )
    assert res_patch.status_code == 200
    updated = res_patch.json()
    assert updated["color"] == "blue"
    assert updated["kind"] == "note"
    assert updated["note"] == "Reflexão importante para a tese."


def test_delete_highlight(api):
    client, _, _ = api
    study_id = setup_study(client)

    res_create = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "concepts",
            "start_offset": 0,
            "end_offset": 10,
            "selected_text": "Conceito A",
            "color": "pink",
            "kind": "highlight",
        },
    )
    assert res_create.status_code == 201
    highlight_id = res_create.json()["id"]

    res_del = client.delete(f"/api/studies/{study_id}/highlights/{highlight_id}")
    assert res_del.status_code == 204

    # Confirmar exclusão
    res_list = client.get(f"/api/studies/{study_id}/highlights")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 0


def test_validation_errors(api):
    client, _, _ = api
    study_id = setup_study(client)

    # Offset inválido (end < start)
    res_offset = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 20,
            "end_offset": 10,
            "selected_text": "teste",
        },
    )
    assert res_offset.status_code == 422

    # Texto selecionado vazio
    res_empty = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 5,
            "selected_text": "   ",
        },
    )
    assert res_empty.status_code == 422

    # Cor inválida
    res_color = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 5,
            "selected_text": "teste",
            "color": "neon_rainbow",
        },
    )
    assert res_color.status_code == 422


def test_cascade_delete_with_study(api):
    client, engine, _ = api
    study_id = setup_study(client)

    res_create = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 5,
            "selected_text": "texto",
            "color": "purple",
        },
    )
    assert res_create.status_code == 201
    highlight_id = res_create.json()["id"]

    # Excluir estudo permanentemente
    client.post(f"/api/studies/{study_id}/trash")
    res_perm = client.delete(f"/api/studies/{study_id}/permanent")
    assert res_perm.status_code == 204, f"Falha no permanent delete: {res_perm.status_code} {res_perm.text}"

    with Session(engine) as session:
        hl = session.get(StudyHighlight, highlight_id)
        assert hl is None
