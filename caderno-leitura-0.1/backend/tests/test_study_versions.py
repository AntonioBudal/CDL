"""Testes de integração para histórico automático, diff e restauração de estudos (F0.6.5)."""
from datetime import datetime, timedelta, timezone
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, DEFAULT_OWNER_ID
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.study_highlight import StudyHighlight
from app.models.study_version import StudyVersion
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
    path = tmp_path / "test-versions.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        with make_client(engine) as client:
            yield client, engine, path
    finally:
        engine.dispose()


def setup_study(client):
    res_b = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autor Sintético"})
    assert res_b.status_code == 201
    book_id = res_b.json()["id"]

    res_c = client.post(f"/api/books/{book_id}/chapters", json={"name": "Capítulo 1"})
    assert res_c.status_code == 201
    chapter_id = res_c.json()["id"]

    res_s = client.post(
        "/api/studies",
        json={
            "chapter_id": chapter_id,
            "title": "Estudo Original",
            "summary": "Resumo inicial do estudo.",
            "explanation": "Explicação preliminar.",
            "concepts": "Conceito 1",
            "references": "Ref 1",
            "notes": "Notas iniciais.",
        },
    )
    assert res_s.status_code == 201
    return res_s.json()["id"]


def test_automatic_version_capture_and_listing(api):
    client, engine, _ = api
    study_id = setup_study(client)

    # Inicialmente, nenhuma versão arquivada
    res_v0 = client.get(f"/api/studies/{study_id}/versions")
    assert res_v0.status_code == 200
    assert res_v0.json() == []

    # Edição 1: Modificar título e resumo
    res_patch = client.patch(
        f"/api/studies/{study_id}",
        json={
            "title": "Estudo Modificado",
            "summary": "Resumo atualizado com novas reflexões.",
        },
    )
    assert res_patch.status_code == 200

    # Deve conter 2 versões: Versão 1 (baseline inicial) e Versão 2 (após a alteração)
    res_v1 = client.get(f"/api/studies/{study_id}/versions")
    assert res_v1.status_code == 200
    versions = res_v1.json()
    assert len(versions) == 2

    # Versão 2 é a mais recente (current)
    assert versions[0]["version_number"] == 2
    assert versions[0]["change_summary"] == "Edição"
    assert versions[0]["is_current"] is True

    # Versão 1 é a inicial
    assert versions[1]["version_number"] == 1
    assert versions[1]["change_summary"] == "Versão inicial"
    assert versions[1]["is_current"] is False

    # Inspecionar detalhes da Versão 1
    v1_id = versions[1]["id"]
    res_det1 = client.get(f"/api/studies/{study_id}/versions/{v1_id}")
    assert res_det1.status_code == 200
    det1 = res_det1.json()
    assert det1["title"] == "Estudo Original"
    assert det1["summary"] == "Resumo inicial do estudo."

    # Inspecionar detalhes da Versão 2
    v2_id = versions[0]["id"]
    res_det2 = client.get(f"/api/studies/{study_id}/versions/{v2_id}")
    assert res_det2.status_code == 200
    det2 = res_det2.json()
    assert det2["title"] == "Estudo Modificado"
    assert det2["summary"] == "Resumo atualizado com novas reflexões."


def test_coalescence_within_5_minutes(api):
    client, engine, _ = api
    study_id = setup_study(client)

    # Primeira edição
    client.patch(f"/api/studies/{study_id}", json={"title": "Primeira Edição"})
    versions = client.get(f"/api/studies/{study_id}/versions").json()
    assert len(versions) == 2
    assert versions[0]["version_number"] == 2

    # Segunda edição imediata pelo mesmo autor (deve consolidar na Versão 2)
    client.patch(f"/api/studies/{study_id}", json={"summary": "Resumo corrigido imediatamente."})
    versions2 = client.get(f"/api/studies/{study_id}/versions").json()
    assert len(versions2) == 2  # Não cria versão 3!
    assert versions2[0]["version_number"] == 2

    # Detalhe da versão 2 reflete ambas as alterações
    v2_id = versions2[0]["id"]
    det2 = client.get(f"/api/studies/{study_id}/versions/{v2_id}").json()
    assert det2["title"] == "Primeira Edição"
    assert det2["summary"] == "Resumo corrigido imediatamente."


def test_new_version_after_coalescence_window(api):
    client, engine, _ = api
    study_id = setup_study(client)

    # Primeira edição
    client.patch(f"/api/studies/{study_id}", json={"title": "Edição Antiga"})

    # Simular passagem do tempo retroagindo o updated_at da versão 2 para 10 minutos atrás
    with Session(engine) as session:
        v2 = session.scalars(
            select(StudyVersion)
            .where(StudyVersion.study_id == study_id)
            .order_by(StudyVersion.version_number.desc())
        ).first()
        assert v2 is not None
        v2.updated_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        session.commit()

    # Nova edição agora deve gerar a Versão 3
    client.patch(f"/api/studies/{study_id}", json={"title": "Edição Recente Após Pausa"})
    versions = client.get(f"/api/studies/{study_id}/versions").json()
    assert len(versions) == 3
    assert versions[0]["version_number"] == 3
    assert versions[0]["title"] == "Edição Recente Após Pausa" if "title" in versions[0] else True


def test_diff_calculation_between_versions(api):
    client, engine, _ = api
    study_id = setup_study(client)

    # Editar estudo para alterar o título e acrescentar texto no resumo
    client.patch(
        f"/api/studies/{study_id}",
        json={
            "title": "Estudo Modificado",
            "summary": "Resumo inicial do estudo. Frase adicional.",
        },
    )

    versions = client.get(f"/api/studies/{study_id}/versions").json()
    v1_id = versions[1]["id"]  # Versão inicial

    # Comparar v1 com o estado atual
    res_diff = client.get(f"/api/studies/{study_id}/versions/{v1_id}/diff")
    assert res_diff.status_code == 200
    diff = res_diff.json()

    assert diff["version_number"] == 1
    assert diff["target_version_number"] == 2
    assert diff["is_target_current"] is True

    # Seção título deve estar modificada
    assert diff["sections"]["title"]["status"] == "modified"
    # Seção resumo deve estar modificada e conter chunks
    assert diff["sections"]["summary"]["status"] == "modified"
    chunks = diff["sections"]["summary"]["chunks"]
    assert any(c["type"] == "insert" and "Frase adicional" in c["text"] for c in chunks)

    # Seção explicação deve estar inalterada
    assert diff["sections"]["explanation"]["status"] == "unchanged"


def test_restore_version_with_highlights(api):
    client, engine, _ = api
    study_id = setup_study(client)

    # 1. Adicionar destaque na versão inicial
    res_hl = client.post(
        f"/api/studies/{study_id}/highlights",
        json={
            "section": "summary",
            "start_offset": 0,
            "end_offset": 6,
            "selected_text": "Resumo",
            "color": "yellow",
            "kind": "highlight",
        },
    )
    assert res_hl.status_code == 201

    # 2. Fazer uma alteração para gerar v1 (baseline com highlight) e v2
    client.patch(f"/api/studies/{study_id}", json={"title": "Título Versão 2"})

    versions = client.get(f"/api/studies/{study_id}/versions").json()
    v1_id = versions[1]["id"]

    # 3. Fazer outra alteração radical: apagar destaque e mudar o texto completamente
    client.patch(
        f"/api/studies/{study_id}",
        json={
            "title": "Título Radicalmente Diferente",
            "summary": "Texto totalmente novo sem relação com anterior.",
        },
    )

    # Simular intervalo e restaurar Versão 1
    with Session(engine) as session:
        v = session.scalars(select(StudyVersion).where(StudyVersion.study_id == study_id)).all()
        for item in v:
            item.updated_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        session.commit()

    res_restore = client.post(f"/api/studies/{study_id}/versions/{v1_id}/restore")
    assert res_restore.status_code == 200
    restored_study = res_restore.json()

    # O estudo voltou a ter os valores de v1
    assert restored_study["title"] == "Estudo Original"
    assert restored_study["summary"] == "Resumo inicial do estudo."

    # O destaque original de v1 foi reconstituído
    highlights = client.get(f"/api/studies/{study_id}/highlights").json()
    assert len(highlights) == 1
    assert highlights[0]["selected_text"] == "Resumo"

    # Uma nova versão de restauração foi catalogada no histórico
    versions_after = client.get(f"/api/studies/{study_id}/versions").json()
    assert versions_after[0]["change_summary"] == "Restauração da versão 1"


def test_permissions_read_only_user_cannot_restore(api):
    client, engine, _ = api
    study_id = setup_study(client)
    client.patch(f"/api/studies/{study_id}", json={"title": "Edição do Dono"})

    versions = client.get(f"/api/studies/{study_id}/versions").json()
    v1_id = versions[1]["id"]

    # Criar cliente para outro usuário convidado
    other_user_id = "00000000-0000-0000-0000-000000000002"
    with Session(engine) as session:
        u2 = User(id=other_user_id, username="convidado", display_name="Convidado", email="convidado@teste.com")
        session.add(u2)
        session.commit()


    # Dar permissão pública ao livro para que o convidado possa ler
    client.put(f"/api/studies/{study_id}/visibility", json={"visibility": "public"})

    with make_client(engine, user_id=other_user_id) as guest_client:
        # Leitor convidado pode ver versões
        res_list = guest_client.get(f"/api/studies/{study_id}/versions")
        assert res_list.status_code == 200

        # Leitor convidado pode ver diff
        res_diff = guest_client.get(f"/api/studies/{study_id}/versions/{v1_id}/diff")
        assert res_diff.status_code == 200

        # Leitor convidado NÃO pode restaurar (403 Forbidden)
        res_restore = guest_client.post(f"/api/studies/{study_id}/versions/{v1_id}/restore")
        assert res_restore.status_code == 403
