from fastapi import APIRouter, Response

from app import __version__
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Sistema"])


@router.get("/health", response_model=HealthResponse, summary="Verificar a API local")
def get_health(response: Response) -> HealthResponse:
    response.headers["Cache-Control"] = "no-store"
    return HealthResponse(
        status="ok",
        service="caderno-leitura",
        version=__version__,
    )
