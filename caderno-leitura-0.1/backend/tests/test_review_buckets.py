"""F0.10.04 — baldes da revisão (novos, difícil, médio, fácil) derivados de last_rating, sem migração."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
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
from app.models.study_highlight import StudyHighlight
from app.models.user import User

# (livro, tipo, última avaliação): 2 novos, 3 difíceis, 1 médio, 2 fáceis; o livro 2 só tem 1 difícil e 1 novo.
SEED = [
    (1, "question", None),
    (1, "hidden", "hard"),
    (1, "question", "hard"),
    (1, "question", "medium"),
    (1, "hidden", "easy"),
    (1, "question", "easy"),
    (2, "question", None),
    (2, "hidden", "hard"),
]


@pytest.fixture
def env(tmp_path, monkeypatch) -> Generator[tuple[TestClient, dict], None, None]:
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    engine = create_engine(f"sqlite:///{(tmp_path / 'baldes.db').as_posix()}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    local = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
    ids: dict = {}
    with local() as session:
        session.add(User(id=DEFAULT_OWNER_ID, username=DEFAULT_OWNER_USERNAME, display_name="Dona Fictícia", role="admin", status="ativo"))
        studies = {}
        for n in (1, 2):
            book = Book(user_id=DEFAULT_OWNER_ID, title=f"Livro de Teste {n}")
            session.add(book)
            session.flush()
            chapter = Chapter(book_id=book.id, name="Capítulo 1", position=0)
            session.add(chapter)
            session.flush()
            study = Study(user_id=DEFAULT_OWNER_ID, chapter_id=chapter.id, title=f"Estudo {n}", summary="Resumo fictício.")
            session.add(study)
            session.flush()
            studies[n] = study.id
            ids[f"book{n}"] = book.id
        old = datetime.now(UTC) - timedelta(days=3)
        for i, (n, kind, rating) in enumerate(SEED):
            session.add(StudyHighlight(
                study_id=studies[n], user_id=DEFAULT_OWNER_ID, section="summary", selected_text=f"trecho {i}",
                kind=kind, last_rating=rating, last_reviewed_at=old if rating else None, review_count=1 if rating else 0,
            ))
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
        yield client, ids


def test_stats_report_bucket_counts(env):
    client, _ = env
    data = client.get("/api/review/stats").json()
    assert data["buckets"] == {"new": 2, "hard": 3, "medium": 1, "easy": 2}
    assert data["total_eligible"] == 8


def test_bucket_counts_follow_filters_but_headline_stays_global(env):
    client, ids = env
    by_book = client.get("/api/review/stats", params={"book_id": ids["book2"]}).json()
    assert by_book["buckets"] == {"new": 1, "hard": 1, "medium": 0, "easy": 0}
    assert by_book["total_eligible"] == 8
    by_kind = client.get("/api/review/stats", params={"kind": "hidden"}).json()
    assert by_kind["buckets"] == {"new": 0, "hard": 2, "medium": 0, "easy": 1}


@pytest.mark.parametrize(("bucket", "expected"), [("new", {None}), ("hard", {"hard"}), ("medium", {"medium"}), ("easy", {"easy"})])
def test_items_filtered_by_bucket(env, bucket, expected):
    client, _ = env
    items = client.get("/api/review/items", params={"bucket": bucket, "limit": 50}).json()
    assert items and {item["last_rating"] for item in items} == expected


def test_bucket_combines_with_book_and_limit(env):
    client, ids = env
    items = client.get("/api/review/items", params={"bucket": "hard", "book_id": ids["book1"], "limit": 1}).json()
    assert len(items) == 1 and items[0]["last_rating"] == "hard" and items[0]["book_id"] == ids["book1"]


def test_invalid_bucket_is_rejected(env):
    client, _ = env
    assert client.get("/api/review/items", params={"bucket": "urgente"}).status_code == 422


def test_items_without_bucket_keep_current_order(env):
    client, _ = env
    items = client.get("/api/review/items", params={"limit": 50}).json()
    ratings = [item["last_rating"] for item in items]
    assert ratings[:2] == [None, None], "nunca avaliados continuam primeiro"
    assert ratings[2:5] == ["hard", "hard", "hard"], "depois os difíceis"
