from contextlib import closing
from pathlib import Path
import sqlite3
from time import monotonic

from app.core.config import get_database_path


def create_database_backup(
    destination: Path, *, timeout_seconds: float = 30.0
) -> None:
    source = get_database_path()

    if not source.is_file():
        raise FileNotFoundError("Banco de dados não encontrado.")

    if source.stat().st_size == 0:
        raise sqlite3.DatabaseError("O arquivo do banco está vazio.")

    deadline = monotonic() + timeout_seconds

    def check_progress(
        status: int, _remaining: int, _total: int
    ) -> None:
        if status != sqlite3.SQLITE_DONE and monotonic() >= deadline:
            raise TimeoutError(
                "O banco permaneceu ocupado durante o backup."
            )

    # Abre o banco original somente para leitura.
    source_uri = source.as_uri() + "?mode=ro"

    with closing(
        sqlite3.connect(
            source_uri,
            uri=True,
            timeout=1.0,
            autocommit=True,
        )
    ) as original:
        with closing(
            sqlite3.connect(
                destination,
                timeout=1.0,
                autocommit=True,
            )
        ) as snapshot:
            original.backup(
                snapshot,
                pages=256,
                progress=check_progress,
                sleep=0.05,
            )

            # A cópia deve funcionar sozinha, sem arquivos -wal/-shm.
            # Esta configuração afeta somente a cópia temporária.
            snapshot.execute("PRAGMA journal_mode=DELETE")

            if snapshot.execute("PRAGMA quick_check").fetchall() != [
                ("ok",)
            ]:
                raise sqlite3.DatabaseError(
                    "A cópia falhou na verificação."
                )

            if (
                snapshot.execute("PRAGMA foreign_key_check").fetchone()
                is not None
            ):
                raise sqlite3.DatabaseError(
                    "A cópia contém vínculos inválidos."
                )