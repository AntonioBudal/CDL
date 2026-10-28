"""Raiz única de armazenamento (feature 090-A): marcador de identidade e verificação.

A raiz configurada em ``LEITORUM_STORAGE_ROOT`` (por exemplo o HD de 1 TB) guarda ``db/``, ``backups/`` e,
na fatia B, ``vault/``. O arquivo ``.leitorum-storage.json`` identifica a raiz com um ``storage_id``
(UUID) que também fica gravado no banco (tabela ``storage_settings``). Sem o marcador certo, nada é
criado e o Leitorum não inicia: um disco ausente ou trocado nunca vira um banco vazio novo.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

MARKER_NAME = ".leitorum-storage.json"
MARKER_FORMAT = 1


class StorageError(RuntimeError):
    """Raiz de armazenamento ausente, sem marcador ou diferente do esperado."""


def marker_path(root: Path) -> Path:
    return root / MARKER_NAME


def read_marker(root: Path) -> dict | None:
    """Conteúdo do marcador, ou ``None`` se não existir. Marcador ilegível levanta ``StorageError``."""
    path = marker_path(root)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        uuid.UUID(str(data["storage_id"]))
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise StorageError("O marcador da pasta de armazenamento está ilegível.") from error
    return data


def write_marker(root: Path, storage_id: str | None = None) -> str:
    """Cria o marcador com gravação atômica; devolve o ``storage_id``. Recusa sobrescrever um existente."""
    path = marker_path(root)
    if path.exists():
        raise StorageError("A pasta de armazenamento já tem um marcador.")
    storage_id = storage_id or str(uuid.uuid4())
    body = {
        "storage_id": storage_id,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "format": MARKER_FORMAT,
    }
    temporary = path.with_name(path.name + ".tmp")
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(body, handle)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    return storage_id


def database_storage_id(database_path: Path) -> str | None:
    """``storage_id`` gravado no banco (só leitura); ``None`` se a tabela ou a linha não existirem."""
    if not database_path.is_file():
        return None
    connection = sqlite3.connect(f"{database_path.resolve().as_uri()}?mode=ro", uri=True)
    try:
        row = connection.execute("SELECT storage_id FROM storage_settings WHERE id = 1").fetchone()
    except sqlite3.OperationalError:
        return None
    finally:
        connection.close()
    return str(row[0]) if row else None


def verify_root(root: Path, database_path: Path | None = None) -> str:
    """Confere a raiz: existe, tem marcador e, se houver banco, o mesmo ``storage_id``. Devolve o ID."""
    if not root.is_dir():
        raise StorageError(
            "O HD de armazenamento não foi encontrado. Conecte o disco configurado em LEITORUM_STORAGE_ROOT "
            "e inicie de novo."
        )
    marker = read_marker(root)
    if marker is None:
        raise StorageError(
            "A pasta de armazenamento não tem o marcador do Leitorum. Confira se o disco é o certo ou rode a "
            "migração para o HD."
        )
    storage_id = str(marker["storage_id"])
    if database_path is not None:
        if not database_path.is_file():
            raise StorageError("O banco não foi encontrado na pasta de armazenamento.")
        if database_storage_id(database_path) != storage_id:
            raise StorageError(
                "O banco e a pasta de armazenamento não combinam (identidade diferente). Confira o disco."
            )
    return storage_id
