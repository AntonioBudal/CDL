import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]

# Identidade canônica do proprietário soberano da versão multiusuário
DEFAULT_OWNER_ID: str = "00000000-0000-0000-0000-000000000001"
DEFAULT_OWNER_USERNAME: str = "proprietario"
DEFAULT_OWNER_DISPLAY_NAME: str = "Proprietário do Caderno"



def get_frontend_dist_path() -> Path:
    """Retorna o caminho do build do frontend independente da pasta atual."""
    return BACKEND_DIR.parent / "frontend" / "dist"


def get_database_path() -> Path:
    """Retorna o caminho absoluto canônico do banco de dados ativo.

    Se CADERNO_DATABASE_PATH estiver configurado no ambiente, valida que seja
    um caminho absoluto (disparando ValueError caso contrário) e o resolve.
    Caso padrão: retorna BACKEND_DIR / 'data' / 'caderno.db'.
    """
    configured = os.environ.get("CADERNO_DATABASE_PATH")
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            raise ValueError("CADERNO_DATABASE_PATH deve ser um caminho absoluto.")
        return path.resolve()
    return BACKEND_DIR / "data" / "caderno.db"


def get_backup_dir(database_path: Path | None = None) -> Path:
    """Retorna o diretório dedicado a snapshots e backups (<db_dir>/backups).

    Garante que o diretório exista antes de retornar seu caminho canônico resolvido.
    """
    base_db = database_path or get_database_path()
    backup_dir = base_db.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir.resolve()


def get_covers_dir(database_path: Path | None = None) -> Path:
    """Retorna o diretório dedicado a capas de livros (<db_dir>/covers).

    Se CADERNO_COVERS_DIR estiver configurado no ambiente, valida que seja
    um caminho absoluto (disparando ValueError caso contrário) e o resolve.
    Caso padrão: retorna o diretório 'covers' no mesmo pai do banco de dados ativo.
    Garante que o diretório exista antes de retornar seu caminho canônico resolvido.
    """
    configured = os.environ.get("CADERNO_COVERS_DIR")
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            raise ValueError("CADERNO_COVERS_DIR deve ser um caminho absoluto.")
        covers_dir = path.resolve()
    else:
        base_db = database_path or get_database_path()
        covers_dir = (base_db.parent / "covers").resolve()

    covers_dir.mkdir(parents=True, exist_ok=True)
    return covers_dir
