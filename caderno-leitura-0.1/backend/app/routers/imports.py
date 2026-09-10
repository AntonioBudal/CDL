from fastapi import APIRouter, Response

from app.schemas.imports import ImportPreviewRead, ImportPreviewRequest, ImportWarningRead
from app.services.import_parser import parse_response

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
