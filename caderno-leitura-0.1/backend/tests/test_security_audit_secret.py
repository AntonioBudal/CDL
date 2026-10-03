import logging
import pytest
from app.core.config import (
    DEFAULT_DEVELOPMENT_SESSION_SECRET,
    audit_session_secret,
    get_session_secret,
    is_production_environment,
)
from app.main import create_app
from fastapi.testclient import TestClient


def test_audit_session_secret_in_development(monkeypatch):
    """Em ambiente de desenvolvimento com chave padrão, emite aviso informativo mas é considerado seguro para dev."""
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("CADERNO_SESSION_SECRET", raising=False)

    is_safe, msg = audit_session_secret()
    assert is_safe is True
    assert "desenvolvimento" in msg.lower()


def test_audit_session_secret_in_production_with_default_secret(monkeypatch, caplog):
    """Em ambiente de produção com chave padrão, deve acusar falha de segurança e logar warning no lifespan."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("CADERNO_SESSION_SECRET", raising=False)

    is_safe, msg = audit_session_secret()
    assert is_safe is False
    assert "produção" in msg.lower() or "insegura" in msg.lower()

    # Testa o lifespan emitindo o log
    with caplog.at_level(logging.WARNING, logger="leitorum.security"):
        app = create_app()
        with TestClient(app):
            pass
    assert any("[SEGURANÇA]" in record.message for record in caplog.records)


def test_audit_session_secret_with_short_key(monkeypatch):
    """Chave com menos de 16 caracteres deve ser apontada como insegura."""
    monkeypatch.setenv("CADERNO_SESSION_SECRET", "curta123")

    is_safe, msg = audit_session_secret()
    assert is_safe is False
    assert "muito curta" in msg.lower()


def test_audit_session_secret_with_strong_custom_key(monkeypatch):
    """Chave forte customizada deve passar com is_safe True e sem aviso."""
    monkeypatch.setenv("CADERNO_SESSION_SECRET", "chave-super-secreta-de-producao-com-mais-de-32-caracteres!")

    is_safe, msg = audit_session_secret()
    assert is_safe is True
    assert msg is None
