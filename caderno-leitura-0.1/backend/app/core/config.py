import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _load_env_file() -> None:
    """Carrega variáveis de ambiente de um arquivo .env se presente na raiz do projeto ou em backend/."""
    import sys
    is_pytest = "pytest" in sys.modules or bool(os.environ.get("PYTEST_CURRENT_TEST"))
    for candidate in (BACKEND_DIR.parent / ".env", BACKEND_DIR / ".env"):
        if candidate.is_file():
            try:
                with candidate.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if is_pytest and k == "REQUIRE_AUTH":
                                continue
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass


_load_env_file()

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
    """Retorna o Client ID configurado para o Google Identity Services (GIS) e OAuth, ou None."""
    val = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    return val if val else None


def get_google_client_secret() -> str | None:
    """Retorna o Client Secret configurado para o fluxo Google OAuth 2.0 Web, ou None."""
    val = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    return val if val else None


def get_google_redirect_uri() -> str:
    """Retorna a URL de redirecionamento para o callback do Google OAuth 2.0."""
    return os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback").strip()


def is_google_auth_enabled() -> bool:
    """Informa se a autenticação via Google está ativada (depende de GOOGLE_CLIENT_ID configurado)."""
    return get_google_client_id() is not None


# Configurações de Rate Limiting e Proteção de Autenticação (F10)
DEFAULT_RATE_LIMIT_ATTEMPTS = 5
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 300  # 5 minutos
DEFAULT_LOCKOUT_DURATION_SECONDS = 900   # 15 minutos


def get_rate_limit_max_attempts() -> int:
    """Número máximo de tentativas inválidas permitidas na janela de tempo."""
    try:
        return int(os.environ.get("RATE_LIMIT_MAX_ATTEMPTS", str(DEFAULT_RATE_LIMIT_ATTEMPTS)))
    except ValueError:
        return DEFAULT_RATE_LIMIT_ATTEMPTS


def get_rate_limit_window_seconds() -> int:
    """Tamanho da janela deslizante de rate limiting em segundos."""
    try:
        return int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", str(DEFAULT_RATE_LIMIT_WINDOW_SECONDS)))
    except ValueError:
        return DEFAULT_RATE_LIMIT_WINDOW_SECONDS


def get_lockout_duration_seconds() -> int:
    """Duração do bloqueio de conta após sucessivas falhas de autenticação."""
    try:
        return int(os.environ.get("LOCKOUT_DURATION_SECONDS", str(DEFAULT_LOCKOUT_DURATION_SECONDS)))
    except ValueError:
        return DEFAULT_LOCKOUT_DURATION_SECONDS


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


def get_avatars_dir(database_path: Path | None = None) -> Path:
    """Retorna o diretório dedicado a avatares de usuários (<db_dir>/avatars).

    Se CADERNO_AVATARS_DIR estiver configurado no ambiente, valida que seja
    um caminho absoluto (disparando ValueError caso contrário) e o resolve.
    Caso padrão: retorna o diretório 'avatars' no mesmo pai do banco de dados ativo.
    Garante que o diretório exista antes de retornar seu caminho canônico resolvido.
    """
    configured = os.environ.get("CADERNO_AVATARS_DIR")
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            raise ValueError("CADERNO_AVATARS_DIR deve ser um caminho absoluto.")
        avatars_dir = path.resolve()
    else:
        base_db = database_path or get_database_path()
        avatars_dir = (base_db.parent / "avatars").resolve()

    avatars_dir.mkdir(parents=True, exist_ok=True)
    return avatars_dir


def get_app_base_url() -> str:
    """Retorna a URL base pública do Leitorum configurada no ambiente."""
    return os.environ.get("APP_BASE_URL", "https://leitorum.com").strip().rstrip("/")


# Configurações de Segurança e CORS (F0.6.9)
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
DEFAULT_DEVELOPMENT_SESSION_SECRET = "caderno-secret-key-development-change-me"


def get_cors_allowed_origins() -> list[str]:
    """Retorna lista de origens autorizadas para CORS a partir de CADERNO_CORS_ORIGINS."""
    val = os.environ.get("CADERNO_CORS_ORIGINS", "").strip()
    if not val:
        return list(DEFAULT_CORS_ORIGINS)
    origins = [item.strip() for item in val.split(",") if item.strip()]
    # Nunca permitir '*' com credentials
    return [orig for orig in origins if orig != "*"]


def get_session_secret() -> str:
    """Retorna a chave secreta de sessão configurada no ambiente."""
    return os.environ.get("CADERNO_SESSION_SECRET", DEFAULT_DEVELOPMENT_SESSION_SECRET).strip()


def is_production_environment() -> bool:
    """Informa se a aplicação está operando em modo de produção explícito."""
    env = os.environ.get("ENVIRONMENT", "").strip().lower()
    return env in ("production", "prod")


def audit_session_secret() -> tuple[bool, str | None]:
    """Audita a segurança da chave de sessão configurada.
    
    Retorna (is_safe, warning_message). Se for chave padrão em produção ou chave curta (<16 chars), emite aviso.
    """
    secret = get_session_secret()
    if secret == DEFAULT_DEVELOPMENT_SESSION_SECRET:
        if is_production_environment():
            return False, "CADERNO_SESSION_SECRET está utilizando a chave padrão insegura em ambiente de produção!"
        return True, "CADERNO_SESSION_SECRET utilizando chave de desenvolvimento padrão."
    if len(secret) < 16:
        return False, "CADERNO_SESSION_SECRET é muito curta (menos de 16 caracteres); recomenda-se ao menos 32 caracteres."
    return True, None


