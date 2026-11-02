"""F0.10.02.5 — exclusão de capítulo: só vazio, renumera as posições e nunca apaga estudos junto."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.user import User


@pytest.fixture
def chapters_env(tmp_path, monkeypatch) -> Generator[tuple[TestClient, sessionmaker], None, None]:
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    engine = create_engine(f"sqlite:///{(tmp_path / 'capitulos.db').as_posix()}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    local = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
    with local() as session:
        session.add(User(id=DEFAULT_OWNER_ID, username=DEFAULT_OWNER_USERNAME, display_name="Dona Fictícia", role="admin", status="ativo"))
        session.add(User(id="outra-pessoa", username="outra_pessoa", display_name="Outra Pessoa", role="user", status="ativo"))
        session.commit()

    application = create_app()

    def override_get_session():
        session = local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    application.dependency_overrides[get_session] = override_get_session
    with TestClient(application) as client:
        yield client, local


def _book_with_chapters(local, names: list[str], owner: str = DEFAULT_OWNER_ID) -> tuple[int, list[int]]:
    with local() as session:
        book = Book(user_id=owner, title="Livro de Teste")
        session.add(book)
        session.flush()
        ids = []
        for position, name in enumerate(names):
            chapter = Chapter(book_id=book.id, name=name, position=position)
            session.add(chapter)
            session.flush()
            ids.append(chapter.id)
        session.commit()
        return book.id, ids


def _add_study(local, chapter_id: int, *, trashed: bool = False) -> None:
    with local() as session:
        study = Study(user_id=DEFAULT_OWNER_ID, chapter_id=chapter_id, title="Estudo de Teste", summary="Resumo fictício.")
        if trashed:
            study.deleted_at = datetime.now(UTC)
        session.add(study)
        session.commit()


def test_delete_empty_chapter_renumbers_the_rest(chapters_env):
    client, local = chapters_env
    book_id, (c1, c2, c3) = _book_with_chapters(local, ["Capítulo 1", "Capítulo 2", "Capítulo 3"])

    response = client.delete(f"/api/books/{book_id}/chapters/{c2}")

    assert response.status_code == 200
    assert [(c["id"], c["position"]) for c in response.json()] == [(c1, 0), (c3, 1)]
    listed = client.get(f"/api/books/{book_id}/chapters").json()
    assert [c["name"] for c in listed] == ["Capítulo 1", "Capítulo 3"]


@pytest.mark.parametrize("trashed", [False, True])
def test_chapter_with_studies_is_not_deleted(chapters_env, trashed):
    client, local = chapters_env
    book_id, (c1,) = _book_with_chapters(local, ["Capítulo 1"])
    _add_study(local, c1, trashed=trashed)

    response = client.delete(f"/api/books/{book_id}/chapters/{c1}")

    assert response.status_code == 409
    assert "estudo" in response.json()["detail"]
    assert len(client.get(f"/api/books/{book_id}/chapters").json()) == 1
    with local() as session:
        assert session.query(Study).count() == 1


def test_cannot_delete_chapter_of_someone_elses_book(chapters_env):
    client, local = chapters_env
    book_id, (c1,) = _book_with_chapters(local, ["Capítulo 1"], owner="outra-pessoa")
    assert client.delete(f"/api/books/{book_id}/chapters/{c1}").status_code == 404
    with local() as session:
        assert session.get(Chapter, c1) is not None


def test_delete_unknown_chapter_returns_404(chapters_env):
    client, local = chapters_env
    book_id, _ = _book_with_chapters(local, ["Capítulo 1"])
    assert client.delete(f"/api/books/{book_id}/chapters/999999").status_code == 404
