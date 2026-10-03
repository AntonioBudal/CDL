import logging
from typing import Any
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("leitorum.security")


class ConcurrencyConflictError(Exception):
    def __init__(
        self,
        entity_id: int,
        entity_type: str,
        server_version: int,
        server_updated_at: Any,
        server_data: dict[str, Any],
        detail: str | None = None,
    ) -> None:
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.server_version = server_version
        self.server_updated_at = (
            server_updated_at.isoformat()
            if hasattr(server_updated_at, "isoformat")
            else str(server_updated_at)
        )
        self.server_data = server_data
        self.detail = (
            detail
            or f"Conflito de concorrência: este {entity_type} foi modificado em outro dispositivo. Seus dados foram preservados no formulário."
        )


def register_database_error_handlers(application: FastAPI) -> None:
    @application.exception_handler(ConcurrencyConflictError)
    async def concurrency_conflict_error(_request: Request, error: ConcurrencyConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "detail": error.detail,
                "entity_id": error.entity_id,
                "entity_type": error.entity_type,
                "server_version": error.server_version,
                "server_updated_at": error.server_updated_at,
                "server_data": error.server_data,
            },
        )

    @application.exception_handler(IntegrityError)
    async def integrity_error(_request: Request, _error: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "Não foi possível salvar porque os dados conflitam com uma restrição do banco."},
        )

    @application.exception_handler(OperationalError)
    async def database_unavailable(_request: Request, _error: OperationalError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": "O banco não está disponível. Confira as migrações e tente novamente."},
        )


def register_global_error_handlers(application: FastAPI) -> None:
    """Registra manipulador global de exceções não tratadas (HTTP 500) com mascaramento e error_id."""

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, StarletteHTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=getattr(exc, "headers", None),
            )

        error_id = str(uuid.uuid4())
        logger.error(
            f"Erro interno não tratado [error_id={error_id}] em {request.method} {request.url.path}: {exc}",
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Ocorreu um erro interno no servidor.",
                "error_id": error_id,
            },
        )
