from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException
from fastapi.testclient import TestClient
import pytest

from app.main import create_app

# Router auxiliar de teste para simular falhas internas
test_error_router = APIRouter(prefix="/api/test-errors")


@test_error_router.get("/unhandled")
def trigger_unhandled_error():
    raise RuntimeError("Falha interna de disco secreta em C:\\Users\\User\\database_secret.py com SQL: SELECT * FROM secrets")


@test_error_router.get("/http-error")
def trigger_http_error():
    raise HTTPException(status_code=404, detail="Recurso de teste não encontrado.")


@pytest.fixture
def error_masking_client():
    application = create_app()
    application.include_router(test_error_router)
    with TestClient(application, raise_server_exceptions=False) as client:
        yield client


def test_unhandled_exception_returns_masked_500_with_error_id(error_masking_client):
    """Garante que exceções não tratadas retornem resposta 500 mascarada e com UUID válido."""
    response = error_masking_client.get("/api/test-errors/unhandled")
    assert response.status_code == 500

    data = response.json()
    assert data.get("detail") == "Ocorreu um erro interno no servidor."
    error_id = data.get("error_id")
    assert error_id is not None
    # Valida formato UUID v4
    parsed_uuid = uuid.UUID(error_id)
    assert parsed_uuid.version == 4

    # Garante que nenhum detalhe sensível vazou no corpo
    body_text = response.text
    assert "C:\\Users\\User" not in body_text
    assert "database_secret.py" not in body_text
    assert "SELECT * FROM secrets" not in body_text
    assert "RuntimeError" not in body_text
    assert "Traceback" not in body_text


def test_http_exceptions_preserve_normal_status_and_detail(error_masking_client):
    """Garante que exceções HTTP comuns (4xx) continuem operando normalmente sem serem mascaradas como 500."""
    response = error_masking_client.get("/api/test-errors/http-error")
    assert response.status_code == 404
    data = response.json()
    assert data.get("detail") == "Recurso de teste não encontrado."
    assert "error_id" not in data
