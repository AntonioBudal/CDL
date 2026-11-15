"""F0.12.03 (spec 116): importar a biblioteca de outro serviço (Goodreads, StoryGraph, BookWyrm)."""
from __future__ import annotations

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import TypeAdapter, ValidationError

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.library_import import LibraryChoice, LibraryImportResponse, LibraryPreviewResponse
from app.services.library_import import MAX_BYTES
from app.services.library_import.service import build_preview, parse_upload, run_import

router = APIRouter(prefix="/books/import-library", tags=["Importar biblioteca"])
_CHOICES = TypeAdapter(list[LibraryChoice])


async def _read(upload: UploadFile) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while chunk := await upload.read(1024 * 1024):
        size += len(chunk)
        if size > MAX_BYTES:
            raise HTTPException(status_code=413, detail="O arquivo passa de 10 MB.")
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/preview", response_model=LibraryPreviewResponse, summary="Prévia da biblioteca de outro serviço")
async def library_preview(session: DatabaseSession, current_user: CurrentUser, file: UploadFile = File(...)):
    """Só lê o arquivo: nada é gravado e o arquivo não fica no disco."""
    return build_preview(session, current_user.id, parse_upload(await _read(file)))


@router.post("/import", response_model=LibraryImportResponse, summary="Importar a biblioteca de outro serviço")
async def library_import(
    session: DatabaseSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    choices: str = Form(..., description="JSON: lista de {key, action: create|update|skip}"),
    with_reviews: bool = Form(False),
):
    try:
        parsed_choices = _CHOICES.validate_python(json.loads(choices))
    except (ValueError, ValidationError) as exc:
        raise HTTPException(status_code=422, detail="Escolhas inválidas para a importação.") from exc
    parsed = parse_upload(await _read(file))
    return run_import(session, current_user.id, parsed, parsed_choices, with_reviews)
