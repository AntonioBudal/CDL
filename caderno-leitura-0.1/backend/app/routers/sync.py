from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.sync import SyncChangesResponse
from app.services.sync_service import get_sync_changes

router = APIRouter(prefix="/sync", tags=["Sincronização"])


@router.get(
    "/changes",
    response_model=SyncChangesResponse,
    summary="Consultar feed incremental de alterações e exclusões",
)
def get_changes_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
    since: datetime | None = Query(
        default=None,
        description="Timestamp ISO 8601 em UTC da última sincronização bem-sucedida. Se omitido, retorna o estado completo.",
    ),
) -> SyncChangesResponse:
    return get_sync_changes(session, current_user.id, since=since)
