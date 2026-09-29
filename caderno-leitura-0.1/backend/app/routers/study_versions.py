from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.study import StudyRead
from app.schemas.study_version import (
    StudyDiffResponse,
    StudyVersionDetail,
    StudyVersionSummary,
)
from app.services.persistence import commit_changes
from app.services.study_version_service import (
    check_study_access,
    compute_study_diff,
    get_study_version_detail,
    get_study_versions,
    restore_study_version,
)

router = APIRouter(tags=["Histórico de Estudos"])


@router.get(
    "/studies/{study_id}/versions",
    response_model=list[StudyVersionSummary],
    summary="Listar histórico de versões de um estudo",
)
def list_versions_endpoint(
    study_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    check_study_access(session, study_id, current_user.id, for_mutation=False)
    return get_study_versions(session, study_id)


@router.get(
    "/studies/{study_id}/versions/{version_id}",
    response_model=StudyVersionDetail,
    summary="Inspecionar conteúdo integral de uma versão",
)
def get_version_detail_endpoint(
    study_id: Identifier,
    version_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    check_study_access(session, study_id, current_user.id, for_mutation=False)
    return get_study_version_detail(session, study_id, version_id)


@router.get(
    "/studies/{study_id}/versions/{version_id}/diff",
    response_model=StudyDiffResponse,
    summary="Calcular diff entre a versão selecionada e o estado atual (ou outra versão)",
)
def get_version_diff_endpoint(
    study_id: Identifier,
    version_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
    target_version_id: int | None = Query(default=None, description="ID da versão de destino para comparação"),
):
    check_study_access(session, study_id, current_user.id, for_mutation=False)
    return compute_study_diff(session, study_id, version_id, target_version_id=target_version_id)


@router.post(
    "/studies/{study_id}/versions/{version_id}/restore",
    response_model=StudyRead,
    summary="Restaurar versão anterior do estudo",
)
def restore_version_endpoint(
    study_id: Identifier,
    version_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    check_study_access(session, study_id, current_user.id, for_mutation=True)
    study = restore_study_version(session, study_id, version_id, current_user.id)
    commit_changes(session)
    session.refresh(study)
    study_read = StudyRead.model_validate(study)
    study_read.can_edit = True
    return study_read
