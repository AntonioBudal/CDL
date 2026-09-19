"""Rotas dedicadas da lixeira (/api/trash)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.trash import TrashEmptyResponse, TrashPurgeResponse, TrashSummaryResponse
from app.services import trash_service

router = APIRouter(prefix="/trash", tags=["trash"])


@router.get("", response_model=TrashSummaryResponse, summary="Listar itens da lixeira")
def get_trash(session: Session = Depends(get_session)) -> TrashSummaryResponse:
    """Retorna itens na lixeira com dias restantes e sumário agregado após purga de expirados."""
    trash_service.purge_expired_trash(session)
    trash_data = trash_service.get_trash_items(session)
    return TrashSummaryResponse(
        books=trash_data["books"],
        studies=trash_data["studies"],
        total_items=len(trash_data["books"]) + len(trash_data["studies"]),
    )


@router.post("/empty", response_model=TrashEmptyResponse, summary="Esvaziar lixeira completamente")
def empty_trash_endpoint(session: Session = Depends(get_session)) -> TrashEmptyResponse:
    """Expurga definitivamente todos os itens atualmente na lixeira."""
    purged_books, purged_studies = trash_service.empty_trash(session)
    return TrashEmptyResponse(
        purged_books=purged_books,
        purged_studies=purged_studies,
        message="Lixeira esvaziada com sucesso.",
    )


@router.post("/purge-expired", response_model=TrashPurgeResponse, summary="Purgar itens expirados (>30 dias)")
def purge_expired_endpoint(session: Session = Depends(get_session)) -> TrashPurgeResponse:
    """Expurga itens da lixeira que ultrapassaram a janela de retenção de 30 dias."""
    purged_books, purged_studies = trash_service.purge_expired_trash(session)
    return TrashPurgeResponse(
        purged_books=purged_books,
        purged_studies=purged_studies,
    )
