"""Ambiente comum dos testes da fatia 091-B: banco descartável com chaves estrangeiras, usuários e estudos fictícios."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.organizer_feedback import OrganizerFeedback
from app.models.study import Study
from app.models.user import User
from app.models.user_profile import UserProfile

OWNER = "11111111-1111-1111-1111-111111111111"
OTHER = "22222222-2222-2222-2222-222222222222"

# Página fictícia lida pela máquina (com erros de leitura) e o que o leitor salvou depois de organizar.
READ = (
    "O capitulo trata da leitura atíva.\n"
    "Leitura ativa: ler fazendo perguntas.\n"
    "Isso irnporta porque fixa as ideias.\n"
    "- A margem e o centro — Lúcia Dantas"
)
TEXT = (
    "O capítulo trata da leitura ativa.\n"
    "Leitura ativa: ler fazendo perguntas.\n"
    "Isso importa porque fixa as ideias.\n"
    "- A margem e o centro — Lúcia Dantas"
)
SAVED = {
    "summary": "O capítulo trata da leitura ativa.",
    "explanation": "Isso importa porque fixa as ideias.",
    "concepts": "Leitura ativa: ler fazendo perguntas.",
    "references": "- A margem e o centro — Lúcia Dantas",
}
ENGINE = {"version": "2", "sha256": "9f6530a32726d593142b7a2de3bce3efc1c0095abf3a91335364db6343978aee", "adapter": None}


def suggestion(sections=("summary", "explanation", "explanation", "references"), outcome="saved", text=TEXT) -> dict:
    segments, pos = [], 0
    for k, (line, section) in enumerate(zip(text.split("\n"), sections, strict=False)):
        segments.append({"index": k, "start": pos, "end": pos + len(line), "section": section, "confidence": 0.8,
                         "review": False})
        pos += len(line) + 1
    return {"engine": ENGINE, "outcome": outcome, "text": text, "segments": segments}


class Harness:
    def __init__(self, app, factory):
        self.app = app
        self.factory = factory

    def client(self, uid: str = OWNER) -> TestClient:
        client = TestClient(self.app)
        client.headers["X-User-Id"] = uid
        return client

    def study(self, uid: str = OWNER, *, source: str = READ, sections: dict | None = None) -> int:
        with self.factory() as session:
            book = Book(user_id=uid, title="Livro de Teste", visibility="private")
            session.add(book)
            session.flush()
            chapter = Chapter(book_id=book.id, name="Capítulo 1")
            session.add(chapter)
            session.flush()
            study = Study(user_id=uid, chapter_id=chapter.id, title="Estudo de Teste", source_response=source,
                          **(sections or SAVED))
            session.add(study)
            session.commit()
            return study.id

    def send(self, study_id: int, body: dict, uid: str = OWNER):
        return self.client(uid).post(f"/api/studies/{study_id}/organizer-feedback", json=body)

    def records(self) -> list[OrganizerFeedback]:
        with self.factory() as session:
            return session.query(OrganizerFeedback).order_by(OrganizerFeedback.id).all()

    def document(self, study_id: int) -> dict:
        with self.factory() as session:
            row = session.query(OrganizerFeedback).filter_by(study_id=study_id).one()
            return json.loads(row.payload)


@pytest.fixture
def harness(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    engine = create_sqlite_engine(tmp_path / "fatia-091b.db")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    with factory() as session:
        for uid, name in ((OWNER, "dono_teste"), (OTHER, "outro_teste")):
            session.add(User(id=uid, username=name, display_name=name, role="user", status="ativo"))
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
    yield Harness(app, factory)
    engine.dispose()
