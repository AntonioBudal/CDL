"""F0.10.02 — excluir permanentemente apaga o conteúdo dos bytes do banco (.db) e do WAL (-wal).

Só dados fictícios, em tmp_path. Os bytes são lidos com a conexão do pool ainda aberta: fechar a última conexão faz
o SQLite checkpointar e apagar o WAL sozinho, o que esconderia a falha que o teste procura.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import create_sqlite_engine
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.user import User
from app.services import account_service, trash_service

SENTINEL = "SENTINELA-093-FICTICIO"
TEXT = (SENTINEL + " ") * 200
USER_ID = "usuario-ficticio-093"


def _prepare(engine) -> None:
    """Modo WAL, como no banco real; o PRAGMA precisa rodar fora de transação."""
    with engine.connect() as conn:
        raw = conn.connection.dbapi_connection
        previous = raw.autocommit
        raw.autocommit = True
        try:
            raw.execute("PRAGMA journal_mode=WAL")
        finally:
            raw.autocommit = previous
    Base.metadata.create_all(bind=engine)


def _seed(session: Session, *, trashed: bool = False) -> int:
    session.add(User(id=USER_ID, username="leitora_ficticia", display_name="Leitora Fictícia", role="user", status="ativo"))
    book = Book(user_id=USER_ID, title="Livro de Teste")
    session.add(book)
    session.flush()
    chapter = Chapter(book_id=book.id, name="Capítulo 1")
    session.add(chapter)
    session.flush()
    study = Study(user_id=USER_ID, chapter_id=chapter.id, title=SENTINEL, summary=TEXT, explanation=TEXT)
    if trashed:
        study.deleted_at = datetime.now(UTC)
    session.add(study)
    session.commit()
    return study.id


def _sentinel_on_disk(db_path: Path) -> list[str]:
    found = []
    needle = SENTINEL.encode()
    for path in (db_path, db_path.with_name(db_path.name + "-wal")):
        if path.exists() and needle in path.read_bytes():
            found.append(path.name)
    return found


def test_new_connections_enable_secure_delete(tmp_path):
    engine = create_sqlite_engine(tmp_path / "pragma.db")
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA secure_delete")).scalar() == 1
    engine.dispose()


def test_control_without_secure_delete_leaves_sentinel(tmp_path):
    """Controle: com um engine comum, o sentinela continua nos bytes depois da exclusão."""
    db_path = tmp_path / "controle.db"
    engine = create_engine(f"sqlite:///{db_path.as_posix()}", connect_args={"check_same_thread": False})
    _prepare(engine)
    with Session(engine, expire_on_commit=False) as session:
        study_id = _seed(session)
        session.delete(session.get(Study, study_id))
        session.commit()
        assert _sentinel_on_disk(db_path), "o teste precisa conseguir detectar o sentinela"
    engine.dispose()


@pytest.mark.parametrize("action", ["permanent_delete_study", "empty_trash"])
def test_permanent_deletion_wipes_sentinel(tmp_path, action):
    db_path = tmp_path / f"{action}.db"
    engine = create_sqlite_engine(db_path)
    _prepare(engine)
    with Session(engine, expire_on_commit=False) as session:
        study_id = _seed(session, trashed=action == "empty_trash")
        if action == "permanent_delete_study":
            trash_service.permanent_delete_study(session, study_id, user_id=USER_ID)
        else:
            assert trash_service.empty_trash(session, user_id=USER_ID) == (0, 1)
        assert _sentinel_on_disk(db_path) == []
    engine.dispose()


def test_account_deletion_wipes_sentinel_after_router_checkpoint(tmp_path):
    """O serviço só faz flush; o router confirma e chama o checkpoint, aqui reproduzidos na mesma ordem."""
    from app.services.persistence import checkpoint_after_purge, commit_changes

    db_path = tmp_path / "conta.db"
    engine = create_sqlite_engine(db_path)
    _prepare(engine)
    with Session(engine, expire_on_commit=False) as session:
        _seed(session)
        user = session.get(User, USER_ID)
        account_service.delete_account_permanently(session, user, confirmation_text="leitora_ficticia")
        commit_changes(session)
        checkpoint_after_purge(session)
        assert _sentinel_on_disk(db_path) == []
    engine.dispose()


def test_account_router_checkpoints_after_commit():
    source = Path(__file__).resolve().parents[1].joinpath("app", "routers", "account.py").read_text(encoding="utf-8")
    body = source[source.index("def delete_account_endpoint"):]
    body = body[: body.index("return AccountLifecycleResponse")]
    assert body.index("commit_changes(session)") < body.index("checkpoint_after_purge(session)")
