import asyncio
from contextlib import asynccontextmanager, suppress
import logging
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.core.config import audit_session_secret, get_cors_allowed_origins
from app.core.security_headers import SecurityHeadersMiddleware
from app.errors import register_database_error_handlers, register_global_error_handlers
from app.frontend import register_frontend
from app.routers import (
    account,
    admin,
    auth,
    backups,
    books,
    canvas,
    categories,
    chapters,
    covers,
    dashboard,
    digitize,
    friends,
    health,
    imports,
    media,
    inbox,
    notifications,
    preferences,
    profile,
    review,
    search,
    seo,
    sharing,
    studies,
    study_highlights,
    study_mentions,
    study_relations,
    study_sessions,
    study_versions,
    support,
    sync,
    trash,
    users,
)

logger = logging.getLogger("leitorum.security")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cotas e retenção do cofre (feature 090-C): configuração inválida impede a partida.
    from app.core.config import validate_media_settings

    validate_media_settings()

    # Auditoria de segurança de credenciais e chave de sessão na inicialização
    is_safe, warning_msg = audit_session_secret()
    if warning_msg and not is_safe:
        logger.warning(f"[SEGURANÇA] {warning_msg}")

    # Purga itens na lixeira há mais de 30 dias, notificações lidas há mais de 60 dias e sincroniza catálogo canônico
    try:
        from app.db.session import get_session
        from app.services.category_service import sync_canonical_categories
        from app.services.notification_service import purge_expired_notifications
        from app.services.persistence import commit_changes
        from app.services.trash_service import purge_expired_trash

        for session in get_session():
            purge_expired_trash(session)
            sync_canonical_categories(session)
            purge_expired_notifications(session, retention_days=60)
            commit_changes(session)
            break
    except Exception:
        pass

    # Cofre de imagens (feature 090-B): confere a chave na partida; um cofre trancado não impede o resto do app.
    if "pytest" not in sys.modules:
        try:
            from app.db.session import get_session
            from app.services import media_service

            for session in get_session():
                logger.info("Cofre de imagens: %s", media_service.vault_status(session)["state"])
                break
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cofre de imagens não verificado na partida: %s", type(exc).__name__)

    # Camada de proteção 2 (feature 090-A): backup automático na partida e a cada hora, se vencido.
    auto_backup = None
    media_retention = None
    if "pytest" not in sys.modules:
        auto_backup = asyncio.create_task(_auto_backup_loop())
        # Retenção do cofre (feature 090-C): na partida e a cada LEITORUM_MEDIA_JOB_INTERVAL_HOURS.
        media_retention = asyncio.create_task(_media_retention_loop())
    try:
        yield
    finally:
        for task in (auto_backup, media_retention):
            if task is not None:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task


async def _auto_backup_loop() -> None:
    from app.services.maintenance import run_auto_backup_if_due

    while True:
        try:
            await asyncio.to_thread(run_auto_backup_if_due)
        except Exception as exc:  # noqa: BLE001 — nunca derruba o servidor; só registra o tipo
            logger.warning("Backup automático falhou: %s", type(exc).__name__)
        await asyncio.sleep(3600)


async def _media_retention_loop() -> None:
    from app.core.config import get_media_job_interval_hours
    from app.services.media_retention import run_once

    while True:
        try:
            await asyncio.to_thread(run_once)
        except Exception as exc:  # noqa: BLE001 — nunca derruba o servidor; só registra o tipo
            logger.warning("Retenção do cofre falhou: %s", type(exc).__name__)
        await asyncio.sleep(get_media_job_interval_hours() * 3600)


def create_app(*, frontend_dist: Path | None = None) -> FastAPI:
    application = FastAPI(
        title="Leitorum API",
        version=__version__,
        description="API da plataforma Leitorum para registro, estudos e organização de leitura.",
        lifespan=lifespan,
    )

    # Middleware CORS controlado por lista explícita de origens (T006)
    cors_origins = get_cors_allowed_origins()
    if cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Injeção incondicional de cabeçalhos de segurança consagrados e CSP em modo Enforce (T005, T014)
    application.add_middleware(SecurityHeadersMiddleware)

    application.include_router(health.router, prefix="/api")
    application.include_router(auth.router, prefix="/api")
    application.include_router(account.router, prefix="/api")
    application.include_router(admin.router, prefix="/api")
    application.include_router(backups.router, prefix="/api")
    application.include_router(categories.router, prefix="/api")
    application.include_router(books.router, prefix="/api")
    application.include_router(chapters.router, prefix="/api")
    application.include_router(inbox.router, prefix="/api")
    application.include_router(study_mentions.router, prefix="/api")
    application.include_router(study_relations.router, prefix="/api")
    application.include_router(studies.router, prefix="/api")
    application.include_router(study_highlights.router, prefix="/api")
    application.include_router(study_versions.router, prefix="/api")
    application.include_router(canvas.router, prefix="/api")
    application.include_router(imports.router, prefix="/api")
    application.include_router(digitize.router, prefix="/api")
    application.include_router(media.router, prefix="/api")
    application.include_router(media.study_router, prefix="/api")
    application.include_router(trash.router, prefix="/api")
    application.include_router(covers.router, prefix="/api")
    application.include_router(dashboard.router, prefix="/api")
    application.include_router(search.router, prefix="/api")
    application.include_router(sync.router, prefix="/api")
    application.include_router(preferences.router, prefix="/api")
    application.include_router(profile.router, prefix="/api")
    application.include_router(profile.avatars_router, prefix="/api")
    application.include_router(users.router, prefix="/api")
    application.include_router(friends.router, prefix="/api")
    application.include_router(sharing.router, prefix="/api")
    application.include_router(notifications.router, prefix="/api")
    application.include_router(support.router, prefix="/api")
    application.include_router(review.router, prefix="/api")
    application.include_router(study_sessions.router, prefix="/api")
    application.include_router(seo.router)

    # Registro de manipuladores de erro de banco e mascaramento global 500 (T007, T018)
    register_database_error_handlers(application)
    register_global_error_handlers(application)
    register_frontend(application, frontend_dist)
    return application


app = create_app()
