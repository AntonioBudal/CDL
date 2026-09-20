"""Testes automatizados isolados para o Dashboard 2.0 (F07).

Valida endpoint consolidado /api/dashboard/summary, estudos recentes ordenados,
identificação de estudos órfãos, conexões semânticas recentes e exclusão de soft delete.
"""
from datetime import UTC, datetime, timedelta
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app


@pytest.fixture
def client_and_db(tmp_path):
    """Configura base SQLite temporária e TestClient 100% isolado em tmp_path."""
    db_path = tmp_path / "acervo_dashboard_v2" / "caderno.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

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
            yield client, engine
    finally:
        engine.dispose()


def test_empty_dashboard_v2(client_and_db):
    client, _ = client_and_db
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()

    assert data["summary"]["total_books"] == 0
    assert data["summary"]["total_studies"] == 0
    assert data["summary"]["total_relations"] == 0
    assert data["summary"]["total_categories"] >= 0
    assert data["summary"]["unlinked_studies_count"] == 0
    assert data["recent_studies"] == []
    assert data["unlinked_studies"] == []
    assert data["latest_relations"] == []


def test_dashboard_summary_recent_studies(client_and_db):
    client, _ = client_and_db

    # Cria Livro
    res_b = client.post("/api/books", json={"title": "A República", "author": "Platão"})
    assert res_b.status_code == 201
    b_id = res_b.json()["id"]

    # Cria Capítulo
    res_c = client.post(f"/api/books/{b_id}/chapters", json={"name": "Livro VII"})
    assert res_c.status_code == 201
    c_id = res_c.json()["id"]

    # Cria Estudo 1
    res_s1 = client.post(
        "/api/studies",
        json={
            "chapter_id": c_id,
            "title": "Alegoria da Caverna",
            "summary": "Estudo sobre sombras e luz",
            "location": "514a",
        },
    )
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    # Cria Estudo 2
    res_s2 = client.post(
        "/api/studies",
        json={
            "chapter_id": c_id,
            "title": "O Filósofo-Rei",
            "summary": "Estudo sobre a dialética e liderança",
            "location": "520a",
        },
    )
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    # Consulta Dashboard
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()

    assert data["summary"]["total_books"] == 1
    assert data["summary"]["total_studies"] == 2
    assert len(data["recent_studies"]) == 2

    # S2 foi criado por último, deve ser o primeiro
    assert data["recent_studies"][0]["study_id"] == s2_id
    assert data["recent_studies"][0]["title"] == "O Filósofo-Rei"
    assert data["recent_studies"][0]["book_title"] == "A República"
    assert data["recent_studies"][0]["chapter_title"] == "Livro VII"
    assert data["recent_studies"][0]["reading_status"] == "rascunho"

    # Atualiza S1 para alterar updated_at
    client.patch(
        f"/api/studies/{s1_id}",
        json={"title": "Alegoria da Caverna (Revisado)"},
    )

    res2 = client.get("/api/dashboard/summary")
    data2 = res2.json()
    # Agora S1 é o mais recente
    assert data2["recent_studies"][0]["study_id"] == s1_id
    assert data2["recent_studies"][0]["title"] == "Alegoria da Caverna (Revisado)"


def test_unlinked_studies_and_recent_relations(client_and_db):
    client, _ = client_and_db

    # Cria Livro e Capítulo
    res_b = client.post("/api/books", json={"title": "Ética a Nicômaco", "author": "Aristóteles"})
    b_id = res_b.json()["id"]
    res_c = client.post(f"/api/books/{b_id}/chapters", json={"name": "Livro I"})
    c_id = res_c.json()["id"]

    # Cria 3 estudos
    res_s1 = client.post("/api/studies", json={"chapter_id": c_id, "title": "Conceito de Eudaimonia", "summary": "Felicidade suprema", "location": "1094a"})
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    res_s2 = client.post("/api/studies", json={"chapter_id": c_id, "title": "A Virtude Moral", "summary": "Hábito e justa medida", "location": "1103a"})
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    res_s3 = client.post("/api/studies", json={"chapter_id": c_id, "title": "Justiça e Equidade", "summary": "Virtude completa", "location": "1129a"})
    assert res_s3.status_code == 201
    s3_id = res_s3.json()["id"]

    # Sem relações: todos os 3 são órfãos
    res = client.get("/api/dashboard/summary")
    data = res.json()
    assert data["summary"]["unlinked_studies_count"] == 3
    assert data["summary"]["total_relations"] == 0
    assert len(data["unlinked_studies"]) == 3
    assert len(data["latest_relations"]) == 0

    # Cria relação semântica entre s1 e s2
    res_rel = client.post(
        f"/api/studies/{s1_id}/relations",
        json={
            "target_study_id": s2_id,
            "relation_type": "complementa",
            "description": "A virtude é caminho para a eudaimonia.",
        },
    )
    assert res_rel.status_code == 201

    # Agora s1 e s2 estão conectados! Apenas s3 deve ser órfão.
    res_after = client.get("/api/dashboard/summary")
    data_after = res_after.json()
    assert data_after["summary"]["unlinked_studies_count"] == 1
    assert data_after["summary"]["total_relations"] == 1
    assert len(data_after["unlinked_studies"]) == 1
    assert data_after["unlinked_studies"][0]["study_id"] == s3_id

    # Verifica latest_relations
    assert len(data_after["latest_relations"]) == 1
    rel_item = data_after["latest_relations"][0]
    assert rel_item["relation_type"] == "complementa"
    assert rel_item["source_study_id"] == s1_id
    assert rel_item["source_study_title"] == "Conceito de Eudaimonia"
    assert rel_item["target_study_id"] == s2_id
    assert rel_item["target_study_title"] == "A Virtude Moral"
    assert rel_item["source_book_title"] == "Ética a Nicômaco"
    assert rel_item["target_book_title"] == "Ética a Nicômaco"


def test_soft_deleted_items_excluded_from_dashboard(client_and_db):
    client, _ = client_and_db

    # Cria Livro A
    res_b1 = client.post("/api/books", json={"title": "Livro Alfa", "author": "Autor A"})
    b1_id = res_b1.json()["id"]
    res_c1 = client.post(f"/api/books/{b1_id}/chapters", json={"name": "Capítulo A"})
    c1_id = res_c1.json()["id"]

    res_s1 = client.post("/api/studies", json={"chapter_id": c1_id, "title": "Estudo Alfa", "summary": "Resumo Alfa", "location": "p. 1"})
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    # Cria Livro B
    res_b2 = client.post("/api/books", json={"title": "Livro Beta", "author": "Autor B"})
    b2_id = res_b2.json()["id"]
    res_c2 = client.post(f"/api/books/{b2_id}/chapters", json={"name": "Capítulo B"})
    c2_id = res_c2.json()["id"]

    res_s2 = client.post("/api/studies", json={"chapter_id": c2_id, "title": "Estudo Beta", "summary": "Resumo Beta", "location": "p. 2"})
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    # Conecta s1 e s2
    res_con = client.post(
        f"/api/studies/{s1_id}/relations",
        json={"target_study_id": s2_id, "relation_type": "relacionado_com"},
    )
    assert res_con.status_code == 201

    # Estado inicial com 2 estudos conectados
    res_init = client.get("/api/dashboard/summary")
    data_init = res_init.json()
    assert data_init["summary"]["total_studies"] == 2
    assert data_init["summary"]["total_relations"] == 1
    assert data_init["summary"]["unlinked_studies_count"] == 0

    # Move s2 para a lixeira
    res_trash = client.post(f"/api/studies/{s2_id}/trash")
    assert res_trash.status_code == 200

    # Dashboard deve excluir s2:
    # total_studies = 1 (apenas s1)
    # total_relations = 0 (relação com s2 está latente/inativa)
    # unlinked_studies_count = 1 (s1 agora não possui relações ativas)
    res_after_trash = client.get("/api/dashboard/summary")
    data_trash = res_after_trash.json()
    assert data_trash["summary"]["total_studies"] == 1
    assert data_trash["summary"]["total_relations"] == 0
    assert data_trash["summary"]["unlinked_studies_count"] == 1
    assert data_trash["unlinked_studies"][0]["study_id"] == s1_id
    assert len(data_trash["latest_relations"]) == 0
    assert all(s["study_id"] != s2_id for s in data_trash["recent_studies"])

    # Restaura s2
    res_restore = client.post(f"/api/studies/{s2_id}/restore")
    assert res_restore.status_code == 200
    res_restored = client.get("/api/dashboard/summary")
    data_restored = res_restored.json()
    assert data_restored["summary"]["total_studies"] == 2
    assert data_restored["summary"]["total_relations"] == 1
    assert data_restored["summary"]["unlinked_studies_count"] == 0
    assert len(data_restored["latest_relations"]) == 1


def test_categories_count_in_summary(client_and_db):
    client, _ = client_and_db

    res_cats = client.get("/api/categories")
    assert res_cats.status_code == 200
    expected_categories = len(res_cats.json())

    res = client.get("/api/dashboard/summary")
    data = res.json()
    assert data["summary"]["total_categories"] == expected_categories
    assert data["summary"]["total_categories"] > 0
