"""Testes de integração para os campos agregados de StudySummary na Grid View (F 0.7.4)."""
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app


def make_client(engine, user_id: str = DEFAULT_OWNER_ID):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application, headers={"X-User-Id": user_id})


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-study-grid-summary.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def test_study_grid_summary_metrics(api):
    client, engine, _ = api

    # 1. Cria livro e capítulo
    res_b = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    # 2. Cria estudo 1 com summary longo (> 240 caracteres)
    long_summary = "Este é um resumo analítico detalhado sobre o tema. " * 10
    res_s1 = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo Alfa",
            "summary": long_summary,
            "explanation": "Explicação secundária",
        },
    )
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    # 3. Cria estudo 2 sem summary, mas com explanation (fallback)
    res_s2 = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo Beta",
            "summary": "   ",  # em branco
            "explanation": "Explicação principal que servirá de fallback elegante.",
        },
    )
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    # 4. Cria estudo 3 sem summary e sem explanation (somente concepts)
    res_s3 = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo Gama",
            "concepts": "Conceito 1; Conceito 2",
        },
    )
    assert res_s3.status_code == 201
    s3_id = res_s3.json()["id"]

    # 5. Adiciona destaques ao Estudo Alfa
    h1 = client.post(
        f"/api/studies/{s1_id}/highlights",
        json={
            "section": "summary",
            "selected_text": "resumo analítico",
            "start_offset": 10,
            "end_offset": 26,
            "color": "yellow",
            "kind": "highlight",
        },
    )
    assert h1.status_code == 201

    h2 = client.post(
        f"/api/studies/{s1_id}/highlights",
        json={
            "section": "summary",
            "selected_text": "detalhado",
            "start_offset": 27,
            "end_offset": 36,
            "color": "blue",
            "kind": "note",
            "note": "Nota importante",
        },
    )
    assert h2.status_code == 201

    # 6. Cria relação semântica: Alfa -> Beta
    r1 = client.post(
        f"/api/studies/{s1_id}/relations",
        json={
            "target_study_id": s2_id,
            "relation_type": "relacionado_com",
            "description": "Conexão semântica",
        },
    )
    assert r1.status_code == 201

    # 7. Chama list_studies para o capítulo
    res_list = client.get(f"/api/chapters/{chapter_id}/studies")
    assert res_list.status_code == 200
    studies = res_list.json()
    assert len(studies) == 3

    studies_by_id = {s["id"]: s for s in studies}

    # Validação do Estudo Alfa (s1)
    alfa = studies_by_id[s1_id]
    assert len(alfa["summary_preview"]) <= 240
    assert alfa["summary_preview"].startswith("Este é um resumo analítico detalhado")
    assert alfa["highlights_count"] == 2
    assert alfa["relations_count"] == 1  # origem de 1 relação

    # Validação do Estudo Beta (s2)
    beta = studies_by_id[s2_id]
    assert beta["summary_preview"] == "Explicação principal que servirá de fallback elegante."
    assert beta["highlights_count"] == 0
    assert beta["relations_count"] == 1  # destino de 1 relação (s1 -> s2)

    # Validação do Estudo Gama (s3)
    gama = studies_by_id[s3_id]
    assert gama["summary_preview"] == ""
    assert gama["highlights_count"] == 0
    assert gama["relations_count"] == 0
