"""F0.10.02.5 — mudar um estudo de capítulo: subestudos acompanham e as posições ficam contíguas nos dois lados."""
from __future__ import annotations

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
def env(tmp_path, monkeypatch) -> Generator[tuple[TestClient, sessionmaker], None, None]:
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    engine = create_engine(f"sqlite:///{(tmp_path / 'mudar.db').as_posix()}", connect_args={"check_same_thread": False})
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


def _book(local, owner: str = DEFAULT_OWNER_ID, chapters: int = 2) -> tuple[int, list[int]]:
    with local() as session:
        book = Book(user_id=owner, title="Livro de Teste")
        session.add(book)
        session.flush()
        ids = []
        for position in range(chapters):
            chapter = Chapter(book_id=book.id, name=f"Capítulo {position + 1}", position=position)
            session.add(chapter)
            session.flush()
            ids.append(chapter.id)
        session.commit()
        return book.id, ids


def _study(local, chapter_id: int, title: str, position: int = 0, parent: int | None = None, owner: str = DEFAULT_OWNER_ID) -> int:
    with local() as session:
        study = Study(user_id=owner, chapter_id=chapter_id, title=title, summary="Resumo fictício.", position=position, parent_study_id=parent)
        session.add(study)
        session.commit()
        return study.id


def _rows(local, chapter_id: int) -> list[tuple[str, int | None, int]]:
    with local() as session:
        studies = session.query(Study).filter(Study.chapter_id == chapter_id).order_by(Study.parent_study_id.is_(None).desc(), Study.position).all()
        return [(s.title, s.parent_study_id, s.position) for s in studies]


def test_moves_study_with_its_substudies_and_renumbers(env):
    client, local = env
    _, (c1, c2) = _book(local)
    first = _study(local, c1, "Estudo A", 0)
    moving = _study(local, c1, "Estudo B", 1)
    child = _study(local, c1, "Subestudo de B", 0, parent=moving)
    _study(local, c1, "Estudo C", 2)
    _study(local, c2, "Estudo D", 0)

    response = client.post(f"/api/studies/{moving}/chapter", json={"chapter_id": c2})

    assert response.status_code == 200
    body = response.json()
    assert body["chapter_id"] == c2 and body["parent_study_id"] is None and body["position"] == 1
    assert _rows(local, c1) == [("Estudo A", None, 0), ("Estudo C", None, 1)]
    assert ("Subestudo de B", moving, 0) in _rows(local, c2)
    assert ("Estudo D", None, 0) in _rows(local, c2)
    with local() as session:
        assert session.get(Study, child).chapter_id == c2
        assert session.get(Study, first).chapter_id == c1


def test_substudy_becomes_root_in_the_new_chapter(env):
    client, local = env
    _, (c1, c2) = _book(local)
    parent = _study(local, c1, "Estudo A", 0)
    child = _study(local, c1, "Subestudo", 0, parent=parent)

    response = client.post(f"/api/studies/{child}/chapter", json={"chapter_id": c2})

    assert response.status_code == 200
    assert _rows(local, c2) == [("Subestudo", None, 0)]
    assert _rows(local, c1) == [("Estudo A", None, 0)]


def test_same_chapter_is_a_no_op(env):
    client, local = env
    _, (c1, _) = _book(local)
    study = _study(local, c1, "Estudo A", 0)
    response = client.post(f"/api/studies/{study}/chapter", json={"chapter_id": c1})
    assert response.status_code == 200
    assert _rows(local, c1) == [("Estudo A", None, 0)]


def test_chapter_of_another_book_is_rejected(env):
    client, local = env
    _, (c1, _) = _book(local)
    _, (other,) = _book(local, chapters=1)
    study = _study(local, c1, "Estudo A", 0)
    response = client.post(f"/api/studies/{study}/chapter", json={"chapter_id": other})
    assert response.status_code == 400
    assert _rows(local, c1) == [("Estudo A", None, 0)]


def test_chapter_of_someone_elses_book_is_not_found(env):
    client, local = env
    _, (c1, _) = _book(local)
    _, (foreign,) = _book(local, owner="outra-pessoa", chapters=1)
    study = _study(local, c1, "Estudo A", 0)
    assert client.post(f"/api/studies/{study}/chapter", json={"chapter_id": foreign}).status_code == 404


def test_stale_version_is_rejected(env):
    client, local = env
    _, (c1, c2) = _book(local)
    study = _study(local, c1, "Estudo A", 0)
    response = client.post(f"/api/studies/{study}/chapter", json={"chapter_id": c2, "expected_version": 99})
    assert response.status_code == 409
    assert _rows(local, c1) == [("Estudo A", None, 0)]
