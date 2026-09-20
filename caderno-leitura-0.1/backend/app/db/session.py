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


import unicodedata


def sqlite_unaccent(text: str | None) -> str:
    """Normaliza texto removendo acentos diacríticos e convertendo para minúsculas."""
    if text is None:
        return ""
    normalized = unicodedata.normalize("NFKD", str(text))
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


def _configure_sqlite_functions(connection: Connection, _record: object) -> None:
    connection.create_function("unaccent", 1, sqlite_unaccent, deterministic=True)


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


def create_sqlite_engine(path: Path, *, enable_foreign_keys: bool = True) -> Engine:
    url = sqlite_url(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False, "autocommit": False, "timeout": 10},
    )
    event.listen(engine, "connect", _configure_sqlite_functions)
    if enable_foreign_keys:
        event.listen(engine, "connect", _configure_connection)
    return engine



@lru_cache(maxsize=8)
def _get_engine_for_path(path: Path) -> Engine:
    return create_sqlite_engine(path)


def get_engine() -> Engine:
    # A importacao da aplicacao nao abre nem recria o banco.
    return _get_engine_for_path(get_database_path())


def get_session() -> Iterator[Session]:
    """Uma sessao por requisicao; a operacao de escrita deve confirmar seu commit."""
    with Session(get_engine(), expire_on_commit=False) as session:
        yield session
