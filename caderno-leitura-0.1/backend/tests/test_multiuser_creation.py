import uuid

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.book import Book
from app.models.canvas_frame import CanvasFrame
from app.models.category import Category
from app.models.study import Study
from app.models.study_canvas_node import StudyCanvasNode
from app.models.study_relation import StudyRelation
from app.models.user import User


@pytest.fixture
def client_and_engine(tmp_path):
    path = tmp_path / "multiuser-create-test.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)

    # Cria um usuário B ativo para os testes
    user_b_id = str(uuid.uuid4())
    with Session(engine) as session:
        user_b = User(
            id=user_b_id,
            username="leitor_b",
            display_name="Leitor B de Testes",
            status="ativo",
        )
        session.add(user_b)
        session.commit()

    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session

    with TestClient(application) as client:
        yield client, engine, user_b_id

    engine.dispose()


def test_create_book_default_owner_when_no_header(client_and_engine):
    client, engine, _ = client_and_engine
    resp = client.post("/api/books", json={"title": "Livro do Proprietário", "author": "Autor A"})
    assert resp.status_code == 201
    book_data = resp.json()
    assert book_data["id"] > 0

    with Session(engine) as session:
        book = session.get(Book, book_data["id"])
        assert book is not None
        assert book.user_id == DEFAULT_OWNER_ID


def test_create_book_with_user_b_header(client_and_engine):
    client, engine, user_b_id = client_and_engine
    resp = client.post(
        "/api/books",
        json={"title": "Livro do Leitor B", "author": "Autor B"},
        headers={"X-User-Id": user_b_id},
    )
    assert resp.status_code == 201
    book_data = resp.json()

    with Session(engine) as session:
        book = session.get(Book, book_data["id"])
        assert book is not None
        assert book.user_id == user_b_id


def test_create_chapter_checks_book_ownership(client_and_engine):
    client, _, user_b_id = client_and_engine

    # Livro criado pelo proprietário padrão
    resp_book = client.post("/api/books", json={"title": "Livro A", "author": "Autor A"})
    book_id = resp_book.json()["id"]

    # Leitor B tenta criar capítulo no Livro A -> deve retornar 404 (anti-IDOR)
    resp_chap_b = client.post(
        f"/api/books/{book_id}/chapters",
        json={"name": "Capítulo Invasor"},
        headers={"X-User-Id": user_b_id},
    )
    assert resp_chap_b.status_code == 404
    assert "não encontrado" in resp_chap_b.json()["detail"].lower()

    # Proprietário cria capítulo no próprio livro -> sucesso 201
    resp_chap_a = client.post(
        f"/api/books/{book_id}/chapters",
        json={"name": "Capítulo Legítimo"},
    )
    assert resp_chap_a.status_code == 201


def test_create_study_and_assigns_user_id(client_and_engine):
    client, engine, user_b_id = client_and_engine

    # Criar livro e capítulo para o Leitor B
    r_book = client.post(
        "/api/books",
        json={"title": "Livro B", "author": "Autor B"},
        headers={"X-User-Id": user_b_id},
    )
    book_id = r_book.json()["id"]

    r_chap = client.post(
        f"/api/books/{book_id}/chapters",
        json={"name": "Capítulo B1"},
        headers={"X-User-Id": user_b_id},
    )
    chap_id = r_chap.json()["id"]

    # Leitor B cria estudo
    r_study = client.post(
        "/api/studies",
        json={
            "chapter_id": chap_id,
            "title": "Estudo de B",
            "summary": "Resumo do estudo",
        },
        headers={"X-User-Id": user_b_id},
    )
    assert r_study.status_code == 201
    study_id = r_study.json()["id"]

    with Session(engine) as session:
        study = session.get(Study, study_id)
        assert study is not None
        assert study.user_id == user_b_id


def test_create_study_relation_validates_ownership(client_and_engine):
    client, engine, user_b_id = client_and_engine

    # Criar 1 livro e 2 estudos para o proprietário
    r_book_a = client.post("/api/books", json={"title": "Livro A", "author": "A"})
    b_id_a = r_book_a.json()["id"]
    r_ch_a = client.post(f"/api/books/{b_id_a}/chapters", json={"name": "Cap 1"})
    ch_id_a = r_ch_a.json()["id"]
    s1_a = client.post(
        "/api/studies",
        json={"chapter_id": ch_id_a, "title": "Estudo A1", "summary": "Resumo A1"},
    ).json()["id"]
    s2_a = client.post(
        "/api/studies",
        json={"chapter_id": ch_id_a, "title": "Estudo A2", "summary": "Resumo A2"},
    ).json()["id"]

    # Criar 1 livro e 1 estudo para Leitor B
    r_book_b = client.post("/api/books", json={"title": "Livro B", "author": "B"}, headers={"X-User-Id": user_b_id})
    b_id_b = r_book_b.json()["id"]
    r_ch_b = client.post(f"/api/books/{b_id_b}/chapters", json={"name": "Cap B"}, headers={"X-User-Id": user_b_id})
    ch_id_b = r_ch_b.json()["id"]
    s1_b = client.post(
        "/api/studies",
        json={"chapter_id": ch_id_b, "title": "Estudo B1", "summary": "Resumo B1"},
        headers={"X-User-Id": user_b_id},
    ).json()["id"]

    # Leitor B tenta relacionar seu estudo com estudo do proprietário -> 404
    r_cross = client.post(
        "/api/study-relations",
        json={
            "source_study_id": s1_b,
            "target_study_id": s1_a,
            "relation_type": "relacionado_com",
            "description": "Tentativa cruzada",
        },
        headers={"X-User-Id": user_b_id},
    )
    assert r_cross.status_code == 404

    # Proprietário relaciona dois estudos próprios -> sucesso 201
    r_rel_a = client.post(
        "/api/study-relations",
        json={
            "source_study_id": s1_a,
            "target_study_id": s2_a,
            "relation_type": "relacionado_com",
            "description": "Relação válida",
        },
    )
    assert r_rel_a.status_code == 201
    rel_id = r_rel_a.json()["id"]

    with Session(engine) as session:
        rel = session.get(StudyRelation, rel_id)
        assert rel is not None
        assert rel.user_id == DEFAULT_OWNER_ID


def test_create_user_category(client_and_engine):
    client, engine, user_b_id = client_and_engine

    # Leitor B cria categoria personalizada
    r_cat = client.post(
        "/api/categories",
        json={"id": "epistemologia-b", "name": "Epistemologia Pessoal", "parent_id": None},
        headers={"X-User-Id": user_b_id},
    )
    assert r_cat.status_code == 201

    with Session(engine) as session:
        cat = session.get(Category, "epistemologia-b")
        assert cat is not None
        assert cat.user_id == user_b_id


def test_create_canvas_frame_and_nodes_assigns_user(client_and_engine):
    client, engine, user_b_id = client_and_engine

    # Criar livro, capítulo e estudo para o Leitor B
    r_book = client.post("/api/books", json={"title": "Livro Canvas B"}, headers={"X-User-Id": user_b_id})
    b_id = r_book.json()["id"]
    r_ch = client.post(f"/api/books/{b_id}/chapters", json={"name": "Cap Canvas"}, headers={"X-User-Id": user_b_id})
    ch_id = r_ch.json()["id"]
    r_st = client.post(f"/api/studies", json={"chapter_id": ch_id, "summary": "Resumo"}, headers={"X-User-Id": user_b_id})
    st_id = r_st.json()["id"]

    # Criar moldura para o livro de B
    r_frame = client.post(
        f"/api/books/{b_id}/canvas/frames",
        json={"title": "Moldura de B", "color": "neutral", "pos_x": 10.0, "pos_y": 20.0, "width": 300.0, "height": 200.0},
        headers={"X-User-Id": user_b_id},
    )
    assert r_frame.status_code == 201
    frame_id = r_frame.json()["id"]

    # Salvar nó no canvas para o estudo de B
    r_batch = client.put(
        f"/api/books/{b_id}/canvas",
        json={"nodes": [{"study_id": st_id, "pos_x": 50.0, "pos_y": 60.0, "z_index": 1}]},
        headers={"X-User-Id": user_b_id},
    )
    assert r_batch.status_code == 200

    with Session(engine) as session:
        frame = session.get(CanvasFrame, frame_id)
        assert frame is not None
        assert frame.user_id == user_b_id

        stmt = select(StudyCanvasNode).where(StudyCanvasNode.study_id == st_id)
        node = session.scalars(stmt).first()
        assert node is not None
        assert node.user_id == user_b_id
