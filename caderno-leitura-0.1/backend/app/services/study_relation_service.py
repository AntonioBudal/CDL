"""Serviço para gestão de relações semânticas e backlinks entre estudos."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.models import Book, Chapter, Study, StudyRelation
from app.schemas.study_relation import (
    BookCanvasRelationItem,
    CandidateStudyItem,
    ConnectedStudySummary,
    StudyRelationCreate,
    StudyRelationItem,
    StudyRelationsResponse,
    StudyRelationUpdate,
)
from app.services.persistence import commit_changes

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _build_connected_study_summary(study: Study) -> ConnectedStudySummary:
    """Extrai metadados do estudo conectado com livro e capítulo."""
    chapter = study.chapter
    book = chapter.book if chapter else None
    return ConnectedStudySummary(
        id=study.id,
        title=study.title,
        book_id=book.id if book else 0,
        book_title=book.title if book else "",
        chapter_id=chapter.id if chapter else 0,
        chapter_title=chapter.name if chapter else "",
    )


def _build_relation_item(relation: StudyRelation, connected_study: Study) -> StudyRelationItem:
    return StudyRelationItem(
        id=relation.id,
        source_study_id=relation.source_study_id,
        target_study_id=relation.target_study_id,
        relation_type=relation.relation_type,  # type: ignore[arg-type]
        description=relation.description,
        created_at=relation.created_at,
        connected_study=_build_connected_study_summary(connected_study),
    )


def get_study_relations(session: Session, study_id: int, user_id: str | None = None) -> StudyRelationsResponse:
    """Retorna todas as relações de saída e backlinks recebidos de um estudo ativo."""
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None or (user_id and study.user_id != user_id):
        raise HTTPException(status_code=404, detail=f"Estudo #{study_id} não encontrado ou está na lixeira.")

    # Relações de saída (onde o estudo atual é a origem)
    stmt_out = (
        select(StudyRelation)
        .join(Study, StudyRelation.target_study_id == Study.id)
        .options(
            selectinload(StudyRelation.target_study).selectinload(Study.chapter).selectinload(Chapter.book)
        )
        .where(
            StudyRelation.source_study_id == study_id,
            Study.deleted_at.is_(None),
        )
    )
    if user_id:
        stmt_out = stmt_out.where(StudyRelation.user_id == user_id)

    stmt_out = stmt_out.order_by(StudyRelation.created_at.desc())
    outbound_relations = session.scalars(stmt_out).all()
    outbound_items = [
        _build_relation_item(rel, rel.target_study)
        for rel in outbound_relations
        if rel.target_study is not None and rel.target_study.deleted_at is None
    ]

    # Relações de entrada / backlinks (onde o estudo atual é o destino)
    stmt_in = (
        select(StudyRelation)
        .join(Study, StudyRelation.source_study_id == Study.id)
        .options(
            selectinload(StudyRelation.source_study).selectinload(Study.chapter).selectinload(Chapter.book)
        )
        .where(
            StudyRelation.target_study_id == study_id,
            Study.deleted_at.is_(None),
        )
    )
    if user_id:
        stmt_in = stmt_in.where(StudyRelation.user_id == user_id)

    stmt_in = stmt_in.order_by(StudyRelation.created_at.desc())
    inbound_relations = session.scalars(stmt_in).all()
    inbound_items = [
        _build_relation_item(rel, rel.source_study)
        for rel in inbound_relations
        if rel.source_study is not None and rel.source_study.deleted_at is None
    ]

    return StudyRelationsResponse(
        study_id=study_id,
        outbound=outbound_items,
        inbound=inbound_items,
    )


def create_study_relation(
    session: Session,
    source_study_id: int,
    payload: StudyRelationCreate,
    user_id: str | None = None,
) -> StudyRelationItem:
    """Cria uma nova relação direcionada entre dois estudos validando titularidade."""
    if source_study_id == payload.target_study_id:
        raise HTTPException(
            status_code=400,
            detail="Um estudo não pode ser relacionado a si mesmo.",
        )

    source_study = session.get(Study, source_study_id)
    if source_study is None or source_study.deleted_at is not None or (user_id and source_study.user_id != user_id):
        raise HTTPException(
            status_code=404,
            detail=f"Estudo de origem #{source_study_id} não encontrado ou está na lixeira.",
        )

    stmt_target = (
        select(Study)
        .options(selectinload(Study.chapter).selectinload(Chapter.book))
        .where(Study.id == payload.target_study_id, Study.deleted_at.is_(None))
    )
    target_study = session.scalars(stmt_target).first()
    if target_study is None or (user_id and target_study.user_id != user_id):
        raise HTTPException(
            status_code=404,
            detail=f"Estudo de destino #{payload.target_study_id} não encontrado ou está na lixeira.",
        )

    # Verificar duplicidade exata
    stmt_dup = select(StudyRelation).where(
        StudyRelation.source_study_id == source_study_id,
        StudyRelation.target_study_id == payload.target_study_id,
        StudyRelation.relation_type == payload.relation_type,
    )
    if session.scalars(stmt_dup).first() is not None:
        raise HTTPException(
            status_code=400,
            detail="Esta relação semântica já existe entre os dois estudos.",
        )

    effective_user_id = user_id or source_study.user_id
    relation = StudyRelation(
        user_id=effective_user_id,
        source_study_id=source_study_id,
        target_study_id=payload.target_study_id,
        relation_type=payload.relation_type,
        description=payload.description or "",
    )
    session.add(relation)
    commit_changes(session)
    session.refresh(relation)

    return _build_relation_item(relation, target_study)


def update_study_relation(
    session: Session,
    relation_id: int,
    payload: StudyRelationUpdate,
    user_id: str | None = None,
) -> StudyRelationItem:
    """Atualiza a anotação descritiva ou o tipo de uma relação existente."""
    stmt = (
        select(StudyRelation)
        .options(selectinload(StudyRelation.target_study).selectinload(Study.chapter).selectinload(Chapter.book))
        .where(StudyRelation.id == relation_id)
    )
    if user_id:
        stmt = stmt.where(StudyRelation.user_id == user_id)

    relation = session.scalars(stmt).first()
    if relation is None:
        raise HTTPException(status_code=404, detail="Relação não encontrada.")

    # Se mudar o tipo de relação, verificar se não gerará duplicata
    if payload.relation_type is not None and payload.relation_type != relation.relation_type:
        stmt_dup = select(StudyRelation).where(
            StudyRelation.source_study_id == relation.source_study_id,
            StudyRelation.target_study_id == relation.target_study_id,
            StudyRelation.relation_type == payload.relation_type,
            StudyRelation.id != relation_id,
        )
        if session.scalars(stmt_dup).first() is not None:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma relação desse tipo entre os mesmos estudos.",
            )
        relation.relation_type = payload.relation_type

    if payload.description is not None:
        relation.description = payload.description

    commit_changes(session)
    session.refresh(relation)
    return _build_relation_item(relation, relation.target_study)


def delete_study_relation(session: Session, relation_id: int, user_id: str | None = None) -> None:
    """Remove individualmente uma relação semântica."""
    relation = session.get(StudyRelation, relation_id)
    if relation is None or (user_id and relation.user_id != user_id):
        raise HTTPException(status_code=404, detail="Relação não encontrada.")

    session.delete(relation)
    commit_changes(session)


def search_candidate_studies(
    session: Session,
    exclude_study_id: int,
    query: str = "",
    limit: int = 20,
    user_id: str | None = None,
) -> list[CandidateStudyItem]:
    """Busca incremental de estudos candidatos em todo o acervo do usuário ativo."""
    clean_limit = min(max(1, limit), 50)

    stmt = (
        select(Study)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .options(selectinload(Study.chapter).selectinload(Chapter.book))
        .where(
            Study.deleted_at.is_(None),
            Study.id != exclude_study_id,
        )
    )
    if user_id:
        stmt = stmt.where(Study.user_id == user_id)

    clean_query = query.strip()
    if clean_query:
        like_pattern = f"%{clean_query}%"
        stmt = stmt.where(
            or_(
                Study.title.ilike(like_pattern),
                Chapter.name.ilike(like_pattern),
                Book.title.ilike(like_pattern),
            )
        )

    stmt = stmt.order_by(Study.title.asc()).limit(clean_limit)
    candidates = session.scalars(stmt).all()

    items: list[CandidateStudyItem] = []
    for study in candidates:
        chapter = study.chapter
        book = chapter.book if chapter else None
        items.append(
            CandidateStudyItem(
                id=study.id,
                title=study.title,
                book_id=book.id if book else 0,
                book_title=book.title if book else "",
                chapter_id=chapter.id if chapter else 0,
                chapter_title=chapter.name if chapter else "",
            )
        )

    return items


def get_book_canvas_relations(session: Session, book_id: int, user_id: str | None = None) -> list[BookCanvasRelationItem]:
    """Retorna todas as relações semânticas ativas entre estudos de um determinado livro."""
    stmt_study_ids = (
        select(Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .where(
            Chapter.book_id == book_id,
            Study.deleted_at.is_(None),
        )
    )
    if user_id:
        stmt_study_ids = stmt_study_ids.where(Study.user_id == user_id)

    book_study_ids = set(session.scalars(stmt_study_ids).all())

    if not book_study_ids:
        return []

    stmt_relations = select(StudyRelation).where(
        StudyRelation.source_study_id.in_(book_study_ids),
        StudyRelation.target_study_id.in_(book_study_ids),
    )
    if user_id:
        stmt_relations = stmt_relations.where(StudyRelation.user_id == user_id)

    relations = session.scalars(stmt_relations).all()

    return [
        BookCanvasRelationItem(
            id=rel.id,
            source_study_id=rel.source_study_id,
            target_study_id=rel.target_study_id,
            relation_type=rel.relation_type,  # type: ignore[arg-type]
            description=rel.description,
        )
        for rel in relations
    ]
