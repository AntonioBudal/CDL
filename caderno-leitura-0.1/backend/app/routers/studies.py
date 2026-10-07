from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import func, select

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.models import Book, Chapter, Study, StudyHighlight, StudyRelation, User
from app.schemas.export import ExportFormat, ExportOptions, ExportType
from app.schemas.sharing import (
    GrantPermissionRequest,
    ResourceOwnerSummary,
    ResourcePermissionItem,
    ResourcePermissionsRead,
    VisibilityUpdateRequest,
)
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
from app.services.persistence import (
    check_optimistic_lock,
    check_optimistic_version,
    commit_changes,
    get_or_404,
    get_user_resource_or_404,
)
from app.services.sharing_service import (
    can_read_book,
    can_read_study,
    get_study_permissions,
    grant_permission,
    resolve_effective_visibility,
    revoke_permission,
    update_study_visibility,
)
from app.services.study_mention_service import sync_study_mentions
from app.services.study_service import move_study, update_study_status
from app.services.study_version_service import record_study_version_on_change
from app.services.trash_service import permanent_delete_study, restore_study, trash_study

router = APIRouter(tags=["Estudos"])



def check_study_mutation_permission(session: DatabaseSession, study_id: int, user_id: str) -> Study:
    """Verifica permissão de mutação sobre o estudo.

    Se o solicitante for o proprietário: retorna o estudo para que a operação prossiga.
    Se o solicitante não for o proprietário:
    - Retorna 403 se o usuário tem permissão de leitura sobre o estudo (somente-leitura).
    - Retorna 404 se não tem acesso algum ou recurso inexistente (anti-enumeração).
    """
    study = session.get(Study, study_id)
    if study is None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    if study.user_id == user_id:
        return study
    if study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    if can_read_study(session, user_id, study):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso somente leitura. Apenas o proprietário pode alterar este estudo.",
        )
    raise HTTPException(status_code=404, detail="Estudo não encontrado.")


def _populate_study_summaries(
    session: DatabaseSession,
    studies: list[Study],
    book: Book,
    current_user_id: str,
) -> list[StudySummary]:
    if not studies:
        return []

    study_ids = [s.id for s in studies]

    # Agregação em lote de destaques
    hl_stmt = (
        select(StudyHighlight.study_id, func.count(StudyHighlight.id))
        .where(StudyHighlight.study_id.in_(study_ids))
        .group_by(StudyHighlight.study_id)
    )
    hl_counts = dict(session.execute(hl_stmt).all())

    # Agregação em lote de relações (outbound e inbound)
    rel_out_stmt = (
        select(StudyRelation.source_study_id, func.count(StudyRelation.id))
        .where(StudyRelation.source_study_id.in_(study_ids))
        .group_by(StudyRelation.source_study_id)
    )
    rel_out_counts = dict(session.execute(rel_out_stmt).all())

    rel_in_stmt = (
        select(StudyRelation.target_study_id, func.count(StudyRelation.id))
        .where(StudyRelation.target_study_id.in_(study_ids))
        .group_by(StudyRelation.target_study_id)
    )
    rel_in_counts = dict(session.execute(rel_in_stmt).all())

    result = []
    for s in studies:
        sr = StudySummary.model_validate(s)
        sr.book_id = book.id
        sr.effective_visibility = resolve_effective_visibility(s, book)
        sr.can_edit = (s.user_id == current_user_id)

        # Prévia tipográfica: prioriza summary, fallback para explanation, truncada em até 240 caracteres
        raw_text = (s.summary or "").strip()
        if not raw_text:
            raw_text = (s.explanation or "").strip()
        sr.summary_preview = raw_text[:240]

        sr.highlights_count = hl_counts.get(s.id, 0)
        sr.relations_count = rel_out_counts.get(s.id, 0) + rel_in_counts.get(s.id, 0)

        # Flags booleanas de completude analítica (F 0.7.5)
        sr.has_summary = bool(s.summary and s.summary.strip())
        sr.has_explanation = bool(s.explanation and s.explanation.strip())
        sr.has_concepts = bool(s.concepts and s.concepts.strip())
        sr.has_references = bool(s.references and s.references.strip())

        result.append(sr)

    return result


@router.get("/chapters/{chapter_id}/studies", response_model=list[StudySummary], summary="Listar estudos de um capítulo")
def list_studies(chapter_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    chapter = get_or_404(session, Chapter, chapter_id, "Capítulo")
    book = chapter.book
    if book is None or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Capítulo não encontrado.")

    if book.user_id == current_user.id:
        statement = select(Study).where(
            Study.chapter_id == chapter_id,
            Study.deleted_at.is_(None),
            Study.user_id == current_user.id,
        ).order_by(Study.parent_study_id.nullsfirst(), Study.position, Study.id)
        studies = list(session.scalars(statement).all())
        return _populate_study_summaries(session, studies, book, current_user.id)

    if not can_read_book(session, current_user.id, book):
        raise HTTPException(status_code=404, detail="Capítulo não encontrado.")

    statement = select(Study).where(
        Study.chapter_id == chapter_id,
        Study.deleted_at.is_(None),
    ).order_by(Study.parent_study_id.nullsfirst(), Study.position, Study.id)
    studies = list(session.scalars(statement).all())
    visible_studies = [s for s in studies if can_read_study(session, current_user.id, s, book=book)]
    return _populate_study_summaries(session, visible_studies, book, current_user.id)


@router.post("/studies/{study_id}/move", response_model=list[StudySummary], summary="Mover e reposicionar estudo na hierarquia")
def move_study_endpoint(
    study_id: Identifier,
    payload: StudyMoveRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    check_study_mutation_permission(session, study_id, current_user.id)
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
    current_user: CurrentUser,
):
    check_study_mutation_permission(session, study_id, current_user.id)
    return update_study_status(session, study_id, payload)


@router.post("/studies", response_model=StudyRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar estudo")
def create_study(payload: StudyCreate, session: DatabaseSession, current_user: CurrentUser):
    chapter = get_or_404(session, Chapter, payload.chapter_id, "Capítulo")
    if chapter.book:
        if chapter.book.user_id != current_user.id or chapter.book.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Não é possível adicionar estudos a um livro inexistente ou na lixeira.")
    values = payload.model_dump()
    if not values["title"]:
        location = payload.location.strip()
        values["title"] = f"{chapter.name} — {location}" if location else chapter.name
    study = Study(**values, user_id=current_user.id)
    session.add(study)
    session.flush()
    sync_study_mentions(session, study, current_user.id)
    commit_changes(session)
    session.refresh(study)
    study_read = StudyRead.model_validate(study)
    study_read.can_edit = True
    return study_read


@router.get("/studies/{study_id}", response_model=StudyRead, summary="Consultar estudo completo")
def get_study(study_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")

    book = None
    if study.chapter:
        book = study.chapter.book
        if book and book.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    elif study.chapter_id:
        chapter = session.get(Chapter, study.chapter_id)
        if chapter and chapter.book:
            book = chapter.book
            if book.deleted_at is not None:
                raise HTTPException(status_code=404, detail="Estudo não encontrado.")

    if not can_read_study(session, current_user.id, study, book=book):
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")

    can_edit = (study.user_id == current_user.id)
    study_read = StudyRead.model_validate(study)
    study_read.can_edit = can_edit

    if not can_edit:
        owner_user = session.get(User, study.user_id)
        if owner_user:
            avatar_url = owner_user.profile.avatar_url if getattr(owner_user, "profile", None) else None
            study_read.owner = ResourceOwnerSummary(
                id=owner_user.id,
                username=owner_user.username,
                display_name=owner_user.display_name,
                avatar_url=avatar_url,
            )

    return study_read


@router.put("/studies/{study_id}/visibility", response_model=ResourcePermissionsRead, summary="Alterar visibilidade do estudo")
def set_study_visibility(
    study_id: Identifier,
    payload: VisibilityUpdateRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    update_study_visibility(session, current_user.id, study_id, payload.visibility)
    commit_changes(session)
    return get_study_permissions(session, current_user.id, study_id)


@router.get("/studies/{study_id}/permissions", response_model=ResourcePermissionsRead, summary="Consultar permissões do estudo")
def get_study_permissions_endpoint(
    study_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    return get_study_permissions(session, current_user.id, study_id)


@router.post(
    "/studies/{study_id}/permissions",
    response_model=ResourcePermissionItem,
    status_code=status.HTTP_201_CREATED,
    summary="Conceder permissão nominal de leitura para o estudo",
)
def grant_study_permission_endpoint(
    study_id: Identifier,
    payload: GrantPermissionRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    perm = grant_permission(
        session=session,
        owner_id=current_user.id,
        resource_type="study",
        resource_id=study_id,
        target_username=payload.username,
    )
    commit_changes(session)
    target_user = session.get(User, perm.granted_to_user_id)
    avatar_url = target_user.profile.avatar_url if getattr(target_user, "profile", None) else None
    return ResourcePermissionItem(
        user_id=target_user.id,
        username=target_user.username,
        display_name=target_user.display_name,
        avatar_url=avatar_url,
        created_at=perm.created_at,
    )


@router.delete("/studies/{study_id}/permissions/{user_id}", summary="Revogar permissão nominal de leitura do estudo")
def revoke_study_permission_endpoint(
    study_id: Identifier,
    user_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    revoke_permission(
        session=session,
        owner_id=current_user.id,
        resource_type="study",
        resource_id=study_id,
        granted_to_user_id=user_id,
    )
    commit_changes(session)
    return {"ok": True}


@router.post("/studies/{study_id}/trash", response_model=StudyRead, summary="Mover estudo para a lixeira")
def trash_study_endpoint(study_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    check_study_mutation_permission(session, study_id, current_user.id)
    return trash_study(session, study_id, user_id=current_user.id)


@router.patch("/studies/{study_id}", response_model=StudyRead, summary="Editar campos de um estudo")
def update_study(study_id: Identifier, payload: StudyPatch, session: DatabaseSession, current_user: CurrentUser):
    study = check_study_mutation_permission(session, study_id, current_user.id)
    if study.chapter and study.chapter.book and study.chapter.book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Não é possível editar um estudo que está na lixeira.")

    server_data = StudyRead.model_validate(study).model_dump(mode="json")
    if payload.expected_version is not None:
        check_optimistic_version(
            current_version=study.version,
            expected_version=payload.expected_version,
            entity_id=study.id,
            entity_type="study",
            server_updated_at=study.updated_at,
            server_data=server_data,
            label="Estudo",
        )
    elif payload.expected_updated_at is not None:
        check_optimistic_lock(
            study.updated_at,
            payload.expected_updated_at,
            label="Estudo",
            entity_id=study.id,
            entity_type="study",
            server_version=study.version,
            server_data=server_data,
        )

    changes = payload.model_dump(exclude_unset=True, exclude={"expected_updated_at", "expected_version"})
    candidate = {name: changes.get(name, getattr(study, name)) for name in ANALYSIS_FIELDS}
    if not any(value.strip() for value in candidate.values()):
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body"], "msg": ANALYSIS_REQUIRED_MESSAGE, "type": "value_error"}],
        )

    # Gravar versão de histórico automaticamente ao detectar alterações
    record_study_version_on_change(session, study, changes, current_user.id)

    for name, value in changes.items():
        setattr(study, name, value)
    study.version += 1
    sync_study_mentions(session, study, current_user.id)

    commit_changes(session)
    session.refresh(study)
    study_read = StudyRead.model_validate(study)
    study_read.can_edit = True
    return study_read


@router.post("/studies/{study_id}/restore", response_model=TrashActionResponse, summary="Restaurar estudo da lixeira")
def restore_study_endpoint(study_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    study, book_restored = restore_study(session, study_id, user_id=current_user.id)
    return TrashActionResponse(
        id=study.id,
        title=study.title,
        deleted_at=study.deleted_at,
        book_restored=book_restored,
    )


@router.delete("/studies/{study_id}/permanent", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir estudo permanentemente")
def permanent_delete_study_endpoint(study_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    permanent_delete_study(session, study_id, user_id=current_user.id)


@router.get("/studies/{study_id}/export", summary="Exportar estudo individual")
def export_study(
    study_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
    format: ExportFormat = ExportFormat.MARKDOWN,
    export_type: ExportType = ExportType.FULL,
    include_highlights: bool = True,
    exercise_mode: bool = False,
    include_notes: bool = True,
    include_sections: bool = True,
    include_source: bool = False,
    include_metadata: bool = True,
):
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    if not can_read_study(session, current_user.id, study):
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")

    options = ExportOptions(
        format=format,
        export_type=export_type,
        include_highlights=include_highlights,
        exercise_mode=exercise_mode,
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

