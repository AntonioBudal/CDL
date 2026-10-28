"""Ambiente comum dos testes da fatia 090-C: banco descartável com chaves estrangeiras, cofre e chave de teste.

Usuários, livros, capítulos e estudos são fictícios. O espaço livre do disco é simulado (``harness.free``).
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.core.config import GIB
from app.db.base import Base
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services import media_quota, media_service

OWNER = "11111111-1111-1111-1111-111111111111"
OTHER = "22222222-2222-2222-2222-222222222222"
ADMIN = "44444444-4444-4444-4444-444444444444"


def synthetic_photo(width: int = 4000, height: int = 3000, *, with_gps: bool = False, fmt: str = "JPEG") -> bytes:
    """Foto fictícia de página (12 MP por padrão), opcionalmente com EXIF e GPS falsos."""
    image = Image.new("RGB", (width, height), (235, 230, 215))
    for y in range(200, height - 200, 120):
        image.paste((60, 60, 70), (300, y, width - 300, y + 6))
    buffer = io.BytesIO()
    if with_gps:
        exif = Image.Exif()
        exif[0x010F] = "CameraDeTeste"
        exif.get_ifd(0x8825).update({1: "S", 2: (23.0, 33.0, 1.0), 3: "W", 4: (46.0, 38.0, 1.0)})
        image.save(buffer, format=fmt, exif=exif)
    else:
        image.save(buffer, format=fmt)
    return buffer.getvalue()


def small_webp(width: int = 1200, height: int = 900, color=(120, 60, 30)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color).save(buffer, format="WEBP")
    return buffer.getvalue()


class Harness:
    def __init__(self, app, factory, vault_dir: Path):
        self.app = app
        self.factory = factory
        self.vault_dir = vault_dir
        self.free = 500 * GIB

    def client(self, uid: str = OWNER) -> TestClient:
        client = TestClient(self.app)
        client.headers["X-User-Id"] = uid
        return client

    def study(self, uid: str = OWNER, *, title: str = "Estudo de Teste", status: str = "rascunho",
              trashed: bool = False) -> int:
        from app.db.types import utc_now

        with self.factory() as session:
            book = Book(user_id=uid, title="Livro de Teste", visibility="private")
            session.add(book)
            session.flush()
            chapter = Chapter(book_id=book.id, name="Capítulo 1")
            session.add(chapter)
            session.flush()
            study = Study(user_id=uid, chapter_id=chapter.id, title=title, reading_status=status,
                          summary="Resumo de teste", explanation="Explicação de teste", concepts="Conceito",
                          references="Referência", notes="Nota", source_response="Texto lido de teste")
            if trashed:
                study.deleted_at = utc_now()
            session.add(study)
            session.commit()
            return study.id

    def page(self, uid: str = OWNER, study_id: int | None = None, **fields) -> str:
        """Foto de página gravada direto no cofre, com campos de retenção ajustáveis."""
        with self.factory() as session:
            book_id = session.get(Study, study_id).book_id if study_id else None
            row = media_service.store(session, user_id=uid, kind="notebook_page", webp=small_webp(),
                                      study_id=study_id, book_id=book_id)
            for name, value in fields.items():
                setattr(row, name, value)
            session.commit()
            return row.id

    def snapshot(self, study_id: int) -> tuple:
        """Todas as colunas do estudo e todas as suas versões, para conferir que nada mudou (SC-005)."""
        with self.factory() as session:
            study = session.execute(text("SELECT * FROM studies WHERE id = :id"), {"id": study_id}).mappings().one()
            versions = session.execute(
                text("SELECT * FROM study_versions WHERE study_id = :id ORDER BY id"), {"id": study_id}
            ).mappings().all()
            return dict(study), [dict(v) for v in versions]


@pytest.fixture
def harness(tmp_path: Path, monkeypatch, isolated_media_vault):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    for name in ("LEITORUM_USER_STORAGE_QUOTA_BYTES", "LEITORUM_GLOBAL_STORAGE_QUOTA_BYTES",
                 "LEITORUM_STORAGE_FREE_MARGIN_BYTES", "LEITORUM_MEDIA_RETENTION_DAYS",
                 "LEITORUM_MEDIA_COMPLETED_GRACE_DAYS", "LEITORUM_MEDIA_DELETE_ON_COMPLETED"):
        monkeypatch.delenv(name, raising=False)
    engine = create_sqlite_engine(tmp_path / "fatia-c.db")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    with factory() as session:
        for uid, name, role in ((OWNER, "dono_teste", "user"), (OTHER, "outro_teste", "user"),
                                (ADMIN, "admin_teste", "admin")):
            session.add(User(id=uid, username=name, display_name=name, role=role, status="ativo"))
            session.add(UserProfile(user_id=uid, username=name, display_name=name))
        session.commit()

    def override():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_session] = override
    built = Harness(app, factory, isolated_media_vault)
    monkeypatch.setattr(media_quota, "disk_free", lambda _path: built.free)
    yield built
    engine.dispose()
