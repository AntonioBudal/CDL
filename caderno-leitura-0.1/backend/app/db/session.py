from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from sqlite3 import Connection

from sqlalchemy import URL, Engine, create_engine, event
from sqlalchemy.orm import Session

from app.core.config import get_database_path


def sqlite_url(path: Path) -> URL:
    if not path.is_absolute():
        raise ValueError("O caminho do banco deve ser absoluto.")
    return URL.create("sqlite+pysqlite", database=str(path))


def _configure_connection(connection: Connection, _record: object) -> None:
    # PRAGMA foreign_keys precisa ser executado fora de uma transacao.
    previous = connection.autocommit
    connection.autocommit = True
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            if cursor.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
                raise RuntimeError("Nao foi possivel ativar as chaves estrangeiras do SQLite.")
        finally:
            cursor.close()
    finally:
        connection.autocommit = previous


def create_sqlite_engine(path: Path) -> Engine:
    url = sqlite_url(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False, "autocommit": False, "timeout": 10},
    )
    event.listen(engine, "connect", _configure_connection)
    return engine


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    # A importacao da aplicacao nao abre nem recria o banco.
    return create_sqlite_engine(get_database_path())


def get_session() -> Iterator[Session]:
    """Uma sessao por requisicao; a operacao de escrita deve confirmar seu commit."""
    with Session(get_engine(), expire_on_commit=False) as session:
        yield session
