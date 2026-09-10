import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]


def get_frontend_dist_path() -> Path:
    # Independente da pasta usada para iniciar o servidor.
    return BACKEND_DIR.parent / "frontend" / "dist"


def get_database_path() -> Path:
    configured = os.environ.get("CADERNO_DATABASE_PATH")
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            raise ValueError("CADERNO_DATABASE_PATH deve ser um caminho absoluto.")
        return path.resolve()
    return BACKEND_DIR / "data" / "caderno.db"
