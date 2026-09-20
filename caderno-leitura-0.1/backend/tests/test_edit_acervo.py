"""Testes automatizados isolados de edição de livros, capítulos e concorrência."""
from datetime import UTC, datetime, timedelta
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.core.config import BACKEND_DIR
from app.main import app
from app.models import Book, Chapter, Study


@pytest.fixture
def client_and_db(tmp_path, monkeypatch):
    """Configura base SQLite temporária e TestClient isolado."""
    db_path = tmp_path / "acervo_edicao" / "caderno.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("CADERNO_DATABASE_PATH", str(db_path))

    # Executa migrações no banco temporário
    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.attributes["database_path"] = db_path
    command.upgrade(alembic_cfg, "head")

    with TestClient(app) as client:
        yield client, db_path


def test_update_book_success(client_and_db):
    """T007: Valida atualização com sucesso de título, autor, subtítulo e ano."""
    client, _ = client_and_db

    # Cria livro inicial
    create_res = client.post("/api/books", json={"title": "Livro Original", "author": "Autor Original"})
    assert create_res.status_code == 201
    book_id = create_res.json()["id"]

    # Edita todos os metadados
    patch_res = client.patch(
        f"/api/books/{book_id}",
        json={
            "title": "A Arte da Guerra",
            "author": "Sun Tzu",
            "subtitle": "Tratado Estratégico Clássico",
            "year": 2021,
        },
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["title"] == "A Arte da Guerra"
    assert data["author"] == "Sun Tzu"
    assert data["subtitle"] == "Tratado Estratégico Clássico"
    assert data["year"] == 2021
    assert data["updated_at"] is not None

    # Verifica persistência listando livros
    list_res = client.get("/api/books")
    assert list_res.status_code == 200
    books = list_res.json()
    assert any(b["id"] == book_id and b["subtitle"] == "Tratado Estratégico Clássico" for b in books)


def test_quickstart_scenario_1_integrity_preservation(client_and_db):
    """Cenário 1 do Quickstart: Edição de livro preserva capítulos e estudos intactos."""
    client, _ = client_and_db

    # Cria livro, capítulo e estudo
    book = client.post("/api/books", json={"title": "Livro Original", "author": "Autor Inicial"}).json()
    chap = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    study = client.post(
        "/api/studies",
        json={
            "chapter_id": chap["id"],
            "title": "Estudo Associado",
            "summary": "Resumo do estudo",
            "source_response": "Texto original",
        },
    ).json()

    # Edita metadados do livro
    patch_res = client.patch(
        f"/api/books/{book['id']}",
        json={
            "title": "Livro Atualizado",
            "author": "Novo Autor",
            "subtitle": "Subtítulo de Teste",
            "year": 2024,
        },
    )
    assert patch_res.status_code == 200

    # Comprova que capítulo e estudo continuam estritamente vinculados e inalterados
    chapters = client.get(f"/api/books/{book['id']}/chapters").json()
    assert len(chapters) == 1
    assert chapters[0]["id"] == chap["id"]
    assert chapters[0]["name"] == "Capítulo 1"

    studies = client.get(f"/api/chapters/{chap['id']}/studies").json()
    assert len(studies) == 1
    assert studies[0]["id"] == study["id"]
    assert studies[0]["title"] == "Estudo Associado"



def test_update_book_rejects_empty_title(client_and_db):
    """T007: Título vazio ou com apenas espaços deve ser rejeitado com 422."""
    client, _ = client_and_db
    create_res = client.post("/api/books", json={"title": "Livro Inicial"})
    book_id = create_res.json()["id"]

    res = client.patch(f"/api/books/{book_id}", json={"title": "   "})
    assert res.status_code == 422


def test_update_book_rejects_invalid_year(client_and_db):
    """T007: Ano fora de 1000..2100 deve ser rejeitado com 422."""
    client, _ = client_and_db
    create_res = client.post("/api/books", json={"title": "Livro Inicial"})
    book_id = create_res.json()["id"]

    res_past = client.patch(f"/api/books/{book_id}", json={"year": 850})
    assert res_past.status_code == 422

    res_future = client.patch(f"/api/books/{book_id}", json={"year": 2500})
    assert res_future.status_code == 422


def test_update_book_not_found(client_and_db):
    """T007: Tentar editar livro inexistente retorna 404."""
    client, _ = client_and_db
    res = client.patch("/api/books/999999", json={"title": "Novo Título"})
    assert res.status_code == 404


def test_update_book_concurrency_conflict(client_and_db):
    """T007: Conflito de versão (expected_updated_at desatualizado) retorna 409."""
    client, _ = client_and_db
    create_res = client.post("/api/books", json={"title": "Livro Inicial"})
    book_id = create_res.json()["id"]

    # Simula cliente enviando expected_updated_at de 1 hora atrás
    stale_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    res = client.patch(
        f"/api/books/{book_id}",
        json={"title": "Tentativa de Sobrescrita", "expected_updated_at": stale_time},
    )
    assert res.status_code == 409
    assert "conflito" in res.json()["detail"].lower()


def test_update_chapter_name_success(client_and_db):
    """T012: Valida renomeação de capítulo com sucesso."""
    client, _ = client_and_db
    book = client.post("/api/books", json={"title": "Livro Teste"}).json()
    chap = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo Antigo"}).json()

    res = client.patch(
        f"/api/books/{book['id']}/chapters/{chap['id']}",
        json={"name": "Capítulo Novo"},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Capítulo Novo"
    assert res.json()["updated_at"] is not None

    # Consulta listagem
    chapters = client.get(f"/api/books/{book['id']}/chapters").json()
    assert len(chapters) == 1
    assert chapters[0]["name"] == "Capítulo Novo"


def test_update_chapter_rejects_empty_name(client_and_db):
    """T012: Nome em branco ou apenas espaços é rejeitado com 422."""
    client, _ = client_and_db
    book = client.post("/api/books", json={"title": "Livro Teste"}).json()
    chap = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo Original"}).json()

    res = client.patch(
        f"/api/books/{book['id']}/chapters/{chap['id']}",
        json={"name": "   "},
    )
    assert res.status_code == 422


def test_update_chapter_concurrency_conflict(client_and_db):
    """T012: Conflito de versão ao renomear capítulo retorna 409."""
    client, _ = client_and_db
    book = client.post("/api/books", json={"title": "Livro Teste"}).json()
    chap = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo Original"}).json()

    stale_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    res = client.patch(
        f"/api/books/{book['id']}/chapters/{chap['id']}",
        json={"name": "Novo Nome", "expected_updated_at": stale_time},
    )
    assert res.status_code == 409
    assert "conflito" in res.json()["detail"].lower()


def test_move_chapter_up_and_down_success(client_and_db):
    """T012: Reordenação atômica subir/descer (▲ / ▼) e limites."""
    client, _ = client_and_db
    book = client.post("/api/books", json={"title": "Livro Teste"}).json()
    c1 = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Cap 1"}).json()
    c2 = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Cap 2"}).json()
    c3 = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Cap 3"}).json()

    # Move c2 para cima (up)
    res = client.post(f"/api/books/{book['id']}/chapters/{c2['id']}/move", json={"direction": "up"})
    assert res.status_code == 200
    order = [c["name"] for c in res.json()]
    assert order == ["Cap 2", "Cap 1", "Cap 3"]

    # Tentativa de mover c2 para cima novamente deve retornar 400 (já no topo)
    res_top = client.post(f"/api/books/{book['id']}/chapters/{c2['id']}/move", json={"direction": "up"})
    assert res_top.status_code == 400
    assert "topo" in res_top.json()["detail"].lower()

    # Move c2 para baixo (down)
    res_down = client.post(f"/api/books/{book['id']}/chapters/{c2['id']}/move", json={"direction": "down"})
    assert res_down.status_code == 200
    order_down = [c["name"] for c in res_down.json()]
    assert order_down == ["Cap 1", "Cap 2", "Cap 3"]

    # Tentativa de mover c3 para baixo quando já é o último deve retornar 400
    res_bot = client.post(f"/api/books/{book['id']}/chapters/{c3['id']}/move", json={"direction": "down"})
    assert res_bot.status_code == 400
    assert "final" in res_bot.json()["detail"].lower()


def test_chapter_not_found(client_and_db):
    """T012: Rota retorna 404 para capítulo inexistente."""
    client, _ = client_and_db
    book = client.post("/api/books", json={"title": "Livro Teste"}).json()

    res_patch = client.patch(f"/api/books/{book['id']}/chapters/99999", json={"name": "Qualquer"})
    assert res_patch.status_code == 404

    res_move = client.post(f"/api/books/{book['id']}/chapters/99999/move", json={"direction": "up"})
    assert res_move.status_code == 404


def test_update_study_concurrency_conflict(client_and_db):
    """T017: Conflito de versão ao editar estudo retorna 409."""
    client, _ = client_and_db
    book = client.post("/api/books", json={"title": "Livro Teste"}).json()
    chap = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Cap 1"}).json()
    study = client.post(
        "/api/studies",
        json={
            "chapter_id": chap["id"],
            "title": "Estudo 1",
            "summary": "Resumo inicial",
            "source_response": "Texto original",
        },
    ).json()

    stale_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    res = client.patch(
        f"/api/studies/{study['id']}",
        json={"notes": "Tentativa", "expected_updated_at": stale_time},
    )
    assert res.status_code == 409
    assert "conflito" in res.json()["detail"].lower()


def test_update_study_preserves_source_response_and_forbids_tampering(client_and_db):
    """T017: Campo source_response é proibido no PATCH e permanece 100% imutável."""
    client, _ = client_and_db
    book = client.post("/api/books", json={"title": "Livro Teste"}).json()
    chap = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Cap 1"}).json()
    study = client.post(
        "/api/studies",
        json={
            "chapter_id": chap["id"],
            "title": "Estudo Imutável",
            "summary": "Resumo analítico",
            "source_response": "Texto original intocável",
        },
    ).json()

    # Tentativa de injetar source_response no PATCH é rejeitada com 422
    res_tamper = client.patch(
        f"/api/studies/{study['id']}",
        json={"notes": "Nota nova", "source_response": "Texto adulterado"},
    )
    assert res_tamper.status_code == 422

    # Atualização legítima preserva source_response no banco
    res_valid = client.patch(
        f"/api/studies/{study['id']}",
        json={"notes": "Nota legítima"},
    )
    assert res_valid.status_code == 200
    assert res_valid.json()["source_response"] == "Texto original intocável"
    assert res_valid.json()["notes"] == "Nota legítima"

    # Confere via GET
    get_res = client.get(f"/api/studies/{study['id']}").json()
    assert get_res["source_response"] == "Texto original intocável"
    assert get_res["notes"] == "Nota legítima"


def test_update_study_requires_at_least_one_analysis_section(client_and_db):
    """T017: Limpar todas as 4 seções analíticas é rejeitado com 422."""
    client, _ = client_and_db
    book = client.post("/api/books", json={"title": "Livro Teste"}).json()
    chap = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Cap 1"}).json()
    study = client.post(
        "/api/studies",
        json={
            "chapter_id": chap["id"],
            "title": "Estudo Analítico",
            "summary": "Resumo",
        },
    ).json()

    res = client.patch(
        f"/api/studies/{study['id']}",
        json={"summary": "", "explanation": "", "concepts": "", "references": ""},
    )
    assert res.status_code == 422

