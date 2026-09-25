from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app import __version__
from app.errors import register_database_error_handlers
from app.frontend import register_frontend
from app.routers import (
    auth,
    backups,
    books,
    canvas,
    categories,
    chapters,
    covers,
    dashboard,
    health,
    imports,
    preferences,
    search,
    studies,
    study_relations,
    sync,
    trash,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Purga itens na lixeira há mais de 30 dias e sincroniza catálogo canônico na inicialização
    try:
        from app.db.session import get_session
        from app.services.category_service import sync_canonical_categories
        from app.services.trash_service import purge_expired_trash

        for session in get_session():
            purge_expired_trash(session)
            sync_canonical_categories(session)
            break
    except Exception:
        pass
    yield


def create_app(*, frontend_dist: Path | None = None) -> FastAPI:
    application = FastAPI(
        title="Caderno de Leitura",
        version=__version__,
        description="API local do caderno pessoal de leitura.",
        lifespan=lifespan,
    )
    application.include_router(health.router, prefix="/api")
    application.include_router(auth.router, prefix="/api")
    application.include_router(backups.router, prefix="/api")
    application.include_router(categories.router, prefix="/api")
    application.include_router(books.router, prefix="/api")
    application.include_router(chapters.router, prefix="/api")
    application.include_router(study_relations.router, prefix="/api")
    application.include_router(studies.router, prefix="/api")
    application.include_router(canvas.router, prefix="/api")
    application.include_router(imports.router, prefix="/api")
    application.include_router(trash.router, prefix="/api")
    application.include_router(covers.router, prefix="/api")
    application.include_router(dashboard.router, prefix="/api")
    application.include_router(search.router, prefix="/api")
    application.include_router(sync.router, prefix="/api")
    application.include_router(preferences.router, prefix="/api")
    register_database_error_handlers(application)
    register_frontend(application, frontend_dist)
    return application


app = create_app()
