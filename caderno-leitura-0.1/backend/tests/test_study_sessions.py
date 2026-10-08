"""Testes de integração para Sessões Estruturadas de Estudo e Auditoria (F0.7.14)."""
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
    path = tmp_path / "test-study-sessions.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def create_sample_structure(client, book_title="Livro de Ensaio"):
    res_b = client.post("/api/books", json={"title": book_title, "author": "Autor de Teste"})
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
            "summary": "Resumo sintético para estudos e testes de recordação.",
            "explanation": "Explicação aprofundada com termos e ideias principais.",
            "concepts": "Conceito Central",
            "references": "Fonte 1",
        },
    )
    assert res_s.status_code == 201
    study_id = res_s.json()["id"]
    return book_id, chapter_id, study_id


def add_highlight(client, study_id, section="explanation", kind="question", text="Termo Chave", note="O que é?"):
    res = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": section,
            "start_offset": 0,
            "end_offset": len(text),
            "selected_text": text,
            "kind": kind,
            "note": note,
        },
    )
    assert res.status_code == 201
    return res.json()["id"]


def test_start_study_session_empty_error(api):
    client, _, _ = api
    res = client.post("/api/study-sessions/start", json={"scope_type": "quick"})
    assert res.status_code == 400
    assert "Nenhum item pendente" in res.json()["detail"]


def test_start_study_session_quick(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)

    # Cria 3 cartões
    h1 = add_highlight(client, study_id, kind="question", text="Conceito A", note="Explique A")
    h2 = add_highlight(client, study_id, kind="hidden", text="Lacuna B")
    h3 = add_highlight(client, study_id, kind="question", text="Conceito C", note="Explique C")

    res = client.post("/api/study-sessions/start", json={"scope_type": "quick", "limit": 10})
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "in_progress"
    assert data["total_items"] == 3
    assert data["completed_items"] == 0
    assert len(data["pending_cards"]) == 3
    assert data["scope_type"] == "quick"


def test_start_study_session_dynamic_scope(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client, "Livro Curto")

    # Apenas 2 cartões no livro
    h1 = add_highlight(client, study_id, kind="question", text="Questão 1")
    h2 = add_highlight(client, study_id, kind="hidden", text="Oclusão 2")

    # Solicita 10 itens para o livro, mas só tem 2 -> ajusta dinamicamente para 2 (Q2: A)
    res = client.post(
        "/api/study-sessions/start",
        json={"scope_type": "book", "book_id": book_id, "limit": 10},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["total_items"] == 2
    assert len(data["pending_cards"]) == 2
    assert data["book_id"] == book_id


def test_answer_item_and_update_highlight(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)
    h1 = add_highlight(client, study_id, kind="question", text="Memória Ativa")

    res_start = client.post("/api/study-sessions/start", json={"scope_type": "quick", "limit": 5})
    session_id = res_start.json()["id"]

    # Registra resposta
    res_ans = client.post(
        f"/api/study-sessions/{session_id}/items",
        json={"highlight_id": h1, "rating": "easy", "time_spent_seconds": 12},
    )
    assert res_ans.status_code == 200
    item_data = res_ans.json()
    assert item_data["session_id"] == session_id
    assert item_data["rating"] == "easy"
    assert item_data["time_spent_seconds"] == 12

    # Verifica se os carimbos foram atualizados em study_highlights
    _, engine, _ = api
    with Session(engine) as s:
        from app.models.study_highlight import StudyHighlight
        hl_db = s.get(StudyHighlight, h1)
        assert hl_db.review_count == 1
        assert hl_db.last_rating == "easy"
        assert hl_db.last_reviewed_at is not None


def test_complete_study_session_summary(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)
    h1 = add_highlight(client, study_id, kind="question", text="Item 1")
    h2 = add_highlight(client, study_id, kind="question", text="Item 2")

    res_start = client.post("/api/study-sessions/start", json={"scope_type": "quick", "limit": 2})
    session_id = res_start.json()["id"]

    client.post(
        f"/api/study-sessions/{session_id}/items",
        json={"highlight_id": h1, "rating": "easy", "time_spent_seconds": 5},
    )
    client.post(
        f"/api/study-sessions/{session_id}/items",
        json={"highlight_id": h2, "rating": "medium", "time_spent_seconds": 7},
    )

    # Conclusão formal
    res_complete = client.post(
        f"/api/study-sessions/{session_id}/complete",
        json={"duration_seconds": 15},
    )
    assert res_complete.status_code == 200
    data = res_complete.json()
    session_info = data["session"]
    assert session_info["status"] == "completed"
    assert session_info["completed_items"] == 2
    assert session_info["easy_count"] == 1
    assert session_info["medium_count"] == 1
    assert session_info["duration_seconds"] == 15
    assert data["accuracy_rate"] > 0
    assert data["next_reviews_summary"]["easy"] == 1
    assert data["next_reviews_summary"]["medium"] == 1


def test_interrupt_session_preserves_answers(api):
    client, engine, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)
    h1 = add_highlight(client, study_id, kind="question", text="Item Respondido")
    h2 = add_highlight(client, study_id, kind="question", text="Item Nao Respondido")

    res_start = client.post("/api/study-sessions/start", json={"scope_type": "quick", "limit": 2})
    session_id = res_start.json()["id"]

    # Responde apenas o primeiro
    client.post(
        f"/api/study-sessions/{session_id}/items",
        json={"highlight_id": h1, "rating": "hard", "time_spent_seconds": 8},
    )

    # Interrompe a sessão (Q1: A)
    res_interrupt = client.post(f"/api/study-sessions/{session_id}/interrupt")
    assert res_interrupt.status_code == 200
    data = res_interrupt.json()
    assert data["status"] == "interrupted"
    assert data["completed_items"] == 1
    assert data["hard_count"] == 1

    # Confirma que h1 manteve os carimbos
    with Session(engine) as s:
        from app.models.study_highlight import StudyHighlight
        hl_db = s.get(StudyHighlight, h1)
        assert hl_db.review_count == 1
        assert hl_db.last_rating == "hard"


def test_session_history_isolation(api):
    client, engine, _ = api
    book_id, chapter_id, study_id = create_sample_structure(client)
    h1 = add_highlight(client, study_id, kind="question", text="Destaque Leitor 1")

    res_start = client.post("/api/study-sessions/start", json={"scope_type": "quick"})
    session_id = res_start.json()["id"]
    client.post(
        f"/api/study-sessions/{session_id}/items",
        json={"highlight_id": h1, "rating": "easy", "time_spent_seconds": 10},
    )
    client.post(f"/api/study-sessions/{session_id}/complete")

    # Consulta histórico do usuário padrão
    res_hist = client.get("/api/study-sessions/history")
    assert res_hist.status_code == 200
    items = res_hist.json()
    assert len(items) == 1
    assert items[0]["id"] == session_id

    # Cria segundo usuário e verifica que histórico vem vazio (isolamento estrito)
    other_user_id = "11111111-2222-3333-4444-555555555555"
    with Session(engine) as s:
        other_user = User(
            id=other_user_id,
            username="leitor2",
            display_name="Leitor 2",
            email="leitor2@exemplo.com",
            role="reader",
            status="ativo",
        )
        s.add(other_user)
        s.commit()

    with make_client(engine, user_id=other_user_id) as client2:
        res_hist2 = client2.get("/api/study-sessions/history")
        assert res_hist2.status_code == 200
        assert len(res_hist2.json()) == 0

