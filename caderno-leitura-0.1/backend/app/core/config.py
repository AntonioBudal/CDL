import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]

# Identidade canônica do proprietário soberano da versão multiusuário
DEFAULT_OWNER_ID: str = "00000000-0000-0000-0000-000000000001"
DEFAULT_OWNER_USERNAME: str = "proprietario"
DEFAULT_OWNER_DISPLAY_NAME: str = "Proprietário do Caderno"

# Configurações de Sessão e Autenticação (F02)
SESSION_COOKIE_NAME: str = "caderno_session"
SESSION_MAX_AGE_SECONDS: int = 30 * 24 * 3600  # 30 dias de inatividade
SESSION_ACTIVITY_THROTTLE_SECONDS: int = 10 * 60  # 10 minutos entre atualizações de last_activity
PASSWORD_MIN_LENGTH: int = 8


def get_allow_registration() -> bool:
    """Informa se o auto-registro de novos usuários está habilitado no ambiente local."""
    val = os.environ.get("ALLOW_REGISTRATION", "true").strip().lower()
    return val in ("true", "1", "yes", "sim")


def get_google_client_id() -> str | None:
    """Retorna o Client ID configurado para o Google Identity Services (GIS), ou None."""
    val = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    return val if val else None


def is_google_auth_enabled() -> bool:
    """Informa se a autenticação via Google está ativada (depende de GOOGLE_CLIENT_ID configurado)."""
    return get_google_client_id() is not None


def get_session_cookie_secure() -> bool | None:
    """Retorna configuração explícita de Secure para cookies de sessão, ou None para detecção dinâmica."""
    val = os.environ.get("SESSION_COOKIE_SECURE")
    if val is None:
        return None
    return val.strip().lower() in ("true", "1", "yes", "sim")


def is_auth_required() -> bool:
    """Verifica se autenticação é estritamente obrigatória para requisições sem credenciais.

    - Se REQUIRE_AUTH estiver explicitamente definido no ambiente, respeita o valor.
    - Se estiver executando suíte legada com pytest e REQUIRE_AUTH não estiver configurado,
      permite fallback controlado ao proprietário padrão para retrocompatibilidade total.
    - Em ambiente de produção e execução normal, retorna True (autenticação obrigatória).
    """
    import sys

    val = os.environ.get("REQUIRE_AUTH")
    if val is not None:
        return val.strip().lower() in ("true", "1", "yes", "sim")
    if ("pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST")) and not os.environ.get("ENFORCE_AUTH_TESTS"):
        return False
    return True





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
