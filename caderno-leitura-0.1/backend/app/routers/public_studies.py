"""F0.12.02 (spec 115): publicar estudos na web e a página pública `/compartilhado/{id}` (HTML do servidor, sem login)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.services import public_study_service as svc

api_router = APIRouter(tags=["Estudos publicados na web"])
page_router = APIRouter(include_in_schema=False)


class PublicationRead(BaseModel):
    study_id: int
    published_at: datetime
    path: str


class PublishedStudyItem(BaseModel):
    study_id: int
    title: str
    book_title: str
    published_at: datetime
    path: str
    available: bool


@api_router.get("/studies/published", response_model=list[PublishedStudyItem], summary="Meus estudos publicados na web")
def list_my_published(session: DatabaseSession, current_user: CurrentUser):
    rows = svc.list_published(session, current_user.id)
    available = svc.available_published_ids(session, {study.id for study, _ in rows})
    return [
        PublishedStudyItem(
            study_id=study.id, title=study.title, book_title=book.title, published_at=study.published_at,
            path=svc.public_path(study.id), available=study.id in available,
        )
        for study, book in rows
    ]


@api_router.post("/studies/{study_id}/publication", response_model=PublicationRead, summary="Publicar o estudo na web")
def publish_study(study_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    study = svc.publish(session, current_user.id, study_id)
    return PublicationRead(study_id=study.id, published_at=study.published_at, path=svc.public_path(study.id))


@api_router.delete("/studies/{study_id}/publication", status_code=status.HTTP_204_NO_CONTENT, summary="Despublicar")
def unpublish_study(study_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    svc.unpublish(session, current_user.id, study_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


NOT_FOUND_PAGE = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Página não encontrada — Leitorum</title></head>
<body style="font:18px/1.6 Georgia,serif;max-width:40rem;margin:3rem auto;padding:0 1rem">
<h1>Página não encontrada</h1><p>Este estudo não está publicado ou não existe mais.</p></body></html>"""


@page_router.api_route("/compartilhado/{study_id}", methods=["GET", "HEAD"], response_class=HTMLResponse)
def public_study_page(study_id: int, session: DatabaseSession):
    try:
        study, chapter, book, author = svc.get_public_study(session, study_id)
    except HTTPException:  # 404 igual para todos os casos (não revela se existe)
        return HTMLResponse(NOT_FOUND_PAGE, status_code=404, headers={"X-Robots-Tag": "noindex", "Cache-Control": "no-store"})
    page = svc.render_page(session, study, chapter, book, author)
    # "no-cache" (e não max-age): o navegador sempre confere com o servidor, para despublicar tirar do ar na hora.
    return HTMLResponse(page.html, headers={"Cache-Control": "public, no-cache"})
