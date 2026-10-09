"""Testes de integração para Templates Estruturados de Estudo (F0.7.15)."""
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text
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
    path = tmp_path / "test-study-templates.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def create_sample_chapter(client, book_title="Livro de Filosofia"):
    res_b = client.post("/api/books", json={"title": book_title, "author": "Autor de Teste"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]
    return book_id, chapter_id


def test_create_study_with_canonical_template(api):
    client, _, _ = api
    book_id, chapter_id = create_sample_chapter(client)

    payload = {
        "chapter_id": chapter_id,
        "title": "Conceito de Dialética",
        "location": "p. 45",
        "template_id": "conceito",
        "summary": "### Definição Essencial\n- Movimento de superação de contradições.",
        "explanation": "### Origem\n- Heráclito, Platão e Hegel.",
        "concepts": "### Aplicações\n- Método de investigação.",
        "references": "### Limitações\n- Crítica de Popper.",
    }
    res = client.post("/api/studies", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["template_id"] == "conceito"
    assert data["title"] == "Conceito de Dialética"

    # Verificar recuperação via GET
    res_get = client.get(f"/api/studies/{data['id']}")
    assert res_get.status_code == 200
    assert res_get.json()["template_id"] == "conceito"


def test_create_study_default_template_classico(api):
    client, _, _ = api
    book_id, chapter_id = create_sample_chapter(client)

    payload = {
        "chapter_id": chapter_id,
        "title": "Estudo sem template explícito",
        "summary": "Resumo clássico do trecho.",
    }
    res = client.post("/api/studies", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["template_id"] == "classico"


def test_create_study_invalid_template_normalized_to_classico(api):
    client, _, _ = api
    book_id, chapter_id = create_sample_chapter(client)

    payload = {
        "chapter_id": chapter_id,
        "title": "Estudo com template desconhecido",
        "template_id": "modelo_inexistente_xyz",
        "summary": "Resumo geral.",
    }
    res = client.post("/api/studies", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["template_id"] == "classico"


def test_update_study_template_via_put_and_patch(api):
    client, _, _ = api
    book_id, chapter_id = create_sample_chapter(client)

    # 1. Cria com clássico
    res_create = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Tese sobre Linguagem",
            "template_id": "classico",
            "summary": "Resumo inicial.",
        },
    )
    assert res_create.status_code == 201
    study_id = res_create.json()["id"]
    version_initial = res_create.json()["version"]

    # 2. Atualiza via PUT para 'argumento'
    res_put = client.put(
        f"/api/studies/{study_id}",
        json={
            "template_id": "argumento",
            "summary": "### Tese Central\n- A linguagem estrutura o pensamento.",
        },
    )
    assert res_put.status_code == 200
    data_put = res_put.json()
    assert data_put["template_id"] == "argumento"
    assert data_put["version"] == version_initial + 1

    # 3. Atualiza via PATCH para 'resenha'
    res_patch = client.patch(
        f"/api/studies/{study_id}",
        json={
            "template_id": "resenha",
        },
    )
    assert res_patch.status_code == 200
    data_patch = res_patch.json()
    assert data_patch["template_id"] == "resenha"
    assert data_patch["version"] == version_initial + 2


def test_list_studies_includes_template_id(api):
    client, _, _ = api
    book_id, chapter_id = create_sample_chapter(client)

    res_1 = client.post(
        "/api/studies",
        json={"chapter_id": chapter_id, "title": "Estudo 1", "template_id": "comparativo", "summary": "Comparação A vs B."},
    )
    assert res_1.status_code == 201

    res_list = client.get(f"/api/chapters/{chapter_id}/studies")
    assert res_list.status_code == 200
    items = res_list.json()
    assert len(items) >= 1
    found = next((i for i in items if i["id"] == res_1.json()["id"]), None)
    assert found is not None
    assert found["template_id"] == "comparativo"


def test_legacy_study_fallback_to_classico(api):
    client, engine, _ = api
    book_id, chapter_id = create_sample_chapter(client)

    # Simular estudo inserido diretamente no banco com template_id nulo ou inexistente
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO studies (user_id, chapter_id, title, location, source_response, summary, explanation, concepts, "references", notes, position, reading_status, visibility, version, template_id)
                VALUES (:u, :c, :t, '', '', 'Resumo antigo', '', '', '', '', 0, 'rascunho', 'inherit', 1, NULL)
                """
            ),
            {"u": DEFAULT_OWNER_ID, "c": chapter_id, "t": "Estudo Legado Sem Template"},
        )
        res_row = conn.execute(text("SELECT id FROM studies WHERE title = 'Estudo Legado Sem Template'")).fetchone()
        legacy_id = res_row[0]

    # Verificar que a API retorna 'classico' como fallback transparente
    res_get = client.get(f"/api/studies/{legacy_id}")
    assert res_get.status_code == 200
    assert res_get.json()["template_id"] == "classico"

    # Verificar listagem do capítulo também com fallback
    res_list = client.get(f"/api/chapters/{chapter_id}/studies")
    assert res_list.status_code == 200
    legacy_item = next((i for i in res_list.json() if i["id"] == legacy_id), None)
    assert legacy_item is not None
    assert legacy_item["template_id"] == "classico"
