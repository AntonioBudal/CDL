"""Feature 090-B (B018): rotas de imagens cifradas, regra de acesso e erros do cofre. Só dados sintéticos."""

from __future__ import annotations

import io
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.book import Book
from app.models.encrypted_media import EncryptedMedia
from app.models.friendship import Friendship
from app.models.storage_settings import StorageSettings
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services import media_service
from app.services.vault import MAGIC, media_path, thumb_path

OWNER = "11111111-1111-1111-1111-111111111111"
READER = "22222222-2222-2222-2222-222222222222"
BLOCKED = "33333333-3333-3333-3333-333333333333"
PLAIN_SIGNATURES = (b"RIFF", b"WEBP", b"\xff\xd8\xff", b"\x89PNG", b"JFIF", b"Exif", b"CameraDeTeste")


def synthetic_jpeg(width: int = 600, height: int = 400, *, with_exif: bool = False) -> bytes:
    image = Image.new("RGB", (width, height), (40, 90, 140))
    buffer = io.BytesIO()
    if with_exif:
        exif = Image.Exif()
        exif[0x010F] = "CameraDeTeste"  # Make
        exif[0x0110] = "ModeloDeTeste"  # Model
        exif.get_ifd(0x8825).update({1: "S", 2: (23.0, 33.0, 1.0), 3: "W", 4: (46.0, 38.0, 1.0)})  # GPS
        image.save(buffer, format="JPEG", exif=exif)
    else:
        image.save(buffer, format="JPEG")
    return buffer.getvalue()


def synthetic_webp(width: int = 1200, height: int = 900) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (120, 60, 30)).save(buffer, format="WEBP")
    return buffer.getvalue()


@pytest.fixture
def harness(tmp_path: Path, monkeypatch, isolated_media_vault):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("CADERNO_AVATARS_DIR", str(tmp_path / "avatars"))
    monkeypatch.setenv("CADERNO_COVERS_DIR", str(tmp_path / "covers"))
    (tmp_path / "avatars").mkdir()
    (tmp_path / "covers").mkdir()

    engine = create_engine(f"sqlite:///{(tmp_path / 'media.db').as_posix()}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    with factory() as session:
        for uid, name in ((OWNER, "dono_teste"), (READER, "leitor_teste"), (BLOCKED, "bloqueado_teste")):
            session.add(User(id=uid, username=name, display_name=name, role="user", status="ativo"))
            session.add(UserProfile(user_id=uid, username=name, display_name=name))
        a, b = Friendship.normalize_pair(OWNER, BLOCKED)
        session.add(Friendship(user_id_a=a, user_id_b=b, status="blocked", action_user_id=OWNER))
        session.commit()

    def override():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_session] = override

    class Harness:
        vault_dir = isolated_media_vault
        avatars_dir = tmp_path / "avatars"
        covers_dir = tmp_path / "covers"
        session_factory = factory
        anon = TestClient(app)

        def as_user(self, uid: str) -> TestClient:
            client = TestClient(app)
            client.headers["X-User-Id"] = uid
            return client

        def book(self, title: str, visibility: str) -> int:
            with factory() as session:
                book = Book(user_id=OWNER, title=title, visibility=visibility)
                session.add(book)
                session.commit()
                return book.id

        def page(self, uid: str = OWNER) -> str:
            with factory() as session:
                row = media_service.store(session, user_id=uid, kind="notebook_page", webp=synthetic_webp())
                session.commit()
                return row.id

    yield Harness()
    engine.dispose()


def upload_cover(harness, book_id: int) -> str:
    res = harness.as_user(OWNER).post(
        f"/api/books/{book_id}/cover", files={"file": ("capa.jpg", synthetic_jpeg(with_exif=True), "image/jpeg")}
    )
    assert res.status_code == 200, res.text
    return res.json()["cover_image"]


def upload_avatar(harness, uid: str = OWNER) -> str:
    res = harness.as_user(uid).post(
        "/api/profile/avatar", files={"file": ("foto.jpg", synthetic_jpeg(with_exif=True), "image/jpeg")}
    )
    assert res.status_code == 200, res.text
    return res.json()["avatar_url"]


def assert_private_image(res) -> Image.Image:
    assert res.status_code == 200, res.text
    assert res.headers["content-type"] == "image/webp"
    assert "no-store" in res.headers["cache-control"] and "private" in res.headers["cache-control"]
    assert res.headers["x-content-type-options"] == "nosniff"
    image = Image.open(io.BytesIO(res.content))
    image.load()
    assert not image.info.get("exif") and not image.info.get("xmp") and not image.info.get("icc_profile")
    assert b"CameraDeTeste" not in res.content and b"Exif" not in res.content
    return image


# --- disco: só cifrado, sem metadados -----------------------------------------------------------


def test_uploads_leave_only_ciphertext_on_disk(harness):
    cover_id = upload_cover(harness, harness.book("Livro de Teste", "public"))
    avatar_id = upload_avatar(harness).rsplit("/", 1)[-1]
    page_id = harness.page()

    files = sorted(harness.vault_dir.rglob("*"))
    encs = [p for p in files if p.is_file()]
    assert {p.name for p in encs} == {f"{i}{suffix}" for i in (cover_id, avatar_id, page_id)
                                      for suffix in (".enc", ".thumb.enc")}
    for enc in encs:
        blob = enc.read_bytes()
        assert blob.startswith(MAGIC) and enc.suffix == ".enc"
        assert not any(signature in blob for signature in PLAIN_SIGNATURES)
    assert list(harness.avatars_dir.iterdir()) == [] and list(harness.covers_dir.iterdir()) == []


def test_served_images_have_no_exif_or_gps(harness):
    cover_id = upload_cover(harness, harness.book("Livro de Teste", "public"))
    avatar_url = upload_avatar(harness)
    owner = harness.as_user(OWNER)
    assert_private_image(owner.get(f"/api/covers/{cover_id}"))
    assert_private_image(owner.get(avatar_url))


# --- matriz de acesso ---------------------------------------------------------------------------


def test_avatar_access_matrix(harness):
    url = upload_avatar(harness)
    media_id = url.rsplit("/", 1)[-1]

    assert_private_image(harness.as_user(OWNER).get(url))
    assert_private_image(harness.as_user(READER).get(url))
    assert harness.as_user(BLOCKED).get(url).status_code == 404
    assert harness.anon.get(url).status_code == 401
    assert harness.as_user(READER).get(f"/api/media/{media_id}/content").status_code == 200
    assert harness.as_user(BLOCKED).get(f"/api/media/{media_id}/content").status_code == 404


def test_cover_follows_book_visibility(harness):
    public_cover = upload_cover(harness, harness.book("Livro Público de Teste", "public"))
    private_cover = upload_cover(harness, harness.book("Livro Privado de Teste", "private"))
    friends_cover = upload_cover(harness, harness.book("Livro de Amigos de Teste", "friends"))
    owner, reader, blocked = harness.as_user(OWNER), harness.as_user(READER), harness.as_user(BLOCKED)

    for cover in (public_cover, private_cover, friends_cover):
        assert_private_image(owner.get(f"/api/covers/{cover}"))
    assert_private_image(reader.get(f"/api/covers/{public_cover}"))
    assert reader.get(f"/api/covers/{private_cover}").status_code == 404
    assert reader.get(f"/api/covers/{friends_cover}").status_code == 404  # sem amizade aceita
    assert blocked.get(f"/api/covers/{public_cover}").status_code == 404
    assert harness.anon.get(f"/api/covers/{public_cover}").status_code == 401
    assert reader.get(f"/api/media/{private_cover}/thumbnail").status_code == 404


def test_cover_of_trashed_book_is_hidden_from_others(harness):
    book_id = harness.book("Livro Público de Teste", "public")
    cover = upload_cover(harness, book_id)
    assert harness.as_user(OWNER).post(f"/api/books/{book_id}/trash").status_code == 200
    assert harness.as_user(READER).get(f"/api/covers/{cover}").status_code == 404
    assert harness.as_user(OWNER).get(f"/api/covers/{cover}").status_code == 200


def test_notebook_page_is_owner_only_and_thumbnail_is_small(harness):
    page = harness.page()
    owner = harness.as_user(OWNER)

    full = assert_private_image(owner.get(f"/api/media/{page}/content"))
    assert full.size == (1200, 900)
    thumb = assert_private_image(owner.get(f"/api/media/{page}/thumbnail"))
    assert max(thumb.size) <= 320
    for uid in (READER, BLOCKED):
        assert harness.as_user(uid).get(f"/api/media/{page}/content").status_code == 404
    assert harness.anon.get(f"/api/media/{page}/content").status_code == 401
    # a rota de avatar não serve página de caderno
    assert owner.get(f"/api/avatars/{page}").status_code == 404
    assert owner.get(f"/api/covers/{page}").status_code == 404


def test_unknown_or_malformed_ids_answer_404(harness):
    owner = harness.as_user(OWNER)
    assert owner.get(f"/api/media/{uuid.uuid4()}/content").status_code == 404
    assert owner.get("/api/media/nao-e-uuid/content").status_code == 404
    assert owner.get(f"/api/avatars/{uuid.uuid4()}").status_code == 404


# --- listagem e exclusão ------------------------------------------------------------------------


def test_list_shows_only_own_items_with_pagination(harness):
    mine = {harness.page() for _ in range(3)}
    harness.page(READER)
    owner = harness.as_user(OWNER)

    first = owner.get("/api/media", params={"limit": 2})
    assert first.status_code == 200 and first.headers["cache-control"] == "no-store"
    body = first.json()
    assert len(body["items"]) == 2 and body["next_offset"] == 2
    rest = owner.get("/api/media", params={"limit": 2, "offset": 2}).json()
    assert rest["next_offset"] is None
    assert {item["id"] for item in body["items"] + rest["items"]} == mine
    assert owner.get("/api/media", params={"kind": "avatar"}).json()["items"] == []


def test_delete_cover_keeps_book_and_frees_bytes(harness):
    book_id = harness.book("Livro de Teste", "public")
    cover = upload_cover(harness, book_id)
    path = media_path(harness.vault_dir, uuid.UUID(cover))
    owner = harness.as_user(OWNER)

    assert harness.as_user(READER).delete(f"/api/media/{cover}").status_code == 404
    res = owner.delete(f"/api/media/{cover}")
    assert res.status_code == 200 and res.json()["freed_bytes"] > 0
    assert not path.exists()
    book = owner.get(f"/api/books/{book_id}")
    assert book.status_code == 200 and book.json()["cover_image"] is None
    with harness.session_factory() as session:
        assert session.get(EncryptedMedia, cover) is None


def test_delete_avatar_media_clears_profile(harness):
    media_id = upload_avatar(harness).rsplit("/", 1)[-1]
    owner = harness.as_user(OWNER)
    assert owner.delete(f"/api/media/{media_id}").status_code == 200
    with harness.session_factory() as session:
        assert session.get(UserProfile, OWNER).avatar_url is None
    assert owner.get(f"/api/avatars/{media_id}").status_code == 404


def test_replacing_avatar_discards_old_media(harness):
    first = upload_avatar(harness).rsplit("/", 1)[-1]
    second = upload_avatar(harness).rsplit("/", 1)[-1]
    assert first != second
    assert not media_path(harness.vault_dir, uuid.UUID(first)).exists()
    assert not thumb_path(harness.vault_dir, uuid.UUID(first)).exists()
    assert media_path(harness.vault_dir, uuid.UUID(second)).exists()


# --- cofre trancado, arquivo ausente, arquivo adulterado ----------------------------------------


def test_locked_vault_answers_503_without_leaking(harness, monkeypatch):
    page = harness.page()
    monkeypatch.delenv("LEITORUM_MEDIA_MASTER_KEY")
    monkeypatch.setenv("LEITORUM_MEDIA_KEY_FILE", str(harness.vault_dir.parent / "sem-chave.key"))
    media_service.reset_cache()

    res = harness.as_user(OWNER).get(f"/api/media/{page}/content")
    assert res.status_code == 503 and res.json()["code"] == "vault_locked"
    upload = harness.as_user(OWNER).post(
        "/api/profile/avatar", files={"file": ("foto.jpg", synthetic_jpeg(), "image/jpeg")}
    )
    assert upload.status_code == 503 and upload.json()["code"] == "vault_locked"
    assert list(harness.avatars_dir.iterdir()) == []


def test_other_key_than_registered_locks_the_vault(harness, monkeypatch):
    page = harness.page()
    with harness.session_factory() as session:
        session.get(StorageSettings, 1).media_key_fingerprint = "0" * 16
        session.commit()
    media_service.reset_cache()
    res = harness.as_user(OWNER).get(f"/api/media/{page}/content")
    assert res.status_code == 503 and res.json()["code"] == "vault_locked"
    assert "não é a deste acervo" in res.json()["detail"]


def test_missing_file_answers_409_and_tampered_file_422(harness):
    missing, tampered = harness.page(), harness.page()
    media_path(harness.vault_dir, uuid.UUID(missing)).unlink()
    path = media_path(harness.vault_dir, uuid.UUID(tampered))
    blob = bytearray(path.read_bytes())
    blob[-5] ^= 0xFF
    path.write_bytes(bytes(blob))
    owner = harness.as_user(OWNER)

    res = owner.get(f"/api/media/{missing}/content")
    assert res.status_code == 409 and res.json()["code"] == "missing"
    res = owner.get(f"/api/media/{tampered}/content")
    assert res.status_code == 422 and res.json()["code"] == "integrity_failed"
    assert owner.get(f"/api/media/{missing}/thumbnail").status_code == 409


def test_thumbnail_is_stored_encrypted_and_regenerated_if_lost(harness):
    page = harness.page()
    owner = harness.as_user(OWNER)
    stored = thumb_path(harness.vault_dir, uuid.UUID(page))
    assert stored.read_bytes().startswith(MAGIC)
    assert_private_image(owner.get(f"/api/media/{page}/thumbnail"))

    stored.unlink()
    regenerated = assert_private_image(owner.get(f"/api/media/{page}/thumbnail"))
    assert max(regenerated.size) <= 320

    # trocar a miniatura pelo arquivo principal não passa na autenticação
    stored.write_bytes(media_path(harness.vault_dir, uuid.UUID(page)).read_bytes())
    assert owner.get(f"/api/media/{page}/thumbnail").status_code == 422


# --- rotas legadas (arquivos em claro ainda não importados) -------------------------------------


def test_legacy_avatar_requires_session_and_respects_block(harness):
    name = "avatar_legado_teste.webp"
    (harness.avatars_dir / name).write_bytes(synthetic_webp(64, 64))
    with harness.session_factory() as session:
        session.get(UserProfile, OWNER).avatar_url = f"/api/avatars/{name}"
        session.commit()

    assert harness.anon.get(f"/api/avatars/{name}").status_code == 401
    assert_private_image(harness.as_user(READER).get(f"/api/avatars/{name}"))
    assert harness.as_user(BLOCKED).get(f"/api/avatars/{name}").status_code == 404
    assert harness.as_user(READER).get("/api/avatars/sem_dono.webp").status_code == 404


def test_legacy_cover_requires_permission_on_the_book(harness):
    name = "capa_legada_teste.webp"
    (harness.covers_dir / name).write_bytes(synthetic_webp(80, 120))
    book_id = harness.book("Livro Privado de Teste", "private")
    with harness.session_factory() as session:
        session.get(Book, book_id).cover_image = name
        session.commit()

    assert harness.anon.get(f"/api/covers/{name}").status_code == 401
    assert harness.as_user(OWNER).get(f"/api/covers/{name}").status_code == 200
    assert harness.as_user(READER).get(f"/api/covers/{name}").status_code == 404
