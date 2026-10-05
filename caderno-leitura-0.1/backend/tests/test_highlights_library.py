"""Testes de integração para a Biblioteca Transversal de Highlights e Anotações (F0.7.11)."""
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
    path = tmp_path / "test-highlights-library.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def create_structure(client, book_title="Livro Alfa", chapter_name="Capítulo 1", study_title="Estudo 1"):
    res_b = client.post("/api/books", json={"title": book_title, "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": chapter_name})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": study_title,
            "summary": "Resumo sintético para análise crítica.",
            "explanation": "Explicação detalhada dos conceitos.",
            "concepts": "Conceito Chave",
            "references": "Referência 1",
        },
    )
    assert res_s.status_code == 201
    study_id = res_s.json()["id"]

    return book_id, chapter_id, study_id


def test_highlights_library_empty(api):
    client, _, _ = api
    res = client.get("/api/highlights/library")
    assert res.status_code == 200
    data = res.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["available_books"] == []
    assert data["summary"]["total_highlights"] == 0


def test_highlights_library_aggregation_and_search(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_structure(client, "Crítica da Razão Pura", "Introdução", "Estudo Kantiano")

    # Criar 3 destaques
    res1 = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 15,
            "selected_text": "Resumo sintético",
            "color": "yellow",
            "kind": "highlight",
            "note": "Passagem epistemológica central",
        },
    )
    assert res1.status_code == 201

    res2 = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "explanation",
            "start_offset": 0,
            "end_offset": 20,
            "selected_text": "Explicação detalhada",
            "color": "green",
            "kind": "quote",
            "note": "Citação direta relevante",
        },
    )
    assert res2.status_code == 201

    res3 = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "concepts",
            "start_offset": 0,
            "end_offset": 14,
            "selected_text": "Conceito Chave",
            "color": "purple",
            "kind": "question",
            "note": "Qual o significado a priori?",
        },
    )
    assert res3.status_code == 201

    # Consulta geral
    res_lib = client.get("/api/highlights/library")
    assert res_lib.status_code == 200
    lib_data = res_lib.json()
    assert lib_data["total"] == 3
    assert len(lib_data["items"]) == 3

    item = lib_data["items"][0]
    assert item["book_title"] == "Crítica da Razão Pura"
    assert item["chapter_title"] == "Introdução"
    assert item["study_title"] == "Estudo Kantiano"
    assert len(lib_data["available_books"]) == 1
    assert lib_data["available_books"][0]["title"] == "Crítica da Razão Pura"

    # Busca por termo no trecho selecionado
    res_q1 = client.get("/api/highlights/library?q=sintético")
    assert res_q1.status_code == 200
    assert res_q1.json()["total"] == 1
    assert res_q1.json()["items"][0]["selected_text"] == "Resumo sintético"

    # Busca por termo na nota pessoal
    res_q2 = client.get("/api/highlights/library?q=priori")
    assert res_q2.status_code == 200
    assert res_q2.json()["total"] == 1
    assert res_q2.json()["items"][0]["kind"] == "question"


def test_highlights_library_filters_and_pagination(api):
    client, _, _ = api
    book1_id, _, s1 = create_structure(client, "Obra 1", "Cap 1", "Estudo 1")
    book2_id, _, s2 = create_structure(client, "Obra 2", "Cap 2", "Estudo 2")

    # Cria destaques no livro 1
    client.post(
        f"/api/studies/{s1}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 10,
            "selected_text": "Destaque Amarelo Obra 1",
            "color": "yellow",
            "kind": "highlight",
        },
    )
    client.post(
        f"/api/studies/{s1}/highlights",
        json={
            "section": "summary",
            "start_offset": 11,
            "end_offset": 20,
            "selected_text": "Destaque Azul Obra 1",
            "color": "blue",
            "kind": "quote",
        },
    )

    # Cria destaques no livro 2
    res_k_create = client.post(
        f"/api/studies/{s2}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 10,
            "selected_text": "Destaque Amarelo Obra 2",
            "color": "yellow",
            "kind": "question",
        },
    )
    assert res_k_create.status_code == 201

    # Filtro por book_id
    res_b = client.get(f"/api/highlights/library?book_id={book1_id}")
    assert res_b.status_code == 200
    assert res_b.json()["total"] == 2
    for it in res_b.json()["items"]:
        assert it["book_id"] == book1_id

    # Filtro combinado: book_id + color
    res_bc = client.get(f"/api/highlights/library?book_id={book1_id}&color=blue")
    assert res_bc.status_code == 200
    assert res_bc.json()["total"] == 1
    assert res_bc.json()["items"][0]["color"] == "blue"

    # Filtro combinado: kind=question
    res_k = client.get("/api/highlights/library?kind=question")
    assert res_k.status_code == 200
    assert res_k.json()["total"] == 1
    assert res_k.json()["items"][0]["book_id"] == book2_id

    # Paginação
    res_p1 = client.get("/api/highlights/library?page=1&per_page=2")
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert data_p1["total"] == 3
    assert len(data_p1["items"]) == 2
    assert data_p1["page"] == 1
    assert data_p1["per_page"] == 2

    res_p2 = client.get("/api/highlights/library?page=2&per_page=2")
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert len(data_p2["items"]) == 1
    assert data_p2["page"] == 2


def test_highlights_library_mutations_and_deletion(api):
    client, _, _ = api
    _, _, study_id = create_structure(client, "Obra Dinâmica", "Cap 1", "Estudo Dinâmico")

    # Cria highlight
    res_c = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 10,
            "selected_text": "Trecho Original",
            "color": "yellow",
            "kind": "highlight",
            "note": "Nota Inicial",
        },
    )
    assert res_c.status_code == 201
    h_id = res_c.json()["id"]

    # Edita nota inline
    res_u = client.patch(
        f"/api/studies/{study_id}/highlights/{h_id}",
        json={"note": "Nota Modificada Inline", "kind": "note", "color": "pink"},
    )
    assert res_u.status_code == 200

    # Verifica reflexo na biblioteca
    res_lib = client.get("/api/highlights/library")
    assert res_lib.status_code == 200
    assert res_lib.json()["total"] == 1
    item = res_lib.json()["items"][0]
    assert item["note"] == "Nota Modificada Inline"
    assert item["kind"] == "note"
    assert item["color"] == "pink"

    # Exclui highlight
    res_d = client.delete(f"/api/studies/{study_id}/highlights/{h_id}")
    assert res_d.status_code == 204

    # Verifica remoção da biblioteca
    res_after = client.get("/api/highlights/library")
    assert res_after.status_code == 200
    assert res_after.json()["total"] == 0


def test_highlights_library_multiuser_isolation(api):
    import uuid

    client, engine, _ = api
    _, _, study_id_a = create_structure(client, "Livro do Usuário A", "Cap 1", "Estudo A")

    client.post(
        f"/api/studies/{study_id_a}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 6,
            "selected_text": "Resumo",
            "color": "yellow",
            "kind": "highlight",
            "note": "Nota secreta do usuário A",
        },
    )

    # Criar e consultar com usuário B
    user_b_id = str(uuid.uuid4())
    with Session(engine) as session:
        user_b = User(
            id=user_b_id,
            username="leitor_b",
            display_name="Leitor B",
            status="ativo",
        )
        session.add(user_b)
        session.commit()

    with make_client(engine, user_id=user_b_id) as client_b:
        res_b = client_b.get("/api/highlights/library")
        assert res_b.status_code == 200
        assert res_b.json()["total"] == 0
        assert res_b.json()["items"] == []


def test_highlights_library_hides_trashed_studies(api):
    client, _, _ = api
    book_id, chapter_id, study_id = create_structure(client, "Livro Descartável", "Cap 1", "Estudo a Excluir")

    res = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 6,
            "selected_text": "Resumo",
            "color": "yellow",
            "kind": "highlight",
            "note": "Nota temporária",
        },
    )
    assert res.status_code == 201

    # Antes de mover para a lixeira
    res_before = client.get("/api/highlights/library")
    assert res_before.json()["total"] == 1

    # Mover estudo para a lixeira (soft-delete)
    res_trash = client.post(f"/api/studies/{study_id}/trash")
    assert res_trash.status_code == 200

    # Depois de mover para a lixeira
    res_after = client.get("/api/highlights/library")
    assert res_after.status_code == 200
    assert res_after.json()["total"] == 0
    assert res_after.json()["items"] == []
