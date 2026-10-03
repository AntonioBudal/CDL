"""Testes de integração para as flags de completude de seções analíticas na List View (F 0.7.5)."""
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
    path = tmp_path / "test-study-list-summary.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def test_study_list_summary_section_flags(api):
    client, engine, _ = api

    # 1. Cria livro e capítulo
    res_b = client.post("/api/books", json={"title": "Livro de Epistemologia", "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    # 2. Estudo 1: apenas summary e explanation preenchidos
    res_s1 = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo 1 - Síntese Parcial",
            "summary": "Resumo sintético da tese.",
            "explanation": "Explicação detalhada dos fundamentos.",
            "concepts": "",
            "references": "   ",  # apenas espaços
        },
    )
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    # 3. Estudo 2: todas as 4 seções preenchidas
    res_s2 = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo 2 - Análise Completa",
            "summary": "Resumo presente.",
            "explanation": "Explicação presente.",
            "concepts": "Conceito A; Conceito B",
            "references": "Obra Citada, p. 45",
        },
    )
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    # 4. Estudo 3: apenas concepts preenchido
    res_s3 = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo 3 - Apenas Conceitos",
            "concepts": "Conceito X",
        },
    )
    assert res_s3.status_code == 201
    s3_id = res_s3.json()["id"]

    # 5. Consulta listagem de estudos do capítulo
    res_list = client.get(f"/api/chapters/{chapter_id}/studies")
    assert res_list.status_code == 200
    studies = res_list.json()
    assert len(studies) == 3

    studies_by_id = {s["id"]: s for s in studies}

    # Validação Estudo 1 (R=True, E=True, C=False, Ref=False)
    st1 = studies_by_id[s1_id]
    assert st1["has_summary"] is True
    assert st1["has_explanation"] is True
    assert st1["has_concepts"] is False
    assert st1["has_references"] is False

    # Validação Estudo 2 (todas True)
    st2 = studies_by_id[s2_id]
    assert st2["has_summary"] is True
    assert st2["has_explanation"] is True
    assert st2["has_concepts"] is True
    assert st2["has_references"] is True

    # Validação Estudo 3 (apenas C=True)
    st3 = studies_by_id[s3_id]
    assert st3["has_summary"] is False
    assert st3["has_explanation"] is False
    assert st3["has_concepts"] is True
    assert st3["has_references"] is False
