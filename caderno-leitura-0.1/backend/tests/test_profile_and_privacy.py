from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from PIL import Image
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_avatars_dir
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.dependencies import get_current_user
from app.main import create_app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.local_credential import LocalCredential
from app.models.study import Study
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.profile_service import get_or_create_profile

USER_A_ID = "11111111-1111-1111-1111-111111111111"
USER_B_ID = "22222222-2222-2222-2222-222222222222"


@pytest.fixture
def profile_harness(tmp_path: Path, monkeypatch):
    """Fixture hermética com banco SQLite temporário, diretório isolado de avatares e clientes para User A e User B."""
    avatars_dir = tmp_path / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CADERNO_AVATARS_DIR", str(avatars_dir))
    monkeypatch.setenv("REQUIRE_AUTH", "false")

    db_path = tmp_path / "profile_test.db"
    db_url = f"sqlite:///{db_path.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with testing_session_local() as db_session:
        user_a = User(
            id=USER_A_ID,
            username="leitor_a",
            email="leitor_a@exemplo.com",
            display_name="Leitor Alfa",
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
            display_name="Leitor Beta",
            role="user",
            status="ativo",
        )
        cred_b = LocalCredential(
            user_id=user_b.id,
            password_hash=hash_password("Senha123!"),
        )
        db_session.add_all([user_a, cred_a, user_b, cred_b])

        # Cria livros e estudos para estatísticas de leitura
        book_a = Book(
            user_id=USER_A_ID,
            title="Livro de Ensaio",
            author="Autor de Teste",
        )
        db_session.add(book_a)
        db_session.flush()

        chapter_a = Chapter(
            book_id=book_a.id,
            name="Capítulo 1",
            position=1,
        )
        db_session.add(chapter_a)
        db_session.flush()

        study_a = Study(
            user_id=USER_A_ID,
            chapter_id=chapter_a.id,
            title="Estudo Introdutório",
            summary="Resumo do estudo",
            explanation="Explicação detalhada",
            concepts="Conceitos principais",
            references="Referências",
        )
        db_session.add(study_a)

        # Garante a existência dos perfis
        get_or_create_profile(user_a, db_session)
        get_or_create_profile(user_b, db_session)
        db_session.commit()

    def get_test_db():
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_session] = get_test_db

    class Harness:
        def __init__(self):
            self.avatars_dir = avatars_dir
            self.session_factory = testing_session_local
            self.raw_client = TestClient(app)

        def client_for(self, user_id: str):
            class UserClient:
                def __init__(self, raw_client, uid):
                    self.raw = raw_client
                    self.headers = {"X-User-Id": uid}

                def get(self, url, **kwargs):
                    h = {**self.headers, **kwargs.pop("headers", {})}
                    return self.raw.get(url, headers=h, **kwargs)

                def post(self, url, **kwargs):
                    h = {**self.headers, **kwargs.pop("headers", {})}
                    return self.raw.post(url, headers=h, **kwargs)

                def put(self, url, **kwargs):
                    h = {**self.headers, **kwargs.pop("headers", {})}
                    return self.raw.put(url, headers=h, **kwargs)

                def delete(self, url, **kwargs):
                    h = {**self.headers, **kwargs.pop("headers", {})}
                    return self.raw.delete(url, headers=h, **kwargs)

            return UserClient(self.raw_client, user_id)

    return Harness()


# ============================================================================
# Testes US1: Gestão de Identidade Pública e Handle @username (T010)
# ============================================================================

def test_get_my_profile_returns_complete_private_data(profile_harness):
    client = profile_harness.client_for(USER_A_ID)
    res = client.get("/api/profile/me")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["user_id"] == USER_A_ID
    assert data["username"] == "leitor_a"
    assert data["display_name"] == "Leitor Alfa"
    assert data["email"] == "leitor_a@exemplo.com"
    assert data["profile_visibility"] == "public"
    assert data["dashboard_visibility"] == "private"
    assert data["reading_stats"]["total_books"] == 1
    assert data["reading_stats"]["total_studies"] == 1


def test_update_my_profile_validates_handle_and_bio(profile_harness):
    client = profile_harness.client_for(USER_A_ID)
    payload = {
        "username": "alfa_renovado",
        "display_name": "Alfa da Leitura",
        "bio": "Estudante dedicado de filosofia clássica.",
    }
    res = client.put("/api/profile/me", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["username"] == "alfa_renovado"
    assert data["display_name"] == "Alfa da Leitura"
    assert data["bio"] == "Estudante dedicado de filosofia clássica."

    # Verifica se User.username foi atualizado atomicamente
    with profile_harness.session_factory() as sess:
        u = sess.get(User, USER_A_ID)
        assert u.username == "alfa_renovado"
        assert u.display_name == "Alfa da Leitura"


def test_update_my_profile_rejects_duplicate_username_case_insensitive(profile_harness):
    client_b = profile_harness.client_for(USER_B_ID)
    # Tenta colidir com o username de User A em maiúsculas
    payload = {"username": "LEITOR_A"}
    res = client_b.put("/api/profile/me", json=payload)
    assert res.status_code == 409
    assert "indisponível" in res.json()["detail"].lower()


def test_update_my_profile_rejects_invalid_username_format(profile_harness):
    client = profile_harness.client_for(USER_A_ID)
    # Espaços e caracteres inválidos
    res = client.put("/api/profile/me", json={"username": "leitor invalido!"})
    assert res.status_code == 422


# ============================================================================
# Testes US2: Controles Granulares de Privacidade (T015)
# ============================================================================

def test_public_profile_hides_email_and_shows_data(profile_harness):
    client_b = profile_harness.client_for(USER_B_ID)
    res = client_b.get("/api/users/leitor_a")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["username"] == "leitor_a"
    assert data["display_name"] == "Leitor Alfa"
    assert "email" not in data
    assert data["is_private"] is False
    assert data["reading_stats"]["total_books"] == 1


def test_private_profile_displays_discrete_card(profile_harness):
    # User A torna o perfil privado
    client_a = profile_harness.client_for(USER_A_ID)
    client_a.put("/api/profile/me", json={"profile_visibility": "private", "bio": "Segredo"})

    # User B consulta o perfil público de User A
    client_b = profile_harness.client_for(USER_B_ID)
    res = client_b.get("/api/users/leitor_a")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["username"] == "leitor_a"
    assert data["is_private"] is True
    assert data["bio"] is None
    assert data["reading_stats"] is None
    assert "email" not in data


def test_owner_accessing_own_private_profile_sees_all(profile_harness):
    client_a = profile_harness.client_for(USER_A_ID)
    client_a.put("/api/profile/me", json={"profile_visibility": "private", "bio": "Minha bio"})

    # O próprio dono acessa /api/users/{username}
    res = client_a.get("/api/users/leitor_a")
    assert res.status_code == 200
    data = res.json()
    assert data["is_private"] is False
    assert data["bio"] == "Minha bio"


def test_unknown_username_returns_404(profile_harness):
    client = profile_harness.client_for(USER_A_ID)
    res = client.get("/api/users/usuario_inexistente_xyz")
    assert res.status_code == 404


# ============================================================================
# Testes US3: Processamento e Upload de Avatar (T020)
# ============================================================================

def _generate_synthetic_image(width: int = 500, height: int = 300, format: str = "PNG") -> bytes:
    img = Image.new("RGB", (width, height), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_upload_avatar_validates_and_resizes_square(profile_harness):
    client = profile_harness.client_for(USER_A_ID)
    img_data = _generate_synthetic_image(500, 300, "PNG")

    res = client.post(
        "/api/profile/avatar",
        files={"file": ("foto.png", img_data, "image/png")},
    )
    assert res.status_code == 200, res.text
    avatar_url = res.json()["avatar_url"]
    assert avatar_url.startswith("/api/avatars/avatar_")
    assert avatar_url.endswith(".webp")

    # Verifica arquivo salvo fisicamente
    filename = avatar_url.split("/")[-1]
    saved_path = profile_harness.avatars_dir / filename
    assert saved_path.exists()

    with Image.open(saved_path) as saved_img:
        assert saved_img.format == "WEBP"
        assert saved_img.size == (256, 256)


def test_get_avatar_serves_image(profile_harness):
    client = profile_harness.client_for(USER_A_ID)
    img_data = _generate_synthetic_image(200, 200, "JPEG")
    res = client.post(
        "/api/profile/avatar",
        files={"file": ("foto.jpg", img_data, "image/jpeg")},
    )
    avatar_url = res.json()["avatar_url"]

    # Consulta endpoint estático
    res_img = client.get(avatar_url)
    assert res_img.status_code == 200
    assert "image/webp" in res_img.headers["content-type"]


def test_upload_avatar_rejects_large_file(profile_harness):
    client = profile_harness.client_for(USER_A_ID)
    large_data = b"0" * (2 * 1024 * 1024 + 10)  # > 2MB
    res = client.post(
        "/api/profile/avatar",
        files={"file": ("grande.png", large_data, "image/png")},
    )
    assert res.status_code == 400
    assert "limite máximo" in res.json()["detail"].lower()


def test_delete_avatar_removes_file(profile_harness):
    client = profile_harness.client_for(USER_A_ID)
    img_data = _generate_synthetic_image(200, 200, "PNG")
    res = client.post(
        "/api/profile/avatar",
        files={"file": ("foto.png", img_data, "image/png")},
    )
    avatar_url = res.json()["avatar_url"]
    filename = avatar_url.split("/")[-1]
    saved_path = profile_harness.avatars_dir / filename
    assert saved_path.exists()

    # Deleta avatar
    del_res = client.delete("/api/profile/avatar")
    assert del_res.status_code == 200
    assert del_res.json()["avatar_url"] is None
    assert not saved_path.exists()


# ============================================================================
# Testes US4: Estatísticas e Busca de Leitores (T025)
# ============================================================================

def test_search_discoverable_users_respects_flags(profile_harness):
    client = profile_harness.client_for(USER_A_ID)

    # Inicialmente ambos devem ser descobríveis
    res = client.get("/api/users?q=leitor")
    assert res.status_code == 200
    items = res.json()
    usernames = [it["username"] for it in items]
    assert "leitor_a" in usernames
    assert "leitor_b" in usernames

    # User B define is_discoverable = False
    client_b = profile_harness.client_for(USER_B_ID)
    client_b.put("/api/profile/me", json={"is_discoverable": False})

    res2 = client.get("/api/users?q=leitor")
    usernames2 = [it["username"] for it in res2.json()]
    assert "leitor_a" in usernames2
    assert "leitor_b" not in usernames2


def test_reading_stats_hidden_when_disabled(profile_harness):
    client_a = profile_harness.client_for(USER_A_ID)
    client_a.put("/api/profile/me", json={"show_reading_stats": False})

    client_b = profile_harness.client_for(USER_B_ID)
    res = client_b.get("/api/users/leitor_a")
    assert res.status_code == 200
    data = res.json()
    assert data["reading_stats"] is None
