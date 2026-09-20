"""Serviço de layout espacial 2D isolado para estudos (Canvas)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select

from app.models import Book, CanvasFrame, Study, StudyCanvasNode
from app.schemas.study_canvas_node import CanvasBatchUpdateRequest, CanvasNodeItem, CanvasNodePatchRequest
from app.schemas.study_grouping import CanvasFrameCreate, CanvasFrameUpdate
from app.services.persistence import commit_changes, get_or_404

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def get_book_canvas_nodes(session: Session, book_id: int) -> list[StudyCanvasNode]:
    """Retorna todas as coordenadas espaciais de estudos associados a um livro."""
    get_or_404(session, Book, book_id, "Livro")

    stmt = (
        select(StudyCanvasNode)
        .join(Study, StudyCanvasNode.study_id == Study.id)
        .where(
            StudyCanvasNode.book_id == book_id,
            Study.deleted_at.is_(None),
        )
        .order_by(StudyCanvasNode.z_index.asc(), StudyCanvasNode.id.asc())
    )
    return list(session.scalars(stmt).all())


def batch_upsert_canvas_nodes(
    session: Session,
    book_id: int,
    payload: CanvasBatchUpdateRequest,
) -> list[StudyCanvasNode]:
    """Atualiza ou insere em lote coordenadas espaciais de estudos com isolamento atômico."""
    get_or_404(session, Book, book_id, "Livro")

    # Mapear os nós já existentes no banco para este livro
    stmt_existing = select(StudyCanvasNode).where(StudyCanvasNode.book_id == book_id)
    existing_map = {node.study_id: node for node in session.scalars(stmt_existing).all()}

    updated_nodes: list[StudyCanvasNode] = []

    for item in payload.nodes:
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
    return get_book_canvas_nodes(session, book_id)


def patch_study_canvas_node(
    session: Session,
    study_id: int,
    payload: CanvasNodePatchRequest,
) -> StudyCanvasNode:
    """Atualiza individualmente as coordenadas ou aparência de um estudo no Canvas."""
    study = get_or_404(session, Study, study_id, "Estudo")
    if study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo está na lixeira.")

    if study.chapter is None:
        raise HTTPException(status_code=400, detail="Estudo sem capítulo associado.")

    book_id = study.chapter.book_id

    stmt = select(StudyCanvasNode).where(
        StudyCanvasNode.study_id == study_id,
        StudyCanvasNode.book_id == book_id,
    )
    node = session.scalars(stmt).first()

    if node is None:
        node = StudyCanvasNode(
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


def get_book_canvas_frames(session: Session, book_id: int) -> list[CanvasFrame]:
    """Retorna todas as molduras espaciais associadas ao Canvas de um livro."""
    get_or_404(session, Book, book_id, "Livro")

    stmt = (
        select(CanvasFrame)
        .where(CanvasFrame.book_id == book_id)
        .order_by(CanvasFrame.created_at.asc(), CanvasFrame.id.asc())
    )
    return list(session.scalars(stmt).all())


def create_canvas_frame(
    session: Session,
    book_id: int,
    payload: CanvasFrameCreate,
) -> CanvasFrame:
    """Cria uma nova moldura manual delimitadora no Canvas do livro."""
    get_or_404(session, Book, book_id, "Livro")

    frame = CanvasFrame(
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
) -> CanvasFrame:
    """Atualiza individualmente o título, cor ou dimensões de uma moldura."""
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


def delete_canvas_frame(session: Session, frame_id: int) -> None:
    """Remove individualmente uma moldura manual do Canvas."""
    frame = get_or_404(session, CanvasFrame, frame_id, "Moldura")
    session.delete(frame)
    commit_changes(session)

