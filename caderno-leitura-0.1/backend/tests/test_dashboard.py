"""Testes automatizados isolados para o Dashboard de Leitura (Métricas, Streak, Heatmap e Timeline)."""
from datetime import UTC, datetime, timedelta
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app


@pytest.fixture
def client_and_db(tmp_path):
    """Configura base SQLite temporária e TestClient 100% isolado em tmp_path."""
    db_path = tmp_path / "acervo_dashboard" / "caderno.db"
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


def test_dashboard_empty_database(client_and_db):
    client, _ = client_and_db
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["total_books"] == 0
    assert data["summary"]["total_studies"] == 0
    assert data["summary"]["total_reading_days"] == 0
    assert data["summary"]["current_streak"] == 0
    assert data["summary"]["avg_studies_per_book"] == 0.0
    assert len(data["heatmap"]) == 365
    assert len(data["timeline"]) == 0


def test_dashboard_summary_and_trash_exclusion(client_and_db):
    client, _ = client_and_db

    # Cria Livro 1
    res_b1 = client.post("/api/books", json={"title": "Dom Casmurro", "author": "Machado de Assis"})
    assert res_b1.status_code == 201
    b1_id = res_b1.json()["id"]

    # Cria Capítulo e 2 Estudos no Livro 1
    res_c1 = client.post(f"/api/books/{b1_id}/chapters", json={"name": "Capítulo 1"})
    c1_id = res_c1.json()["id"]

    res_s1 = client.post(
        "/api/studies",
        json={
            "chapter_id": c1_id,
            "title": "Olhos de Ressaca",
            "summary": "Resumo sintético 1",
            "location": "p. 10",
        },
    )
    assert res_s1.status_code == 201
    s1_id = res_s1.json()["id"]

    res_s2 = client.post(
        "/api/studies",
        json={
            "chapter_id": c1_id,
            "title": "Capitu e Bentinho",
            "summary": "Resumo sintético 2",
            "location": "p. 20",
        },
    )
    assert res_s2.status_code == 201
    s2_id = res_s2.json()["id"]

    # Cria Livro 2 (sem estudos)
    res_b2 = client.post("/api/books", json={"title": "Memórias Póstumas", "author": "Machado de Assis"})
    b2_id = res_b2.json()["id"]

    # Verifica métricas ativas
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    summary = res.json()["summary"]
    assert summary["total_books"] == 2
    assert summary["total_studies"] == 2
    assert summary["avg_studies_per_book"] == 1.0  # 2 estudos / 2 livros = 1.0
    assert summary["total_reading_days"] >= 1
    assert summary["current_streak"] >= 1

    # Move Estudo 2 para a lixeira
    res_del_s2 = client.post(f"/api/studies/{s2_id}/trash")
    assert res_del_s2.status_code == 200

    # Estudo na lixeira deixa de pontuar imediatamente
    res_after_s2_trash = client.get("/api/dashboard")
    summary_after = res_after_s2_trash.json()["summary"]
    assert summary_after["total_studies"] == 1
    assert summary_after["avg_studies_per_book"] == 0.5  # 1 estudo / 2 livros

    # Move Livro 1 para a lixeira (seus estudos também devem ser desconsiderados)
    client.post(f"/api/books/{b1_id}/trash")
    res_after_b1_trash = client.get("/api/dashboard")
    summary_b1_trash = res_after_b1_trash.json()["summary"]
    assert summary_b1_trash["total_books"] == 1  # Apenas Livro 2 ativo
    assert summary_b1_trash["total_studies"] == 0  # Nenhum estudo ativo restante
    assert summary_b1_trash["avg_studies_per_book"] == 0.0

    # Restaura Livro 1
    client.post(f"/api/books/{b1_id}/restore")
    res_restored = client.get("/api/dashboard")
    summary_restored = res_restored.json()["summary"]
    assert summary_restored["total_books"] == 2
    assert summary_restored["total_studies"] == 1  # Estudo 1 voltou; Estudo 2 ainda na lixeira
    assert summary_restored["avg_studies_per_book"] == 0.5


def test_streak_calculation_consecutive_days(client_and_db):
    client, engine = client_and_db
    now_utc = datetime.now(UTC)

    # Cria livro e insere carimbos sintéticos diretamente no banco descartável para testar streak
    res_b = client.post("/api/books", json={"title": "Livro de Sequência"})
    b_id = res_b.json()["id"]
    res_c = client.post(f"/api/books/{b_id}/chapters", json={"name": "Cap 1"})
    c_id = res_c.json()["id"]

    # Injeta estudos em 3 dias consecutivos: hoje, ontem e anteontem
    day0 = (now_utc).strftime("%Y-%m-%d %H:%M:%S")
    day1 = (now_utc - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    day2 = (now_utc - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    day4 = (now_utc - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")  # Buraco no dia -3

    with Session(engine) as session:
        # Atualiza created_at do livro para 4 dias atrás para não colidir com streak
        session.execute(
            text("UPDATE books SET created_at = :ts, updated_at = :ts WHERE id = :id"),
            {"ts": day4, "id": b_id},
        )
        # Insere estudos
        session.execute(
            text(
                "INSERT INTO studies (chapter_id, title, summary, created_at, updated_at) "
                "VALUES (:cid, 'Estudo D0', 'Sum', :d0, :d0), "
                "       (:cid, 'Estudo D1', 'Sum', :d1, :d1), "
                "       (:cid, 'Estudo D2', 'Sum', :d2, :d2), "
                "       (:cid, 'Estudo D4', 'Sum', :d4, :d4)"
            ),
            {"cid": c_id, "d0": day0, "d1": day1, "d2": day2, "d4": day4},
        )
        session.commit()

    res = client.get("/api/dashboard")
    assert res.status_code == 200
    summary = res.json()["summary"]
    # Dias consecutivos: D0, D1, D2 -> streak 3 (D4 não entra devido ao buraco em D3)
    assert summary["current_streak"] == 3
    assert summary["total_reading_days"] >= 4


def test_heatmap_points_and_levels(client_and_db):
    client, engine = client_and_db
    now_utc = datetime.now(UTC)
    today_str = now_utc.strftime("%Y-%m-%d")

    # Testa parâmetro days
    res_60 = client.get("/api/dashboard?days=60")
    assert res_60.status_code == 200
    assert len(res_60.json()["heatmap"]) == 60
    assert res_60.json()["heatmap"][-1]["date"] == today_str

    # Cria 1 livro (1 evento hoje -> level 1)
    res_b = client.post("/api/books", json={"title": "Livro de Calor"})
    b_id = res_b.json()["id"]

    res_l1 = client.get("/api/dashboard")
    today_pt = [p for p in res_l1.json()["heatmap"] if p["date"] == today_str][0]
    assert today_pt["count"] >= 1
    assert today_pt["level"] >= 1

    # Cria capítulo e mais 3 estudos hoje -> total >= 4 eventos hoje -> level 3
    res_c = client.post(f"/api/books/{b_id}/chapters", json={"name": "Cap 1"})
    c_id = res_c.json()["id"]
    for i in range(3):
        client.post(
            "/api/studies",
            json={"chapter_id": c_id, "title": f"Estudo Intensidade {i}", "summary": "Resumo"},
        )

    res_l3 = client.get("/api/dashboard")
    today_pt3 = [p for p in res_l3.json()["heatmap"] if p["date"] == today_str][0]
    assert today_pt3["count"] >= 4
    assert today_pt3["level"] == 3


def test_timeline_items_and_date_filtering(client_and_db):
    client, engine = client_and_db
    now_utc = datetime.now(UTC)
    today_str = now_utc.strftime("%Y-%m-%d")
    yesterday_str = (now_utc - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_ts = (now_utc - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    # Cria livro
    res_b = client.post("/api/books", json={"title": "Grande Sertão"})
    b_id = res_b.json()["id"]
    res_c = client.post(f"/api/books/{b_id}/chapters", json={"name": "Capítulo Único"})
    c_id = res_c.json()["id"]

    # Cria estudo hoje
    res_s = client.post(
        "/api/studies",
        json={"chapter_id": c_id, "title": "O Diabo na Rua", "summary": "Resumo hoje"},
    )
    s_id = res_s.json()["id"]

    # Injeta um estudo de ontem diretamente no banco
    with Session(engine) as session:
        session.execute(
            text(
                "INSERT INTO studies (chapter_id, title, summary, created_at, updated_at) "
                "VALUES (:cid, 'Estudo de Ontem', 'Sum Ontem', :yts, :yts)"
            ),
            {"cid": c_id, "yts": yesterday_ts},
        )
        session.commit()

    # Timeline geral (sem filtro)
    res_all = client.get("/api/dashboard")
    assert res_all.status_code == 200
    timeline = res_all.json()["timeline"]
    assert len(timeline) >= 3  # Livro, Estudo hoje, Estudo ontem
    actions = [item["action"] for item in timeline]
    assert "book_created" in actions
    assert "study_created" in actions

    # Timeline filtrada por data de hoje
    res_today = client.get(f"/api/dashboard?date={today_str}")
    assert res_today.status_code == 200
    timeline_today = res_today.json()["timeline"]
    for item in timeline_today:
        assert item["timestamp"].startswith(today_str)

    # Timeline filtrada por data de ontem
    res_yest = client.get(f"/api/dashboard?date={yesterday_str}")
    assert res_yest.status_code == 200
    timeline_yest = res_yest.json()["timeline"]
    assert any(item["title"] == "Estudo de Ontem" for item in timeline_yest)
    assert not any(item["title"] == "O Diabo na Rua" for item in timeline_yest)

    # Mover livro para a lixeira deve ocultar todos os itens da timeline
    client.post(f"/api/books/{b_id}/trash")
    res_after_trash = client.get("/api/dashboard")
    assert len(res_after_trash.json()["timeline"]) == 0


def test_dashboard_query_validation(client_and_db):
    client, _ = client_and_db
    # days < 30 deve falhar com 422
    res_invalid_days = client.get("/api/dashboard?days=10")
    assert res_invalid_days.status_code == 422

    # date com formato inválido deve falhar com 422
    res_invalid_date = client.get("/api/dashboard?date=19-09-2026")
    assert res_invalid_date.status_code == 422

