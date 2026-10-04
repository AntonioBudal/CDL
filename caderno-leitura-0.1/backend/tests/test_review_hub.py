"""Testes de integração para a Central de Revisão de Perguntas e Clozes."""
from datetime import UTC, datetime, timedelta
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.user import User


def make_client(engine, user_id: str = DEFAULT_OWNER_ID):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application, headers={"X-User-Id": user_id})


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-review-hub.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def create_sample_structure(client, book_title="Livro de Filosofia"):
    res_b = client.post("/api/books", json={"title": book_title, "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": f"Estudo sobre {book_title}",
            "summary": "O texto central para análise e estudo.",
            "explanation": "Explicação detalhada dos conceitos.",
            "concepts": "Conceito 1; Conceito 2",
            "references": "Referência primária",
        },
    )
    assert res_s.status_code == 201
    study_id = res_s.json()["id"]
    return book_id, chapter_id, study_id


def test_review_stats_empty(api):
    client, _, _ = api
    res = client.get("/api/review/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_eligible"] == 0
    assert data["total_questions"] == 0
    assert data["total_hidden"] == 0
    assert data["reviewed_today"] == 0
    assert data["pending_review"] == 0
    assert data["books"] == []


def test_review_stats_and_filtering(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)

    # 1 pergunta
    res_q = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "explanation",
            "start_offset": 0,
            "end_offset": 10,
            "selected_text": "Explicação",
            "kind": "question",
            "note": "Qual o ponto central?",
        },
    )
    assert res_q.status_code == 201

    # 1 cloze (termo oculto)
    res_h = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 2,
            "end_offset": 7,
            "selected_text": "texto",
            "prefix": "O ",
            "suffix": " central",
            "kind": "hidden",
        },
    )
    assert res_h.status_code == 201

    # 1 destaque comum (NÃO deve contar como item de revisão)
    res_normal = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 8,
            "end_offset": 15,
            "selected_text": "central",
            "kind": "highlight",
        },
    )
    assert res_normal.status_code == 201

    # Checar stats
    res_stats = client.get("/api/review/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_eligible"] == 2
    assert stats["total_questions"] == 1
    assert stats["total_hidden"] == 1
    assert stats["reviewed_today"] == 0
    assert stats["pending_review"] == 2
    assert len(stats["books"]) == 1
    assert stats["books"][0]["book_id"] == book_id
    assert stats["books"][0]["items_count"] == 2

    # Listar itens de revisão
    res_items = client.get("/api/review/items")
    assert res_items.status_code == 200
    items = res_items.json()
    assert len(items) == 2

    # Filtrar por kind=question
    res_q_only = client.get("/api/review/items?kind=question")
    assert res_q_only.status_code == 200
    assert len(res_q_only.json()) == 1
    assert res_q_only.json()[0]["kind"] == "question"
    assert res_q_only.json()[0]["question_text"] == "Qual o ponto central?"
    assert res_q_only.json()[0]["expected_answer"] == "Explicação"

    # Filtrar por kind=hidden
    res_h_only = client.get("/api/review/items?kind=hidden")
    assert res_h_only.status_code == 200
    assert len(res_h_only.json()) == 1
    assert res_h_only.json()[0]["kind"] == "hidden"
    assert "[...]" in res_h_only.json()[0]["question_text"]
    assert res_h_only.json()[0]["expected_answer"] == "texto"


def test_review_items_queue_prioritization_and_recording(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)

    # Criar 3 perguntas
    res1 = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 5,
            "selected_text": "Item1",
            "kind": "question",
            "note": "Pergunta 1",
        },
    )
    res2 = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 6,
            "end_offset": 11,
            "selected_text": "Item2",
            "kind": "question",
            "note": "Pergunta 2",
        },
    )
    res3 = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 12,
            "end_offset": 17,
            "selected_text": "Item3",
            "kind": "question",
            "note": "Pergunta 3",
        },
    )

    id1 = res1.json()["id"]
    id2 = res2.json()["id"]
    id3 = res3.json()["id"]

    # Avaliar id1 como 'easy'
    rec1 = client.post(f"/api/review/items/{id1}/record", json={"rating": "easy"})
    assert rec1.status_code == 200
    data1 = rec1.json()
    assert data1["id"] == id1
    assert data1["review_count"] == 1
    assert data1["last_rating"] == "easy"
    assert data1["last_reviewed_at"] is not None

    # Avaliar id2 como 'hard'
    rec2 = client.post(f"/api/review/items/{id2}/record", json={"rating": "hard"})
    assert rec2.status_code == 200
    data2 = rec2.json()
    assert data2["id"] == id2
    assert data2["review_count"] == 1
    assert data2["last_rating"] == "hard"

    # id3 ainda não foi avaliado (nunca revisado)
    # Pela heurística:
    # 1º: id3 (nunca revisado)
    # 2º: id2 (revisado, mas com last_rating == 'hard')
    # 3º: id1 (revisado com 'easy')
    res_sorted = client.get("/api/review/items")
    assert res_sorted.status_code == 200
    order = [item["id"] for item in res_sorted.json()]
    assert order == [id3, id2, id1]

    # Avaliar novamente id2 como 'medium' -> review_count deve ser 2
    rec2_again = client.post(f"/api/review/items/{id2}/record", json={"rating": "medium"})
    assert rec2_again.status_code == 200
    assert rec2_again.json()["review_count"] == 2
    assert rec2_again.json()["last_rating"] == "medium"


def test_invalid_rating_and_not_found(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)

    res = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 5,
            "selected_text": "Item1",
            "kind": "question",
            "note": "Pergunta",
        },
    )
    hl_id = res.json()["id"]

    # Rating inválido
    bad_res = client.post(f"/api/review/items/{hl_id}/record", json={"rating": "super_easy"})
    assert bad_res.status_code == 422

    # Highlight inexistente
    nf_res = client.post("/api/review/items/99999/record", json={"rating": "easy"})
    assert nf_res.status_code == 404


def test_trash_isolation(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)

    res = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 5,
            "selected_text": "Item1",
            "kind": "question",
            "note": "Pergunta",
        },
    )
    hl_id = res.json()["id"]

    # Verifica que está disponível
    res_items = client.get("/api/review/items")
    assert len(res_items.json()) == 1

    # Mover estudo para a lixeira
    del_res = client.post(f"/api/studies/{study_id}/trash")
    assert del_res.status_code == 200

    # Não deve mais aparecer em stats nem em items
    stats_after = client.get("/api/review/stats").json()
    assert stats_after["total_eligible"] == 0
    assert stats_after["books"] == []

    items_after = client.get("/api/review/items").json()
    assert len(items_after) == 0

    # Tentar avaliar item do estudo na lixeira deve retornar 404
    rec_after = client.post(f"/api/review/items/{hl_id}/record", json={"rating": "easy"})
    assert rec_after.status_code == 404


def test_multiuser_isolation(api):
    client_owner, engine, _ = api
    user_other = "00000000-0000-0000-0000-000000000002"

    with Session(engine) as session:
        u2 = User(
            id=user_other,
            username="leitor2",
            display_name="Leitor 2",
            email="leitor2@teste.com",
            status="ativo",
        )
        session.add(u2)
        session.commit()

    book_id, chapter_id, study_id = create_sample_structure(client_owner)

    res = client_owner.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 5,
            "selected_text": "Item1",
            "kind": "question",
            "note": "Pergunta de Owner",
        },
    )
    hl_id = res.json()["id"]

    with make_client(engine, user_id=user_other) as client_other:
        # Usuário B não vê itens do Usuário A
        stats_b = client_other.get("/api/review/stats").json()
        assert stats_b["total_eligible"] == 0

        items_b = client_other.get("/api/review/items").json()
        assert len(items_b) == 0

        # Usuário B não pode gravar avaliação no item de A
        rec_b = client_other.post(f"/api/review/items/{hl_id}/record", json={"rating": "easy"})
        assert rec_b.status_code == 404
