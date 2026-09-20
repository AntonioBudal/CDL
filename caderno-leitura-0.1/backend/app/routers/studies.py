from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.dependencies import DatabaseSession, Identifier
from app.models import Chapter, Study
from app.schemas.export import ExportFormat, ExportOptions
from app.schemas.study import (
    ANALYSIS_FIELDS,
    ANALYSIS_REQUIRED_MESSAGE,
    StudyCreate,
    StudyMoveRequest,
    StudyPatch,
    StudyRead,
    StudySummary,
)
from app.schemas.study_grouping import StudyStatusResponse, StudyStatusUpdate
from app.schemas.trash import TrashActionResponse
from app.services.export_service import generate_study_export
from app.services.persistence import check_optimistic_lock, commit_changes, get_or_404
from app.services.study_service import move_study, update_study_status
from app.services.trash_service import permanent_delete_study, restore_study, trash_study

router = APIRouter(tags=["Estudos"])


@router.get("/chapters/{chapter_id}/studies", response_model=list[StudySummary], summary="Listar estudos de um capítulo")
def list_studies(chapter_id: Identifier, session: DatabaseSession):
    chapter = get_or_404(session, Chapter, chapter_id, "Capítulo")
    if chapter.book and chapter.book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Capítulo não encontrado.")
    statement = select(
        Study.id,
        Study.chapter_id,
        Study.parent_study_id,
        Study.position,
        Study.reading_status,
        Study.title,
        Study.location,
        Study.created_at,
        Study.updated_at,
        Study.deleted_at,
    ).where(Study.chapter_id == chapter_id, Study.deleted_at.is_(None)).order_by(
        Study.parent_study_id.nullsfirst(), Study.position, Study.id
    )
    return session.execute(statement).mappings().all()


@router.post("/studies/{study_id}/move", response_model=list[StudySummary], summary="Mover e reposicionar estudo na hierarquia")
def move_study_endpoint(study_id: Identifier, payload: StudyMoveRequest, session: DatabaseSession):
    return move_study(session, study_id, payload)


@router.patch(
    "/studies/{study_id}/status",
    response_model=StudyStatusResponse,
    summary="Atualizar status de maturação/leitura de um estudo",
)
def update_study_status_endpoint(
    study_id: Identifier,
    payload: StudyStatusUpdate,
    session: DatabaseSession,
):
    return update_study_status(session, study_id, payload)



@router.post("/studies", response_model=StudyRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar estudo")
def create_study(payload: StudyCreate, session: DatabaseSession):
    chapter = get_or_404(session, Chapter, payload.chapter_id, "Capítulo")
    if chapter.book and chapter.book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Não é possível adicionar estudos a um livro na lixeira.")
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
    study = get_or_404(session, Study, study_id, "Estudo")
    if study.deleted_at is not None or (study.chapter and study.chapter.book and study.chapter.book.deleted_at is not None):
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    return study


@router.post("/studies/{study_id}/trash", response_model=StudyRead, summary="Mover estudo para a lixeira")
def trash_study_endpoint(study_id: Identifier, session: DatabaseSession):
    return trash_study(session, study_id)


@router.patch("/studies/{study_id}", response_model=StudyRead, summary="Editar campos de um estudo")
def update_study(study_id: Identifier, payload: StudyPatch, session: DatabaseSession):
    study = get_or_404(session, Study, study_id, "Estudo")
    if study.deleted_at is not None or (study.chapter and study.chapter.book and study.chapter.book.deleted_at is not None):
        raise HTTPException(status_code=404, detail="Não é possível editar um estudo que está na lixeira.")
    check_optimistic_lock(study.updated_at, payload.expected_updated_at, "Estudo")
    changes = payload.model_dump(exclude_unset=True, exclude={"expected_updated_at"})
    candidate = {name: changes.get(name, getattr(study, name)) for name in ANALYSIS_FIELDS}
    if not any(value.strip() for value in candidate.values()):
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body"], "msg": ANALYSIS_REQUIRED_MESSAGE, "type": "value_error"}],
        )
    for name, value in changes.items():
        setattr(study, name, value)
    commit_changes(session)
    session.refresh(study)
    return study


@router.post("/studies/{study_id}/restore", response_model=TrashActionResponse, summary="Restaurar estudo da lixeira")
def restore_study_endpoint(study_id: Identifier, session: DatabaseSession):
    study, book_restored = restore_study(session, study_id)
    return TrashActionResponse(
        id=study.id,
        title=study.title,
        deleted_at=study.deleted_at,
        book_restored=book_restored,
    )


@router.delete("/studies/{study_id}/permanent", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir estudo permanentemente")
def permanent_delete_study_endpoint(study_id: Identifier, session: DatabaseSession):
    permanent_delete_study(session, study_id)


@router.get("/studies/{study_id}/export", summary="Exportar estudo individual")
def export_study(
    study_id: Identifier,
    session: DatabaseSession,
    format: ExportFormat = ExportFormat.MARKDOWN,
    include_notes: bool = True,
    include_sections: bool = True,
    include_source: bool = False,
    include_metadata: bool = True,
):
    options = ExportOptions(
        format=format,
        include_notes=include_notes,
        include_sections=include_sections,
        include_source=include_source,
        include_metadata=include_metadata,
    )
    content, filename, media_type = generate_study_export(session, study_id, options)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return Response(content=content.encode("utf-8"), media_type=media_type, headers=headers)

