from fastapi import APIRouter, File, Request, Response, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from app.dependencies import CurrentUser
from app.schemas.digitize import DigitizePreviewRead, DigitizeStatusRead
from app.services import digitize_service
from app.services.digitize_service import DigitizeError

router = APIRouter(prefix="/digitize", tags=["Digitalização"])

NO_STORE = {"Cache-Control": "no-store"}


def _error_response(error: DigitizeError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status,
        content={"detail": error.detail, "code": error.code},
        headers={**NO_STORE, **(error.headers or {})},
    )


@router.get(
    "/status",
    response_model=DigitizeStatusRead,
    summary="Informar se a digitalização está disponível",
    description="Confere uma vez se o motor de leitura está instalado e íntegro. Não acessa o acervo.",
)
async def digitize_status(_current_user: CurrentUser, response: Response) -> DigitizeStatusRead:
    response.headers.update(NO_STORE)
    return await run_in_threadpool(digitize_service.engine_status)


@router.post(
    "/preview",
    response_model=DigitizePreviewRead,
    summary="Ler a foto de uma página manuscrita para revisão",
    description=(
        "Lê a imagem (JPEG, PNG ou WebP) no próprio computador e devolve o texto por linha, com a "
        "confiança de cada uma. Não grava nada no banco e apaga a imagem ao terminar. Após revisar, "
        "use POST /api/studies para salvar."
    ),
    responses={413: {}, 415: {}, 422: {}, 500: {}, 503: {}, 504: {}},
)
async def digitize_preview(
    request: Request,
    _current_user: CurrentUser,
    file: UploadFile = File(...),
):
    try:
        result = await digitize_service.preview(file, request.is_disconnected)
    except DigitizeError as error:
        return _error_response(error)
    return JSONResponse(content=result.model_dump(mode="json"), headers=NO_STORE)
