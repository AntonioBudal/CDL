"""Testes automatizados isolados para controle de concorrência otimista (HTTP 409) (T023)."""
from datetime import UTC, datetime, timedelta
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models import Book, Chapter, Study
from alembic import command
from alembic.config import Config


@pytest.fixture
def client_and_session(tmp_path: Path):
    db_path = tmp_path / "caderno_concurrency.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.attributes["database_path"] = db_path
    command.upgrade(alembic_cfg, "head")

    engine = create_sqlite_engine(db_path)
    app = create_app()

    def override_session():
        with Session(engine, expire_on_commit=False) as s:
            yield s

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    # Cria dados de teste
    with Session(engine) as s:
        book = Book(title="Livro Teste Concorrência", author="Autor")
        s.add(book)
        s.flush()
        chapter = Chapter(name="Capítulo 1", book_id=book.id)
        s.add(chapter)
        s.flush()
        study = Study(
            title="Estudo Original",
            location="Cap. 1",
            notes="Minhas reflexões",
            summary="Resumo inicial",
            chapter_id=chapter.id,
        )
        s.add(study)
        s.commit()
        study_id = study.id

    return client, engine, study_id


def test_concurrency_normal_sequential_update(client_and_session):
    client, engine, study_id = client_and_session

    res = client.get(f"/api/studies/{study_id}")
    assert res.status_code == 200
    study_data = res.json()
    t0 = study_data["updated_at"]

    patch_res = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Título Atualizado T1", "expected_updated_at": t0},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Título Atualizado T1"


def test_concurrency_conflict_409_when_modified_elsewhere(client_and_session):
    client, engine, study_id = client_and_session

    # Dispositivo A lê o estudo no momento T0
    res_a = client.get(f"/api/studies/{study_id}")
    t0 = res_a.json()["updated_at"]

    # Dispositivo B altera o estudo e salva
    # Forçamos o updated_at para +5 segundos no banco
    with Session(engine) as s:
        study = s.get(Study, study_id)
        study.title = "Alteração pelo Celular"
        study.updated_at = datetime.now(UTC) + timedelta(seconds=5)
        s.commit()

    # Dispositivo A tenta salvar suas alterações com o timestamp antigo t0
    patch_res = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Tentativa do PC", "expected_updated_at": t0},
    )

    assert patch_res.status_code == 409
    assert "concorrência" in patch_res.json()["detail"].lower()


def test_concurrency_clock_skew_tolerance(client_and_session):
    client, engine, study_id = client_and_session

    # Timestamp do banco ligeiramente à frente em menos de 1 segundo (clock skew)
    now = datetime.now(UTC)
    with Session(engine) as s:
        study = s.get(Study, study_id)
        study.updated_at = now + timedelta(milliseconds=500)
        s.commit()

    # Cliente envia now (dentro da janela de tolerância de 1s)
    patch_res = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Título com Skew Tolerado", "expected_updated_at": now.isoformat()},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Título com Skew Tolerado"


def test_concurrency_force_overwrite_flow(client_and_session):
    client, engine, study_id = client_and_session

    res_a = client.get(f"/api/studies/{study_id}")
    t0 = res_a.json()["updated_at"]

    # Simula conflito
    with Session(engine) as s:
        study = s.get(Study, study_id)
        study.title = "Alterado em outro dispositivo"
        study.updated_at = datetime.now(UTC) + timedelta(seconds=10)
        s.commit()

    # Dispositivo A recebe 409
    patch_res = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Minha versão que deve prevalecer", "expected_updated_at": t0},
    )
    assert patch_res.status_code == 409

    # Para 'Sobrescrever com minhas alterações', busca o updated_at mais recente e reenvia
    latest_study = client.get(f"/api/studies/{study_id}").json()
    t_latest = latest_study["updated_at"]

    retry_res = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Minha versão que deve prevalecer", "expected_updated_at": t_latest},
    )
    assert retry_res.status_code == 200
    assert retry_res.json()["title"] == "Minha versão que deve prevalecer"
