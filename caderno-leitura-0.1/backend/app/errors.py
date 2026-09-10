from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError


def register_database_error_handlers(application: FastAPI) -> None:
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
