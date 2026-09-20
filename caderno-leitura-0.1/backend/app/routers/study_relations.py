from fastapi import APIRouter, Query, status

from app.dependencies import DatabaseSession, Identifier
from app.schemas.study_relation import (
    BookCanvasRelationItem,
    CandidateStudyItem,
    StudyRelationCreate,
    StudyRelationItem,
    StudyRelationsResponse,
    StudyRelationUpdate,
)
from app.services.study_relation_service import (
    create_study_relation,
    delete_study_relation,
    get_book_canvas_relations,
    get_study_relations,
    search_candidate_studies,
    update_study_relation,
)

router = APIRouter(tags=["Relações entre Estudos"])


@router.get(
    "/studies/search-candidates",
    response_model=list[CandidateStudyItem],
    summary="Buscar estudos candidatos no acervo para criação de relação",
)
def search_candidates(
    session: DatabaseSession,
    exclude_study_id: int = Query(..., gt=0, description="ID do estudo de origem a ser excluído"),
    query: str = Query(default="", description="Termo de busca por título ou capítulo"),
    limit: int = Query(default=20, ge=1, le=50, description="Limite máximo de resultados"),
):
    return search_candidate_studies(
        session=session,
        exclude_study_id=exclude_study_id,
        query=query,
        limit=limit,
    )


@router.get(
    "/studies/{study_id}/relations",
    response_model=StudyRelationsResponse,
    summary="Listar relações de saída e backlinks recebidos de um estudo",
)
def get_relations(study_id: Identifier, session: DatabaseSession):
    return get_study_relations(session, study_id)


@router.post(
    "/studies/{study_id}/relations",
    response_model=StudyRelationItem,
    status_code=status.HTTP_201_CREATED,
    summary="Criar vínculo semântico a partir do estudo",
)
def create_relation(
    study_id: Identifier,
    payload: StudyRelationCreate,
    session: DatabaseSession,
):
    return create_study_relation(session, study_id, payload)


@router.patch(
    "/relations/{relation_id}",
    response_model=StudyRelationItem,
    summary="Atualizar anotação ou tipo de uma relação existente",
)
def update_relation(
    relation_id: Identifier,
    payload: StudyRelationUpdate,
    session: DatabaseSession,
):
    return update_study_relation(session, relation_id, payload)


@router.delete(
    "/relations/{relation_id}",
    summary="Remover individualmente uma relação semântica",
)
def delete_relation(relation_id: Identifier, session: DatabaseSession):
    delete_study_relation(session, relation_id)
    return {"success": True, "message": "Relação removida com sucesso."}


@router.get(
    "/books/{book_id}/relations",
    response_model=list[BookCanvasRelationItem],
    summary="Listar todas as relações entre estudos de um livro para o Canvas e Mapa",
)
def get_book_relations(book_id: Identifier, session: DatabaseSession):
    return get_book_canvas_relations(session, book_id)
