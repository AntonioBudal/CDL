"""Testes de backend para F0.7.13: Caixa de Entrada de Capturas (Inbox de Conhecimento)."""
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
import uuid

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import Book, Chapter, InboxCapture, Study, User


def make_client(engine):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application)


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-inbox.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def test_create_and_count_inbox_capture(api):
    client, engine, _ = api

    # 1. Contagem inicial deve ser zero
    res_c0 = client.get("/api/inbox/count")
    assert res_c0.status_code == 200
    assert res_c0.json()["count"] == 0

    # 2. Criar captura com conteúdo e fonte
    res = client.post(
        "/api/inbox",
        json={
            "content": "Ideia central sobre epistemologia sintética.",
            "source_hint": "Capítulo 1, página 15",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["content"] == "Ideia central sobre epistemologia sintética."
    assert data["source_hint"] == "Capítulo 1, página 15"
    assert data["status"] == "inbox"
    assert data["book_id"] is None
    assert data["promoted_study_id"] is None
    capture_id = data["id"]

    # 3. Contagem deve ser incrementada para 1
    res_c1 = client.get("/api/inbox/count")
    assert res_c1.status_code == 200
    assert res_c1.json()["count"] == 1

    # 4. Obter detalhes da captura criada
    res_get = client.get(f"/api/inbox/{capture_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == capture_id


def test_create_capture_with_book_and_validation(api):
    client, engine, _ = api

    # Criar um livro de teste
    res_b = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autor Teste"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    # Criar captura associada ao livro
    res_cap = client.post(
        "/api/inbox",
        json={
            "content": "Trecho memorável do livro de teste.",
            "book_id": book_id,
        },
    )
    assert res_cap.status_code == 201
    cap_data = res_cap.json()
    assert cap_data["book_id"] == book_id
    assert cap_data["book_title"] == "Livro de Teste"

    # Tentativa de criar com livro inexistente retorna 404
    res_err = client.post(
        "/api/inbox",
        json={
            "content": "Trecho inválido",
            "book_id": 99999,
        },
    )
    assert res_err.status_code == 404

    # Tentativa de criar com conteúdo em branco retorna 422
    res_empty = client.post(
        "/api/inbox",
        json={"content": "   "},
    )
    assert res_empty.status_code == 422


def test_list_and_search_captures(api):
    client, engine, _ = api

    client.post("/api/inbox", json={"content": "Pensamento sobre fenomenologia", "source_hint": "Husserl"})
    client.post("/api/inbox", json={"content": "Reflexão sobre lógica matemática", "source_hint": "Russell"})

    # Listar todos
    res_list = client.get("/api/inbox")
    assert res_list.status_code == 200
    items = res_list.json()
    assert len(items) == 2

    # Filtrar por termo de busca
    res_search = client.get("/api/inbox?q=fenomenologia")
    assert res_search.status_code == 200
    search_items = res_search.json()
    assert len(search_items) == 1
    assert "fenomenologia" in search_items[0]["content"]


def test_update_and_delete_capture(api):
    client, engine, _ = api

    res = client.post("/api/inbox", json={"content": "Texto inicial"})
    cid = res.json()["id"]

    # Atualizar conteúdo e arquivar
    res_patch = client.patch(
        f"/api/inbox/{cid}",
        json={"content": "Texto corrigido", "status": "archived"},
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["content"] == "Texto corrigido"
    assert res_patch.json()["status"] == "archived"

    # Item arquivado não conta no badge do inbox
    res_count = client.get("/api/inbox/count")
    assert res_count.json()["count"] == 0

    # Excluir captura
    res_del = client.delete(f"/api/inbox/{cid}")
    assert res_del.status_code == 204

    res_not_found = client.get(f"/api/inbox/{cid}")
    assert res_not_found.status_code == 404


def test_promote_and_link_capture_to_study(api):
    client, engine, _ = api

    # 1. Criar livro, capítulo e estudo
    res_b = client.post("/api/books", json={"title": "Ética", "author": "Spinoza"})
    bid = res_b.json()["id"]

    res_c = client.post(f"/api/books/{bid}/chapters", json={"name": "Parte 1"})
    chid = res_c.json()["id"]

    res_s = client.post("/api/studies", json={
        "chapter_id": chid,
        "title": "Da Substância",
        "summary": "Resumo das definições 1 a 8.",
        "references": "Edição clássica de 1677.",
    })
    sid = res_s.json()["id"]

    # 2. Criar captura 1 e promover
    res_cap1 = client.post("/api/inbox", json={"content": "Nota a ser promovida"})
    cid1 = res_cap1.json()["id"]

    res_prom = client.post(f"/api/inbox/{cid1}/promote", json={"study_id": sid})
    assert res_prom.status_code == 200
    data_prom = res_prom.json()
    assert data_prom["status"] == "promoted"
    assert data_prom["promoted_study_id"] == sid
    assert data_prom["promoted_study_title"] == "Da Substância"

    # 3. Criar captura 2 e vincular
    res_cap2 = client.post("/api/inbox", json={
        "content": "Citação sobre atributos divinos.",
        "source_hint": "Escólio da Proposição 10",
    })
    cid2 = res_cap2.json()["id"]

    res_link = client.post(f"/api/inbox/{cid2}/link", json={
        "target_study_id": sid,
        "target_section": "references",
    })
    assert res_link.status_code == 200
    data_link = res_link.json()
    assert data_link["status"] == "linked"
    assert data_link["promoted_study_id"] == sid

    # Verificar se o texto foi anexado ao estudo alvo
    res_study = client.get(f"/api/studies/{sid}")
    assert res_study.status_code == 200
    study_data = res_study.json()
    assert "Citação sobre atributos divinos." in study_data["references"]
    assert "Escólio da Proposição 10" in study_data["references"]


def test_multiuser_isolation(api):
    client, engine, _ = api

    # Criar segundo usuário diretamente no banco
    other_user_id = str(uuid.uuid4())
    with Session(engine) as session:
        other_user = User(
            id=other_user_id,
            username="outro_leitor",
            email="outro@exemplo.com",
            display_name="Outro Leitor",
        )
        session.add(other_user)
        # Inserir captura para o outro usuário
        other_cap = InboxCapture(
            user_id=other_user_id,
            content="Captura privada do outro leitor",
            status="inbox",
        )
        session.add(other_cap)
        session.commit()

    # Usuário padrão não deve ver a captura do outro usuário
    res_count = client.get("/api/inbox/count")
    assert res_count.json()["count"] == 0

    res_list = client.get("/api/inbox")
    assert len(res_list.json()) == 0
