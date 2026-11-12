"""F0.11.06 (spec 108): léxico de conceitos (derivado das seções Conceitos e das menções [[conceito:…]])."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.concept import (
    ConceptCandidate,
    ConceptDetail,
    ConceptListResponse,
    ConceptOccurrenceRead,
    ConceptSummary,
)
from app.services.concept_lexicon import ConceptEntry, build_lexicon, get_concept, list_concepts
from app.services.concept_review_service import fragile_keys

router = APIRouter(prefix="/concepts", tags=["Léxico de conceitos"])


def _summary(entry: ConceptEntry, weak: set[str] | None = None) -> ConceptSummary:
    return ConceptSummary(
        key=entry.key,
        term=entry.term,
        definitions=len(entry.definitions),
        mentions=len(entry.mentions),
        books=len(entry.books),
        fragile=bool(weak and entry.key in weak),
    )


@router.get("", response_model=ConceptListResponse, summary="Listar o léxico de conceitos")
def list_concepts_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str = Query(default="", max_length=200),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=200),
):
    entries = list_concepts(session, current_user.id, q)
    start = (page - 1) * per_page
    weak = fragile_keys(session, current_user.id, build_lexicon(session, current_user.id))
    return ConceptListResponse(
        items=[_summary(e, weak) for e in entries[start:start + per_page]],
        total=len(entries),
        page=page,
        per_page=per_page,
    )


@router.get("/candidates", response_model=list[ConceptCandidate], summary="Conceitos para o autocompletar do editor")
def concept_candidates_endpoint(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str = Query(default="", max_length=200),
    limit: int = Query(default=8, ge=1, le=30),
):
    entries = list_concepts(session, current_user.id, q)[:limit]
    return [ConceptCandidate(key=e.key, term=e.term, definitions=len(e.definitions)) for e in entries]


@router.get("/{key}", response_model=ConceptDetail, summary="Definições e menções de um conceito")
def concept_detail_endpoint(key: str, session: DatabaseSession, current_user: CurrentUser):
    entry = get_concept(session, current_user.id, key)
    if entry is None:
        raise HTTPException(status_code=404, detail="Conceito não encontrado no seu léxico.")
    return ConceptDetail(
        key=entry.key,
        term=entry.term,
        fragile=entry.key in fragile_keys(session, current_user.id, {entry.key: entry}),
        definitions=[ConceptOccurrenceRead(**o.__dict__) for o in entry.definitions],
        mentions=[ConceptOccurrenceRead(**o.__dict__) for o in entry.mentions],
    )
