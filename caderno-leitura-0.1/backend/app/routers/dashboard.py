from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
@router.get("/summary", response_model=DashboardResponse)
def get_dashboard(
    tz_offset: Annotated[int, Query(ge=-840, le=840, description="Deslocamento do fuso local em minutos")] = 0,
    days: Annotated[int, Query(ge=30, le=730, description="Dias para projeção do mapa de calor")] = 365,
    date: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$", description="Filtro opcional por data (YYYY-MM-DD)")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Limite de itens da timeline")] = 30,
    session: Session = Depends(get_session),
) -> DashboardResponse:
    return get_dashboard_data(
        session,
        tz_offset=tz_offset,
        days=days,
        filter_date=date,
        limit=limit,
    )
