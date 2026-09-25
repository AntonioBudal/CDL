from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.local_credential import LocalCredential
from app.models.study import Study
from app.models.study_canvas_node import StudyCanvasNode
from app.models.user import User
from app.models.user_preference import UserPreference


USER_A_ID = "11111111-1111-1111-1111-111111111111"
USER_B_ID = "22222222-2222-2222-2222-222222222222"


@pytest.fixture
def sync_harness(tmp_path: Path, monkeypatch):
    """Fixture hermética com banco SQLite isolado e clientes de teste para User A e User B."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")

    db_path = tmp_path / "sync_test.db"
    db_url = f"sqlite:///{db_path.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with testing_session_local() as db_session:
        user_a = User(
            id=USER_A_ID,
            username="leitor_a",
            email="leitor_a@exemplo.com",
            display_name="Leitor A",
            role="user",
            status="ativo",
        )
        cred_a = LocalCredential(
            user_id=user_a.id,
            password_hash=hash_password("Senha123!"),
        )
        user_b = User(
            id=USER_B_ID,
            username="leitor_b",
            email="leitor_b@exemplo.com",
            display_name="Leitor B",
            role="user",
            status="ativo",
        )
        cred_b = LocalCredential(
            user_id=user_b.id,
            password_hash=hash_password("Senha123!"),
        )
        db_session.add_all([user_a, cred_a, user_b, cred_b])

        book_a = Book(
            user_id=USER_A_ID,
            title="Livro do Leitor A",
            author="Autor Notável",
            version=1,
        )
        db_session.add(book_a)
        db_session.flush()

        chap_a = Chapter(
            book_id=book_a.id,
            name="Capítulo I",
            position=1,
        )
        db_session.add(chap_a)
        db_session.flush()

        study_a = Study(
            user_id=USER_A_ID,
            chapter_id=chap_a.id,
            title="Estudo Original",
            location="p. 15",
            summary="Resumo inicial",
            explanation="Explicação inicial",
            concepts="Conceitos iniciais",
            references="Referências iniciais",
            notes="Notas iniciais",
            version=1,
        )
        db_session.add(study_a)

        book_b = Book(
            user_id=USER_B_ID,
            title="Livro do Leitor B",
            author="Outro Autor",
            version=1,
        )
        db_session.add(book_b)
        db_session.commit()

        book_a_id = book_a.id
        chapter_a_id = chap_a.id
        study_a_id = study_a.id
        book_b_id = book_b.id

    application = create_app()

    def override_session():
        with testing_session_local() as s:
            yield s

    application.dependency_overrides[get_session] = override_session
    client = TestClient(application)

    return {
        "client": client,
        "engine": engine,
        "session_factory": testing_session_local,
        "book_a_id": book_a_id,
        "chapter_a_id": chapter_a_id,
        "study_a_id": study_a_id,
        "book_b_id": book_b_id,
        "headers_a": {"X-User-Id": USER_A_ID},
        "headers_b": {"X-User-Id": USER_B_ID},
    }


# ==============================================================================
# Phase 3 / User Story 1: OCC Concurrency Tests (T011)
# ==============================================================================


def test_study_sequential_occ_advances_version(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]
    study_id = sync_harness["study_a_id"]

    res = client.get(f"/api/studies/{study_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == 1

    # Atualização 1: informando expected_version=1
    patch1 = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Título Revisado 1", "expected_version": 1},
        headers=headers,
    )
    assert patch1.status_code == 200
    data1 = patch1.json()
    assert data1["title"] == "Título Revisado 1"
    assert data1["version"] == 2

    # Atualização 2: informando expected_version=2
    patch2 = client.patch(
        f"/api/studies/{study_id}",
        json={"notes": "Notas revisadas", "expected_version": 2},
        headers=headers,
    )
    assert patch2.status_code == 200
    data2 = patch2.json()
    assert data2["notes"] == "Notas revisadas"
    assert data2["version"] == 3


def test_study_occ_conflict_returns_409_with_server_state(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]
    study_id = sync_harness["study_a_id"]

    # Dispositivo A lê o estudo na versão 1
    res = client.get(f"/api/studies/{study_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["version"] == 1

    # Dispositivo B salva primeiro e avança para a versão 2
    patch_b = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Salvo pelo Dispositivo B", "expected_version": 1},
        headers=headers,
    )
    assert patch_b.status_code == 200
    assert patch_b.json()["version"] == 2

    # Dispositivo A tenta salvar informando a versão desatualizada expected_version=1
    patch_a = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Tentativa Concorrente do Dispositivo A", "expected_version": 1},
        headers=headers,
    )
    assert patch_a.status_code == 409
    conflict = patch_a.json()

    # Validação estrita do payload de conflito (ConflictErrorResponse)
    assert "concorrência" in conflict["detail"].lower()
    assert conflict["entity_id"] == study_id
    assert conflict["entity_type"] == "study"
    assert conflict["server_version"] == 2
    assert "server_updated_at" in conflict
    assert conflict["server_data"]["id"] == study_id
    assert conflict["server_data"]["title"] == "Salvo pelo Dispositivo B"
    assert conflict["server_data"]["version"] == 2


def test_study_occ_forced_overwrite(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]
    study_id = sync_harness["study_a_id"]

    # Avança para versão 2
    res1 = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Versão Intermediária", "expected_version": 1},
        headers=headers,
    )
    assert res1.status_code == 200
    assert res1.json()["version"] == 2

    # Conflito detectado com expected_version=1
    conflict_res = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Rascunho Local que Vencerá", "expected_version": 1},
        headers=headers,
    )
    assert conflict_res.status_code == 409
    server_ver = conflict_res.json()["server_version"]
    assert server_ver == 2

    # Sobrescrita forçada: cliente reenvia com expected_version = server_version
    overwrite_res = client.patch(
        f"/api/studies/{study_id}",
        json={"title": "Rascunho Local que Vencerá", "expected_version": server_ver},
        headers=headers,
    )
    assert overwrite_res.status_code == 200
    data = overwrite_res.json()
    assert data["title"] == "Rascunho Local que Vencerá"
    assert data["version"] == 3


def test_book_sequential_occ_and_conflict(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]
    book_id = sync_harness["book_a_id"]

    # Leitura inicial
    res = client.get(f"/api/books/{book_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["version"] == 1

    # Atualização normal com expected_version=1 -> avança para versão 2
    patch1 = client.patch(
        f"/api/books/{book_id}",
        json={"title": "Livro do Leitor A (Edição Revisada)", "expected_version": 1},
        headers=headers,
    )
    assert patch1.status_code == 200
    assert patch1.json()["version"] == 2

    # Tentativa com expected_version desatualizada (1) -> 409 Conflict
    patch_stale = client.patch(
        f"/api/books/{book_id}",
        json={"subtitle": "Subtítulo Concorrente", "expected_version": 1},
        headers=headers,
    )
    assert patch_stale.status_code == 409
    conflict = patch_stale.json()
    assert conflict["entity_id"] == book_id
    assert conflict["entity_type"] == "book"
    assert conflict["server_version"] == 2
    assert conflict["server_data"]["title"] == "Livro do Leitor A (Edição Revisada)"

    # Sobrescrita com expected_version=2 -> avança para versão 3
    patch_overwrite = client.patch(
        f"/api/books/{book_id}",
        json={"subtitle": "Subtítulo Sobrescrito", "expected_version": 2},
        headers=headers,
    )
    assert patch_overwrite.status_code == 200
    assert patch_overwrite.json()["version"] == 3
    assert patch_overwrite.json()["subtitle"] == "Subtítulo Sobrescrito"


# ==============================================================================
# Phase 4 / User Story 2: Incremental Change Feed Tests (T017)
# ==============================================================================


def test_sync_changes_returns_full_state_when_since_omitted(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]
    book_a_id = sync_harness["book_a_id"]
    study_a_id = sync_harness["study_a_id"]
    book_b_id = sync_harness["book_b_id"]

    res = client.get("/api/sync/changes", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "server_time" in data
    # Updated items contain User A's data
    book_ids = [b["id"] for b in data["updated"]["books"]]
    study_ids = [s["id"] for s in data["updated"]["studies"]]
    assert book_a_id in book_ids
    assert study_a_id in study_ids

    # User B's data MUST NOT leak into User A's sync response (IDOR protection)
    assert book_b_id not in book_ids

    # When since is omitted, deleted lists are empty
    assert data["deleted"]["book_ids"] == []
    assert data["deleted"]["study_ids"] == []


def test_sync_changes_incremental_filter_and_tombstones(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]
    chapter_id = sync_harness["chapter_a_id"]
    study_id = sync_harness["study_a_id"]

    # 1. Primeira sincronização: captura o timestamp t0
    res0 = client.get("/api/sync/changes", headers=headers)
    assert res0.status_code == 200
    t0 = res0.json()["server_time"]

    # 2. Cria um novo estudo após t0
    create_res = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo Criado Após T0",
            "summary": "Resumo novo",
        },
        headers=headers,
    )
    assert create_res.status_code == 201
    new_study_id = create_res.json()["id"]

    # 3. Move o estudo original para a lixeira (tombstone)
    trash_res = client.post(f"/api/studies/{study_id}/trash", headers=headers)
    assert trash_res.status_code == 200

    # 4. Consulta incremental com since=t0
    sync_res = client.get(f"/api/sync/changes?since={t0}", headers=headers)
    assert sync_res.status_code == 200
    changes = sync_res.json()

    # O estudo recém-criado deve estar em 'updated'
    updated_study_ids = [s["id"] for s in changes["updated"]["studies"]]
    assert new_study_id in updated_study_ids

    # O estudo movido para a lixeira deve estar em 'deleted'
    assert study_id in changes["deleted"]["study_ids"]


# ==============================================================================
# Phase 5 / User Story 3: User Preferences Sync & OCC Tests (T022)
# ==============================================================================


def test_preferences_default_creation_and_persistence(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]

    # Leitura de preferências inexistentes cria com valores padrão
    res = client.get("/api/preferences", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["active_superclass"] == "mecanica"
    assert data["superclass_intensity"] == 1.0
    assert data["preferred_view_mode"] == "grid"
    assert data["font_family"] == "garamond"
    assert data["font_scale"] == 1.0
    assert data["theme_mode"] == "dark"
    assert data["version"] == 1
    assert data["user_id"] == USER_A_ID


def test_preferences_update_and_version_advancement(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]

    # Atualização normal com expected_version=1 -> avança para versão 2
    put_res = client.put(
        "/api/preferences",
        json={
            "active_superclass": "zero-g",
            "superclass_intensity": 1.5,
            "font_scale": 1.2,
            "tree_collapsed_state": [10, 20],
            "expected_version": 1,
        },
        headers=headers,
    )
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["active_superclass"] == "zero-g"
    assert data["superclass_intensity"] == 1.5
    assert data["font_scale"] == 1.2
    assert data["tree_collapsed_state"] == [10, 20]
    assert data["version"] == 2


def test_preferences_occ_conflict(sync_harness):
    client = sync_harness["client"]
    headers = sync_harness["headers_a"]

    # 1. Atualização inicial avança para versão 2
    put_ok = client.put(
        "/api/preferences",
        json={
            "active_superclass": "zero-g",
            "expected_version": 1,
        },
        headers=headers,
    )
    assert put_ok.status_code == 200
    assert put_ok.json()["version"] == 2

    # 2. Tentativa de atualizar com expected_version desatualizada (1) quando o servidor já está em 2
    conflict_res = client.put(
        "/api/preferences",
        json={
            "active_superclass": "dimensional",
            "expected_version": 1,
        },
        headers=headers,
    )
    assert conflict_res.status_code == 409
    conflict = conflict_res.json()
    assert conflict["entity_type"] == "preference"
    assert conflict["server_version"] == 2
    assert conflict["server_data"]["active_superclass"] == "zero-g"


def test_preferences_multiuser_isolation(sync_harness):
    client = sync_harness["client"]
    headers_b = sync_harness["headers_b"]

    # Usuário B deve obter suas próprias preferências padrão, sem contaminação do Usuário A
    res_b = client.get("/api/preferences", headers=headers_b)
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["user_id"] == USER_B_ID
    assert data_b["active_superclass"] == "mecanica"
    assert data_b["version"] == 1


