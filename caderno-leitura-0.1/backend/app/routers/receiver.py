"""F0.11.09 (spec 111): receptor de destaques compatível com a API v2 do Readwise (usado pelo Readest).

Autentica **só** pelo token de recepção (``Authorization: Token <token>``); cookie nenhum vale aqui. Por isso o
prefixo ``/api/receptor/`` fica fora da conferência de origem. Logs: só contagens, nunca token ou texto.
"""
from __future__ import annotations

import json
import logging
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from pydantic import ValidationError

from app.dependencies import DatabaseSession
from app.models.user import User
from app.schemas.receiver import MAX_HIGHLIGHTS, ReadwiseBookOut, ReadwiseHighlightsIn
from app.services import receiver_tokens
from app.services.ereader_import.readwise import parse_readwise_highlights
from app.services.ereader_import.service import receive_parsed

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/receptor/readwise/v2", tags=["Receptor de destaques"])

MAX_BODY_BYTES = 25 * 1024 * 1024
UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token de recepção inválido.",
    headers={"WWW-Authenticate": "Token"},
)


def _user(session: DatabaseSession, authorization: str | None) -> User:
    user = receiver_tokens.authenticate(session, receiver_tokens.parse_authorization(authorization))
    if user is None:
        raise UNAUTHORIZED
    return user


@router.get("/auth", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
@router.get("/auth/", status_code=status.HTTP_204_NO_CONTENT, summary="Conferir o token (como o Readwise)")
def receiver_auth(
    session: DatabaseSession,
    authorization: Annotated[str | None, Header()] = None,
) -> Response:
    _user(session, authorization)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/highlights", response_model=list[ReadwiseBookOut], include_in_schema=False)
@router.post("/highlights/", response_model=list[ReadwiseBookOut], summary="Receber destaques (formato Readwise)")
async def receiver_highlights(
    request: Request,
    session: DatabaseSession,
    authorization: Annotated[str | None, Header()] = None,
) -> list[ReadwiseBookOut]:
    user = _user(session, authorization)
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Envio grande demais.")
    raw = await request.body()
    if len(raw) > MAX_BODY_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Envio grande demais.")
    try:
        payload = ReadwiseHighlightsIn.model_validate(json.loads(raw or b"{}"))
    except (ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Corpo inválido: esperado {\"highlights\": [...]} no formato do Readwise.",
        ) from exc
    if len(payload.highlights) > MAX_HIGHLIGHTS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Até {MAX_HIGHLIGHTS} destaques por envio.",
        )
    parsed = parse_readwise_highlights(payload.highlights)
    result = receive_parsed(session, user.id, parsed)
    logger.info(
        "Receptor: %d destaque(s) recebido(s), %d nova(s) captura(s), %d duplicada(s), %d pulado(s)",
        len(payload.highlights), result.created, result.duplicates, parsed.skipped,
    )
    authors = {str(i): b.author for i, b in enumerate(parsed.books)}
    return [
        ReadwiseBookOut(id=book.book_id, title=book.book_title, author=authors.get(book.key))
        for book in result.books
    ]
