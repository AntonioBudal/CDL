from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.imports import ImportPreviewRead, ImportPreviewRequest, ImportWarningRead
from app.schemas.organize import OrganizeRead, OrganizeRequest, OrganizeStatusRead
from app.services.import_parser import parse_response
from app.services.organizer import adapter_service
from app.services.organizer import loader as organizer

router = APIRouter(prefix="/imports", tags=["Importação"])


@router.post(
    "/preview",
    response_model=ImportPreviewRead,
    summary="Dividir a resposta em seções para conferência",
    description=(
        "Devolve a resposta original, as quatro seções, os avisos e o texto não associado. "
        "Não acessa o banco. Após revisar, use POST /api/studies para salvar os campos revisados."
    ),
)
def preview_import(payload: ImportPreviewRequest, response: Response) -> ImportPreviewRead:
    parsed = parse_response(payload.source_response)
    response.headers["Cache-Control"] = "no-store"
    return ImportPreviewRead(
        source_response=parsed.source_response,
        **parsed.sections,
        unassigned_text=parsed.unassigned_text,
        warnings=[ImportWarningRead.model_validate(warning) for warning in parsed.warnings],
    )


NO_STORE = {"Cache-Control": "no-store"}


@router.get(
    "/organize/status",
    response_model=OrganizeStatusRead,
    summary="Informar se a organização nas 4 seções está disponível",
    description="Confere uma vez se o artefato do organizador está presente e íntegro. Não acessa o banco.",
)
def organize_status(_current_user: CurrentUser, response: Response) -> OrganizeStatusRead:
    response.headers.update(NO_STORE)
    return OrganizeStatusRead(**organizer.status())


@router.post(
    "/organize",
    response_model=OrganizeRead,
    summary="Sugerir a distribuição do texto nas 4 seções do estudo",
    description=(
        "Divide o texto em trechos e sugere a seção de cada um (Resumo, Explicação, Conceitos, Referências), "
        "sem alterar nenhuma palavra. Não lê estudos nem grava no banco; só com o adaptador ligado "
        "(LEITORUM_ORGANIZER_ADAPTER=on) lê o estado do adaptador do usuário. Após revisar, use POST /api/studies."
    ),
    responses={413: {}, 422: {}, 503: {}},
)
def organize_text(payload: OrganizeRequest, current_user: CurrentUser, session: DatabaseSession):
    lines = [line.model_dump() for line in payload.lines] if payload.lines else None
    user_state, count = adapter_service.user_state_for_suggestion(session, current_user.id)
    try:
        result = organizer.organize(payload.text, lines, user_state, count)
    except organizer.OrganizeError as error:
        return JSONResponse(status_code=error.status, content={"detail": error.detail, "code": error.code}, headers=NO_STORE)
    return JSONResponse(content=OrganizeRead(**result).model_dump(mode="json"), headers=NO_STORE)
