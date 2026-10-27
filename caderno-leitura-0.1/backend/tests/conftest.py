from __future__ import annotations

import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from typing import Any
from unittest.mock import MagicMock, patch
from urllib.parse import unquote, urlsplit

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import BACKEND_DIR


# Isolamento do banco ativo (Constituição II.1). Precisa rodar antes de importar
# app.main, que cria a aplicação no import e já resolve o caminho do banco.
# O lifespan abre sessão direto por get_session(), fora de dependency_overrides;
# sem isto, a manutenção dele rodaria sobre backend/data/caderno.db.
_PROTECTED_DB_PATH = BACKEND_DIR / "data" / "caderno.db"
_SESSION_DB_DIR = Path(tempfile.mkdtemp(prefix="leitorum-pytest-"))
_ORIGINAL_DATABASE_PATH = os.environ.get("CADERNO_DATABASE_PATH")
os.environ["CADERNO_DATABASE_PATH"] = str(_SESSION_DB_DIR / "caderno.db")

_ORIGINAL_SQLITE_CONNECT = sqlite3.connect
_ACTIVE_DB_ATTEMPTS: list[str] = []


def _connect_target_path(database: Any) -> str | None:
    """Extrai o caminho de arquivo de um alvo de sqlite3.connect (None para memória)."""
    if isinstance(database, bytes):
        target = database.decode()
    else:
        target = os.fspath(database)
    if target.startswith("file:"):
        target = unquote(urlsplit(target).path)
        # file:///C:/... vira /C:/... no Windows.
        if len(target) > 2 and target[0] == "/" and target[2] == ":":
            target = target[1:]
    if not target or target == ":memory:":
        return None
    return target


def _normalized(path: str | os.PathLike[str]) -> str:
    return os.path.normcase(os.path.realpath(path))


def _is_protected_target(target: str) -> bool:
    protected = _normalized(_PROTECTED_DB_PATH)
    candidate = _normalized(target)
    return candidate in {protected, protected + "-wal", protected + "-shm", protected + "-journal"}


def _guarded_sqlite_connect(database: Any, *args: Any, **kwargs: Any) -> sqlite3.Connection:
    target = _connect_target_path(database)
    if target is not None and _is_protected_target(target):
        _ACTIVE_DB_ATTEMPTS.append(target)
        raise RuntimeError(f"Teste tentou abrir o banco ativo: {target}")
    return _ORIGINAL_SQLITE_CONNECT(database, *args, **kwargs)


# O dialeto pysqlite do SQLAlchemy usa sqlite3.dbapi2.connect, não sqlite3.connect.
sqlite3.connect = sqlite3.dbapi2.connect = _guarded_sqlite_connect


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if _ACTIVE_DB_ATTEMPTS:
        session.exitstatus = 1


def pytest_unconfigure(config: pytest.Config) -> None:
    sqlite3.connect = sqlite3.dbapi2.connect = _ORIGINAL_SQLITE_CONNECT
    if _ORIGINAL_DATABASE_PATH is None:
        os.environ.pop("CADERNO_DATABASE_PATH", None)
    else:
        os.environ["CADERNO_DATABASE_PATH"] = _ORIGINAL_DATABASE_PATH
    shutil.rmtree(_SESSION_DB_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def _fail_on_active_database_attempt():
    """Falha o teste que tentou abrir o banco ativo, mesmo se a aplicação engoliu o erro."""
    yield
    if _ACTIVE_DB_ATTEMPTS:
        attempts = list(_ACTIVE_DB_ATTEMPTS)
        _ACTIVE_DB_ATTEMPTS.clear()
        pytest.fail(f"Tentativa de abrir o banco ativo durante o teste: {attempts}")


@pytest.fixture(scope="session")
def session_database_dir() -> Path:
    """Diretório temporário que abriga o banco padrão da suíte."""
    return _SESSION_DB_DIR


from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.external_identity import ExternalIdentity
from app.models.local_credential import LocalCredential
from app.models.user import User


TEST_GOOGLE_CLIENT_ID = "test-client-id.apps.googleusercontent.com"


@pytest.fixture(autouse=True)
def isolated_media_vault(tmp_path, monkeypatch):
    """Feature 090-B: chave mestra de teste e cofre próprio em tmp_path para cada teste."""
    import base64

    from app.services import media_service

    monkeypatch.setenv("LEITORUM_MEDIA_MASTER_KEY", base64.b64encode(os.urandom(32)).decode())
    monkeypatch.delenv("LEITORUM_MEDIA_KEY_FILE", raising=False)
    vault_dir = tmp_path / "cofre-de-teste"
    vault_dir.mkdir()
    monkeypatch.setattr(media_service, "_vault_dir", lambda: vault_dir)
    media_service.reset_cache()
    yield vault_dir
    media_service.reset_cache()


@pytest.fixture(autouse=True)
def reset_auth_rate_limiter_fixture():
    """Garante que a memória do rate limiter seja reiniciada para cada teste."""
    from app.core.rate_limiter import auth_rate_limiter
    auth_rate_limiter.reset()
    yield
    auth_rate_limiter.reset()


@pytest.fixture
def mock_google_claims() -> dict[str, Any]:
    """Retorna um payload de claims JWT padrão e sintético emitido pelo Google."""
    return {
        "iss": "https://accounts.google.com",
        "sub": "google-user-sub-12345",
        "aud": TEST_GOOGLE_CLIENT_ID,
        "email": "leitor.google@exemplo.com",
        "email_verified": True,
        "name": "Leitor Google",
        "exp": 9999999999,
        "iat": 1000000000,
    }


@pytest.fixture
def mock_verify_oauth2_token(mock_google_claims):
    """Hermetic mock que intercepta chamadas a google.oauth2.id_token.verify_oauth2_token.

    Nunca realiza chamadas de rede externas e retorna claims controladas pelos testes.
    """
    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = dict(mock_google_claims)
        yield mock_verify


@pytest.fixture
def google_auth_client(tmp_path, monkeypatch, mock_verify_oauth2_token):
    """Cria um cliente de testes hermético com banco SQLite efêmero, REQUIRE_AUTH e GOOGLE_CLIENT_ID."""
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", TEST_GOOGLE_CLIENT_ID)

    db_file = tmp_path / "caderno_test_google_auth.db"
    db_url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with testing_session_local() as db_session:
        # 1. Proprietário canônico
        owner = User(
            id=DEFAULT_OWNER_ID,
            username=DEFAULT_OWNER_USERNAME,
            display_name="Proprietário do Caderno",
            role="admin",
            status="ativo",
        )
        owner_cred = LocalCredential(
            user_id=owner.id,
            password_hash=hash_password("SenhaDoProprietario123!"),
        )

        # 2. Usuário pré-existente com senha local
        local_user = User(
            id="22222222-2222-2222-2222-222222222222",
            username="leitor_local",
            email="leitor.local@exemplo.com",
            display_name="Leitor Local",
            role="user",
            status="ativo",
        )
        local_cred = LocalCredential(
            user_id=local_user.id,
            password_hash=hash_password("SenhaValidaLocal123!"),
        )

        # 3. Usuário já vinculado ao Google
        google_linked_user = User(
            id="33333333-3333-3333-3333-333333333333",
            username="leitor_google",
            email="leitor.google@exemplo.com",
            display_name="Leitor Google Vinculado",
            role="user",
            status="ativo",
        )
        google_identity = ExternalIdentity(
            id="ident-google-1111",
            user_id=google_linked_user.id,
            provider="google",
            provider_subject="google-user-sub-12345",
            email_at_link="leitor.google@exemplo.com",
        )

        # 4. Usuário suspenso vinculado ao Google
        suspended_user = User(
            id="44444444-4444-4444-4444-444444444444",
            username="leitor_suspenso",
            email="suspenso@exemplo.com",
            display_name="Leitor Suspenso",
            role="user",
            status="suspenso",
        )
        suspended_identity = ExternalIdentity(
            id="ident-google-suspended",
            user_id=suspended_user.id,
            provider="google",
            provider_subject="google-sub-suspended-999",
            email_at_link="suspenso@exemplo.com",
        )

        db_session.add_all([
            owner, owner_cred,
            local_user, local_cred,
            google_linked_user, google_identity,
            suspended_user, suspended_identity,
        ])
        db_session.commit()

    def override_get_session():
        session = testing_session_local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client, testing_session_local, mock_verify_oauth2_token

    app.dependency_overrides.clear()
    engine.dispose()
