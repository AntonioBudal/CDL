from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import DatabaseSession, Identifier
from app.models import Chapter, Study
from app.schemas.study import ANALYSIS_FIELDS, ANALYSIS_REQUIRED_MESSAGE, StudyCreate, StudyPatch, StudyRead, StudySummary
from app.services.persistence import commit_changes, get_or_404

router = APIRouter(tags=["Estudos"])


@router.get("/chapters/{chapter_id}/studies", response_model=list[StudySummary], summary="Listar estudos de um capítulo")
def list_studies(chapter_id: Identifier, session: DatabaseSession):
    get_or_404(session, Chapter, chapter_id, "Capítulo")
    # A listagem nao precisa carregar as analises e a resposta original completas.
    statement = select(
        Study.id, Study.chapter_id, Study.title, Study.location, Study.created_at, Study.updated_at
    ).where(Study.chapter_id == chapter_id).order_by(Study.id)
    return session.execute(statement).mappings().all()


@router.post("/studies", response_model=StudyRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar estudo")
def create_study(payload: StudyCreate, session: DatabaseSession):
    chapter = get_or_404(session, Chapter, payload.chapter_id, "Capítulo")
    values = payload.model_dump()
    if not values["title"]:
        location = payload.location.strip()
        values["title"] = f"{chapter.name} — {location}" if location else chapter.name
    study = Study(**values)
    session.add(study)
    commit_changes(session)
    return study


@router.get("/studies/{study_id}", response_model=StudyRead, summary="Consultar estudo completo")
def get_study(study_id: Identifier, session: DatabaseSession):
    return get_or_404(session, Study, study_id, "Estudo")


@router.patch("/studies/{study_id}", response_model=StudyRead, summary="Editar campos de um estudo")
def update_study(study_id: Identifier, payload: StudyPatch, session: DatabaseSession):
    study = get_or_404(session, Study, study_id, "Estudo")
    changes = payload.model_dump(exclude_unset=True)
    candidate = {name: changes.get(name, getattr(study, name)) for name in ANALYSIS_FIELDS}
    if not any(value.strip() for value in candidate.values()):
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body"], "msg": ANALYSIS_REQUIRED_MESSAGE, "type": "value_error"}],
        )
    for name, value in changes.items():
        setattr(study, name, value)
    commit_changes(session)
    return study
