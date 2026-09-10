from pathlib import Path

from fastapi import FastAPI

from app import __version__
from app.errors import register_database_error_handlers
from app.frontend import register_frontend
from app.routers import books, chapters, health, imports, studies


def create_app(*, frontend_dist: Path | None = None) -> FastAPI:
    application = FastAPI(
        title="Caderno de Leitura",
        version=__version__,
        description="API local do caderno pessoal de leitura.",
    )
    application.include_router(health.router, prefix="/api")
    application.include_router(books.router, prefix="/api")
    application.include_router(chapters.router, prefix="/api")
    application.include_router(studies.router, prefix="/api")
    application.include_router(imports.router, prefix="/api")
    register_database_error_handlers(application)
    register_frontend(application, frontend_dist)
    return application


app = create_app()
