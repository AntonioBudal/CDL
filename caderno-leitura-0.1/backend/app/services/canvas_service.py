"""Serviço de layout espacial 2D isolado para estudos (Canvas)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select

from app.models import Book, CanvasFrame, Study, StudyCanvasNode
from app.schemas.study_canvas_node import CanvasBatchUpdateRequest, CanvasNodePatchRequest
from app.schemas.study_grouping import CanvasFrameCreate, CanvasFrameUpdate
from app.services.persistence import commit_changes, get_or_404, get_user_resource_or_404

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def get_book_canvas_nodes(session: Session, book_id: int, user_id: str | None = None) -> list[StudyCanvasNode]:
    """Retorna todas as coordenadas espaciais de estudos associados a um livro."""
    if user_id:
        get_user_resource_or_404(session, Book, book_id, user_id, "Livro")
    else:
        get_or_404(session, Book, book_id, "Livro")

    stmt = (
        select(StudyCanvasNode)
        .join(Study, StudyCanvasNode.study_id == Study.id)
        .where(
            StudyCanvasNode.book_id == book_id,
            Study.deleted_at.is_(None),
        )
    )
    if user_id:
        stmt = stmt.where(StudyCanvasNode.user_id == user_id)

    stmt = stmt.order_by(StudyCanvasNode.z_index.asc(), StudyCanvasNode.id.asc())
    return list(session.scalars(stmt).all())


def batch_upsert_canvas_nodes(
    session: Session,
    book_id: int,
    payload: CanvasBatchUpdateRequest,
    user_id: str | None = None,
) -> list[StudyCanvasNode]:
    """Atualiza ou insere em lote coordenadas espaciais de estudos com isolamento atômico."""
    if user_id:
        book = get_user_resource_or_404(session, Book, book_id, user_id, "Livro")
    else:
        book = get_or_404(session, Book, book_id, "Livro")

    effective_user_id = user_id or book.user_id

    # Mapear os nós já existentes no banco para este livro
    stmt_existing = select(StudyCanvasNode).where(StudyCanvasNode.book_id == book_id)
    if user_id:
        stmt_existing = stmt_existing.where(StudyCanvasNode.user_id == user_id)

    existing_map = {node.study_id: node for node in session.scalars(stmt_existing).all()}

    updated_nodes: list[StudyCanvasNode] = []

    for item in payload.nodes:
        if user_id:
            study = get_user_resource_or_404(session, Study, item.study_id, user_id, "Estudo")
        else:
            study = session.get(Study, item.study_id)
            if study is None or study.deleted_at is not None:
                raise HTTPException(status_code=404, detail=f"Estudo #{item.study_id} não encontrado ou está na lixeira.")

        # Validar pertencimento estrito à obra
        if study.chapter is None or study.chapter.book_id != book_id:
            raise HTTPException(
                status_code=400,
                detail=f"Estudo #{item.study_id} não pertence ao livro #{book_id}.",
            )

        if item.study_id in existing_map:
            node = existing_map[item.study_id]
            node.pos_x = item.pos_x
            node.pos_y = item.pos_y
            if item.width is not None:
                node.width = item.width
            if item.height is not None:
                node.height = item.height
            node.z_index = item.z_index
            if item.color_tag is not None:
                node.color_tag = item.color_tag
        else:
            node = StudyCanvasNode(
                user_id=effective_user_id,
                study_id=item.study_id,
                book_id=book_id,
                pos_x=item.pos_x,
                pos_y=item.pos_y,
                width=item.width,
                height=item.height,
                z_index=item.z_index,
                color_tag=item.color_tag,
            )
            session.add(node)
            existing_map[item.study_id] = node

        updated_nodes.append(node)

    commit_changes(session)

    # Retorna todos os nós válidos do livro
    return get_book_canvas_nodes(session, book_id, user_id=user_id)


def patch_study_canvas_node(
    session: Session,
    study_id: int,
    payload: CanvasNodePatchRequest,
    user_id: str | None = None,
) -> StudyCanvasNode:
    """Atualiza individualmente as coordenadas ou aparência de um estudo no Canvas."""
    if user_id:
        study = get_user_resource_or_404(session, Study, study_id, user_id, "Estudo")
    else:
        study = get_or_404(session, Study, study_id, "Estudo")

    if study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo está na lixeira.")

    if study.chapter is None:
        raise HTTPException(status_code=400, detail="Estudo sem capítulo associado.")

    book_id = study.chapter.book_id
    effective_user_id = user_id or study.user_id

    stmt = select(StudyCanvasNode).where(
        StudyCanvasNode.study_id == study_id,
        StudyCanvasNode.book_id == book_id,
    )
    if user_id:
        stmt = stmt.where(StudyCanvasNode.user_id == user_id)

    node = session.scalars(stmt).first()

    if node is None:
        node = StudyCanvasNode(
            user_id=effective_user_id,
            study_id=study_id,
            book_id=book_id,
            pos_x=payload.pos_x if payload.pos_x is not None else 0.0,
            pos_y=payload.pos_y if payload.pos_y is not None else 0.0,
            width=payload.width,
            height=payload.height,
            z_index=payload.z_index if payload.z_index is not None else 0,
            color_tag=payload.color_tag,
        )
        session.add(node)
    else:
        if payload.pos_x is not None:
            node.pos_x = payload.pos_x
        if payload.pos_y is not None:
            node.pos_y = payload.pos_y
        if payload.width is not None:
            node.width = payload.width
        if payload.height is not None:
            node.height = payload.height
        if payload.z_index is not None:
            node.z_index = payload.z_index
        if payload.color_tag is not None:
            node.color_tag = payload.color_tag

    commit_changes(session)
    return node


def get_book_canvas_frames(session: Session, book_id: int, user_id: str | None = None) -> list[CanvasFrame]:
    """Retorna todas as molduras espaciais associadas ao Canvas de um livro."""
    if user_id:
        get_user_resource_or_404(session, Book, book_id, user_id, "Livro")
    else:
        get_or_404(session, Book, book_id, "Livro")

    stmt = select(CanvasFrame).where(CanvasFrame.book_id == book_id)
    if user_id:
        stmt = stmt.where(CanvasFrame.user_id == user_id)

    stmt = stmt.order_by(CanvasFrame.created_at.asc(), CanvasFrame.id.asc())
    return list(session.scalars(stmt).all())


def create_canvas_frame(
    session: Session,
    book_id: int,
    payload: CanvasFrameCreate,
    user_id: str | None = None,
) -> CanvasFrame:
    """Cria uma nova moldura manual delimitadora no Canvas do livro."""
    if user_id:
        book = get_user_resource_or_404(session, Book, book_id, user_id, "Livro")
    else:
        book = get_or_404(session, Book, book_id, "Livro")

    effective_user_id = user_id or book.user_id

    frame = CanvasFrame(
        user_id=effective_user_id,
        book_id=book_id,
        title=payload.title,
        color=payload.color,
        pos_x=payload.pos_x,
        pos_y=payload.pos_y,
        width=payload.width,
        height=payload.height,
    )
    session.add(frame)
    commit_changes(session)
    return frame


def update_canvas_frame(
    session: Session,
    frame_id: int,
    payload: CanvasFrameUpdate,
    user_id: str | None = None,
) -> CanvasFrame:
    """Atualiza título, cor ou dimensões de uma moldura."""
    if user_id:
        frame = get_user_resource_or_404(session, CanvasFrame, frame_id, user_id, "Moldura")
    else:
        frame = get_or_404(session, CanvasFrame, frame_id, "Moldura")

    if payload.title is not None:
        frame.title = payload.title
    if payload.color is not None:
        frame.color = payload.color
    if payload.pos_x is not None:
        frame.pos_x = payload.pos_x
    if payload.pos_y is not None:
        frame.pos_y = payload.pos_y
    if payload.width is not None:
        frame.width = payload.width
    if payload.height is not None:
        frame.height = payload.height

    commit_changes(session)
    return frame


def delete_canvas_frame(session: Session, frame_id: int, user_id: str | None = None) -> None:
    """Remove permanentemente uma moldura manual do Canvas."""
    if user_id:
        frame = get_user_resource_or_404(session, CanvasFrame, frame_id, user_id, "Moldura")
    else:
        frame = get_or_404(session, CanvasFrame, frame_id, "Moldura")

    session.delete(frame)
    commit_changes(session)
