import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import UTC, datetime, timedelta, timezone

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, get_database_path
from app.db import session as database_session
from app.db.session import create_sqlite_engine
from app.models import Book, Chapter, Study


@pytest.fixture
def database(tmp_path):
    # Inclui espacos, acento e percentual para verificar o caminho SQLite.
    path = tmp_path / "acervo ação 100%" / "teste.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    try:
        yield engine, config, path
    finally:
        engine.dispose()


def make_study() -> Study:
    book = Book(title="Livro de teste — reflexão", author="Autor de teste")
    chapter = Chapter(book=book, name="Capítulo 1", position=1)
    return Study(
        chapter=chapter,
        title="Estudo de teste",
        location="p. 32–34 / Loc. 1820",
        source_response="## Resumo\nUma reflexão.\n\n## Explicação\nTexto original.",
        summary="Uma reflexão.",
        explanation="Explicação em duas linhas.\nSegunda linha.",
        concepts="Conceito: atenção.",
        references="Nenhuma referência externa verificada.",
        notes="Minha interpretação é diferente.\nQuero revisar amanhã.",
    )


def test_persistence_in_new_process_and_repeated_upgrade(database, tmp_path):
    engine, config, path = database
    study = make_study()
    with Session(engine, expire_on_commit=False) as session:
        session.add(study)
        session.commit()
        study_id = study.id
        expected = {field: getattr(study, field) for field in (
            "title", "location", "source_response", "summary", "explanation",
            "concepts", "references", "notes",
        )}
    engine.dispose()

    # Reaplicar head nao deve recriar tabelas nem apagar os registros.
    command.upgrade(config, "head")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(BACKEND_DIR)
    environment["CADERNO_DATABASE_PATH"] = str(path)
    script = """
import json, sys
from sqlalchemy.orm import Session
from app.db.session import get_engine
from app.models import Study
engine = get_engine()
with Session(engine) as session:
    study = session.get(Study, int(sys.argv[1]))
    fields = ('title', 'location', 'source_response', 'summary', 'explanation', 'concepts', 'references', 'notes')
    result = {field: getattr(study, field) for field in fields}
    result['book'] = study.chapter.book.title
    result['chapter'] = study.chapter.name
    print(json.dumps(result))
engine.dispose()
"""
    completed = subprocess.run(
        [sys.executable, "-c", script, str(study_id)],
        cwd=tmp_path, env=environment, check=True, capture_output=True, text=True, encoding="utf-8",
    )
    saved = json.loads(completed.stdout)
    assert saved.pop("book") == "Livro de teste — reflexão"
    assert saved.pop("chapter") == "Capítulo 1"
    assert saved == expected


def test_foreign_keys_on_each_connection_and_orphans_rejected(database):
    engine, _, _ = database
    with engine.connect() as first, engine.connect() as second:
        assert first.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
        assert second.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1

    invalid_records = (
        Chapter(book_id=987654, name="Sem livro"),
        Study(chapter_id=987654, title="Sem capítulo", summary="Texto"),
    )
    for record in invalid_records:
        with Session(engine) as session:
            session.add(record)
            with pytest.raises(IntegrityError):
                session.commit()


def test_failed_transaction_rolls_back_the_entire_write(database):
    engine, _, _ = database
    with Session(engine) as session:
        session.add(Book(title="Este livro também deve ser revertido"))
        session.flush()
        session.add(Chapter(book_id=987654, name="Vínculo inválido"))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    with Session(engine) as reopened:
        assert reopened.scalar(select(func.count()).select_from(Book)) == 0


def test_parent_delete_does_not_remove_related_studies(database):
    engine, _, _ = database
    with Session(engine) as session:
        study = make_study()
        session.add(study)
        session.commit()
        book = study.chapter.book
        assert len(book.chapters) == 1
        session.delete(book)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        assert session.scalar(select(func.count()).select_from(Study)) == 1


def test_migration_matches_models(database):
    _, config, _ = database
    command.check(config)


def test_edit_preserves_source_and_notes_and_reads_utc_dates(database):
    engine, _, _ = database
    original_time = (datetime.now(UTC) - timedelta(days=1)).astimezone(timezone(timedelta(hours=-3)))
    with Session(engine, expire_on_commit=False) as session:
        study = make_study()
        study.created_at = original_time
        study.updated_at = original_time
        original_source = study.source_response
        original_notes = study.notes
        session.add(study)
        session.commit()
        study_id = study.id
    with Session(engine) as session:
        study = session.get(Study, study_id)
        assert study.created_at == original_time.astimezone(UTC)
        assert study.created_at.tzinfo is UTC
        study.explanation = "Explicação corrigida."
        session.commit()
    with Session(engine) as reopened:
        saved = reopened.get(Study, study_id)
        assert saved.explanation == "Explicação corrigida."
        assert saved.source_response == original_source
        assert saved.notes == original_notes
        assert saved.created_at == original_time.astimezone(UTC)
        assert saved.updated_at.tzinfo is UTC
        assert saved.updated_at > saved.created_at


def test_request_sessions_are_distinct_and_close_rolls_back(database, monkeypatch):
    engine, _, _ = database
    monkeypatch.setattr(database_session, "get_engine", lambda: engine)
    first = database_session.get_session()
    second = database_session.get_session()
    try:
        first_session = next(first)
        second_session = next(second)
        assert first_session is not second_session
        first_session.add(Book(title="Sem commit"))
        first_session.flush()
        first.close()
        assert second_session.scalar(select(func.count()).select_from(Book)) == 0
    finally:
        first.close()
        second.close()


def test_default_database_path_does_not_follow_working_directory(tmp_path):
    environment = os.environ.copy()
    environment.pop("CADERNO_DATABASE_PATH", None)
    environment["PYTHONPATH"] = str(BACKEND_DIR)
    completed = subprocess.run(
        [sys.executable, "-c", "import json; from app.core.config import get_database_path; print(json.dumps(str(get_database_path())))"],
        cwd=tmp_path, env=environment, check=True, capture_output=True, text=True, encoding="utf-8",
    )
    assert Path(json.loads(completed.stdout)) == BACKEND_DIR / "data" / "caderno.db"
    assert not (tmp_path / "data" / "caderno.db").exists()


def test_relative_database_override_is_rejected(monkeypatch):
    monkeypatch.setenv("CADERNO_DATABASE_PATH", "data/outro.db")
    with pytest.raises(ValueError, match="absoluto"):
        get_database_path()
