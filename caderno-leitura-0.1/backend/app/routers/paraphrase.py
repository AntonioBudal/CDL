"""F0.11.07 (spec 109): fontes para o validador de paráfrase (o cálculo é feito no navegador)."""
from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.paraphrase import ParaphraseSources
from app.services.paraphrase_sources import chapter_paraphrase_sources, study_paraphrase_sources

router = APIRouter(tags=["Validador de paráfrase"])


@router.get(
    "/studies/{study_id}/paraphrase-sources",
    response_model=ParaphraseSources,
    summary="Textos da fonte de um estudo para o validador de paráfrase",
)
def study_paraphrase_sources_endpoint(study_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return study_paraphrase_sources(session, current_user.id, study_id)


@router.get(
    "/chapters/{chapter_id}/paraphrase-sources",
    response_model=ParaphraseSources,
    summary="Texto do livro de um capítulo para o validador de paráfrase",
)
def chapter_paraphrase_sources_endpoint(chapter_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return chapter_paraphrase_sources(session, current_user.id, chapter_id)
