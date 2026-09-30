from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import DatabaseSession
from app.schemas.support_setting import SupportPublicResponse
from app.services import support_service

router = APIRouter(prefix="/support", tags=["Apoio ao Leitorum"])


@router.get("", response_model=SupportPublicResponse, summary="Consultar parâmetros públicos de apoio")
def get_public_support(
    session: DatabaseSession,
) -> SupportPublicResponse:
    """Retorna dados de apoio voluntário (PIX e link alternativo) para a página /apoie.

    Este endpoint é público e não requer autenticação.
    """
    return support_service.get_public_support_info(session=session)
