"""Testes de backend para F0.7.12: Backlinks e Menções entre Estudos ([[...]])."""
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
import uuid

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import Book, Chapter, Study, StudyMention, User
from app.services.study_mention_service import (
    extract_context_snippet,
    extract_mentions_from_study_text,
)


def make_client(engine):
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    return TestClient(application)


@pytest.fixture
def api(tmp_path):
    path = tmp_path / "test-mentions.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def test_extract_mentions_and_snippet():
    text = (
        "No primeiro parágrafo discutimos o tema central. Em seguida, "
        "conforme exposto em [[Crítica da Razão Pura]], investigamos a faculdade humana "
        "e também citamos [[Ética a Nicômaco|42]] para fundamentar as premissas."
    )
    mentions = extract_mentions_from_study_text(text)
    assert len(mentions) == 2

    # Menção 1: padrão sem ID
    title1, id1, snippet1 = mentions[0]
    assert title1 == "Crítica da Razão Pura"
    assert id1 is None
    assert "[[Crítica da Razão Pura]]" in snippet1

    # Menção 2: com ID explícito
    title2, id2, snippet2 = mentions[1]
    assert title2 == "Ética a Nicômaco"
    assert id2 == 42
    assert "[[Ética a Nicômaco|42]]" in snippet2


def test_study_mentions_sync_and_backlinks(api):
    client, engine, _ = api

    # 1. Criar livro e capítulo
    res_b = client.post("/api/books", json={"title": "Filosofia Moderna", "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    # 2. Criar estudo alvo (Target)
    res_s1 = client.post("/api/studies", json={
        "chapter_id": chapter_id,
        "title": "Crítica da Razão Pura",
        "summary": "Estudo sobre epistemologia kantiana.",
    })
    assert res_s1.status_code == 201
    target_id = res_s1.json()["id"]

    # 3. Criar estudo de origem (Source) com menção natural [[Crítica da Razão Pura]]
    res_s2 = client.post("/api/studies", json={
        "chapter_id": chapter_id,
        "title": "Idealismo Transcendental",
        "summary": "De acordo com as teses de [[Crítica da Razão Pura]], o espaço e o tempo são formas a priori.",
    })
    assert res_s2.status_code == 201
    source_id = res_s2.json()["id"]

    # 4. Verificar se a menção foi persistida na tabela study_mentions
    with Session(engine) as session:
        mentions = session.scalars(select(StudyMention)).all()
        assert len(mentions) == 1
        m = mentions[0]
        assert m.source_study_id == source_id
        assert m.target_study_id == target_id
        assert m.mention_text == "Crítica da Razão Pura"
        assert m.section == "summary"
        assert "[[Crítica da Razão Pura]]" in m.context_snippet

    # 5. Consultar endpoint de backlinks do estudo alvo
    res_bl = client.get(f"/api/studies/{target_id}/backlinks")
    assert res_bl.status_code == 200
    bl_data = res_bl.json()
    assert bl_data["total"] == 1
    assert len(bl_data["items"]) == 1
    item = bl_data["items"][0]
    assert item["source_study_id"] == source_id
    assert item["source_study_title"] == "Idealismo Transcendental"
    assert item["book_title"] == "Filosofia Moderna"
    assert item["chapter_name"] == "Capítulo 1"
    assert item["section"] == "summary"

    # 6. Atualizar estudo de origem removendo a menção
    res_update = client.patch(f"/api/studies/{source_id}", json={
        "summary": "Texto revisado sem referências a outros estudos.",
    })
    assert res_update.status_code == 200

    # Backlinks deve agora estar vazio
    res_bl_after = client.get(f"/api/studies/{target_id}/backlinks")
    assert res_bl_after.status_code == 200
    assert res_bl_after.json()["total"] == 0

    # 7. Atualizar adicionando menção com ID explícito [[Crítica da Razão Pura|target_id]]
    res_update2 = client.patch(f"/api/studies/{source_id}", json={
        "summary": f"Referência com ID explícito: [[Crítica da Razão Pura|{target_id}]].",
    })
    assert res_update2.status_code == 200

    res_bl_explicit = client.get(f"/api/studies/{target_id}/backlinks")
    assert res_bl_explicit.status_code == 200
    assert res_bl_explicit.json()["total"] == 1


def test_search_candidates_endpoint(api):
    client, _, _ = api

    res_b = client.post("/api/books", json={"title": "Teoria Geral", "author": "Autor"})
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo Central"})
    chapter_id = res_c.json()["id"]

    client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Estudo Alfa", "summary": "Conteúdo"})
    client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Estudo Beta", "summary": "Conteúdo"})

    # Buscar com q
    res = client.get("/api/studies/search-candidates?q=Alfa")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["title"] == "Estudo Alfa"
    assert items[0]["chapter_name"] == "Capítulo Central"

    # Buscar todos
    res_all = client.get("/api/studies/search-candidates")
    assert res_all.status_code == 200
    assert len(res_all.json()) >= 2


def test_backlinks_suppression_on_trash(api):
    client, _, _ = api

    res_b = client.post("/api/books", json={"title": "Obras Reunidas", "author": "Pensador"})
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Seção 1"})
    chapter_id = res_c.json()["id"]

    res_s1 = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Conceito A", "summary": "Definição"})
    target_id = res_s1.json()["id"]

    res_s2 = client.post("/api/studies", json={
        "chapter_id": chapter_id,
        "title": "Comentário B",
        "summary": "Comenta [[Conceito A]].",
    })
    source_id = res_s2.json()["id"]

    # Backlink ativo inicialmente
    res_bl = client.get(f"/api/studies/{target_id}/backlinks")
    assert res_bl.json()["total"] == 1

    # Mover estudo de origem para lixeira
    res_del = client.post(f"/api/studies/{source_id}/trash")
    assert res_del.status_code == 200

    # Backlink deve ser ocultado
    res_bl_trash = client.get(f"/api/studies/{target_id}/backlinks")
    assert res_bl_trash.json()["total"] == 0

    # Restaurar estudo de origem
    res_rest = client.post(f"/api/studies/{source_id}/restore")
    assert res_rest.status_code == 200

    # Backlink deve reaparecer
    res_bl_restored = client.get(f"/api/studies/{target_id}/backlinks")
    assert res_bl_restored.json()["total"] == 1


def test_multiuser_isolation(api):
    client, engine, _ = api

    # Usuário 1 (padrão) cria livro e estudo
    res_b = client.post("/api/books", json={"title": "Livro Privado", "author": "Autor 1"})
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo"})
    chapter_id = res_c.json()["id"]

    res_s = client.post("/api/studies", json={"chapter_id": chapter_id, "title": "Estudo Secreto", "summary": "Notas"})
    s_id = res_s.json()["id"]

    # Criar Usuário 2 no banco com status ativo
    user2_id = str(uuid.uuid4())
    with Session(engine) as session:
        u2 = User(id=user2_id, username="leitor2", email="leitor2@exemplo.com", display_name="Leitor 2", status="ativo")
        session.add(u2)
        session.commit()

    # Usuário 2 tenta consultar backlinks do estudo do Usuário 1 -> 404
    headers_u2 = {"X-User-Id": user2_id}
    res_bl_u2 = client.get(f"/api/studies/{s_id}/backlinks", headers=headers_u2)
    assert res_bl_u2.status_code == 404

    # Usuário 2 busca candidatos -> não deve ver os estudos do Usuário 1
    res_cand_u2 = client.get("/api/studies/search-candidates?q=Secreto", headers=headers_u2)
    assert res_cand_u2.status_code == 200
    assert len(res_cand_u2.json()) == 0
