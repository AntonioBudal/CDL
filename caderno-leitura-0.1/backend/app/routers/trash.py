"""Rotas dedicadas da lixeira (/api/trash)."""
from fastapi import APIRouter

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.book import BookRead
from app.schemas.trash import (
    TrashActionResponse,
    TrashEmptyResponse,
    TrashPurgeResponse,
    TrashSummaryResponse,
)
from app.services import trash_service

router = APIRouter(prefix="/trash", tags=["trash"])


@router.get("", response_model=TrashSummaryResponse, summary="Listar itens da lixeira")
def get_trash(session: DatabaseSession, current_user: CurrentUser) -> TrashSummaryResponse:
    """Retorna itens na lixeira com dias restantes e sumário agregado após purga de expirados."""
    trash_service.purge_expired_trash(session, user_id=current_user.id)
    trash_data = trash_service.get_trash_items(session, user_id=current_user.id)
    return TrashSummaryResponse(
        books=trash_data["books"],
        studies=trash_data["studies"],
        total_items=len(trash_data["books"]) + len(trash_data["studies"]),
    )


@router.post("/empty", response_model=TrashEmptyResponse, summary="Esvaziar lixeira completamente")
def empty_trash_endpoint(session: DatabaseSession, current_user: CurrentUser) -> TrashEmptyResponse:
    """Expurga definitivamente todos os itens atualmente na lixeira."""
    purged_books, purged_studies = trash_service.empty_trash(session, user_id=current_user.id)
    return TrashEmptyResponse(
        purged_books=purged_books,
        purged_studies=purged_studies,
        message="Lixeira esvaziada com sucesso.",
    )


@router.post("/purge-expired", response_model=TrashPurgeResponse, summary="Purgar itens expirados (>30 dias)")
def purge_expired_endpoint(session: DatabaseSession, current_user: CurrentUser) -> TrashPurgeResponse:
    """Expurga itens da lixeira que ultrapassaram a janela de retenção de 30 dias."""
    purged_books, purged_studies = trash_service.purge_expired_trash(session, user_id=current_user.id)
    return TrashPurgeResponse(
        purged_books=purged_books,
        purged_studies=purged_studies,
    )


@router.post("/books/{book_id}/restore", response_model=BookRead, summary="Restaurar livro da lixeira")
def restore_book_from_trash(book_id: Identifier, session: DatabaseSession, current_user: CurrentUser) -> BookRead:
    return trash_service.restore_book(session, book_id, user_id=current_user.id)


@router.post("/studies/{study_id}/restore", response_model=TrashActionResponse, summary="Restaurar estudo da lixeira")
def restore_study_from_trash(study_id: Identifier, session: DatabaseSession, current_user: CurrentUser) -> TrashActionResponse:
    study, book_restored = trash_service.restore_study(session, study_id, user_id=current_user.id)
    return TrashActionResponse(
        id=study.id,
        title=study.title,
        deleted_at=study.deleted_at,
        book_restored=book_restored,
    )
