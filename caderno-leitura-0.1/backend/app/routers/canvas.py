from fastapi import APIRouter, status

from app.dependencies import DatabaseSession, Identifier
from app.schemas.study_canvas_node import (
    BookCanvasResponse,
    CanvasBatchUpdateRequest,
    CanvasNodePatchRequest,
    CanvasNodeRead,
)
from app.schemas.study_grouping import (
    CanvasFrameCreate,
    CanvasFrameItem,
    CanvasFrameUpdate,
)
from app.services.canvas_service import (
    batch_upsert_canvas_nodes,
    create_canvas_frame,
    delete_canvas_frame,
    get_book_canvas_frames,
    get_book_canvas_nodes,
    patch_study_canvas_node,
    update_canvas_frame,
)

router = APIRouter(tags=["Canvas de Estudos"])


@router.get(
    "/books/{book_id}/canvas",
    response_model=BookCanvasResponse,
    summary="Obter layout espacial do Canvas de um livro",
)
def get_canvas(book_id: Identifier, session: DatabaseSession):
    nodes = get_book_canvas_nodes(session, book_id)
    return BookCanvasResponse(book_id=book_id, nodes=nodes)


@router.put(
    "/books/{book_id}/canvas",
    response_model=BookCanvasResponse,
    summary="Atualizar em lote coordenadas espaciais dos estudos no Canvas",
)
def update_canvas_batch(
    book_id: Identifier,
    payload: CanvasBatchUpdateRequest,
    session: DatabaseSession,
):
    nodes = batch_upsert_canvas_nodes(session, book_id, payload)
    return BookCanvasResponse(book_id=book_id, nodes=nodes)


@router.patch(
    "/studies/{study_id}/canvas",
    response_model=CanvasNodeRead,
    summary="Atualizar coordenadas ou tag de cor de um estudo específico no Canvas",
)
def patch_canvas_node(
    study_id: Identifier,
    payload: CanvasNodePatchRequest,
    session: DatabaseSession,
):
    return patch_study_canvas_node(session, study_id, payload)


@router.get(
    "/books/{book_id}/canvas/frames",
    response_model=list[CanvasFrameItem],
    summary="Listar todas as molduras manuais do Canvas de um livro",
)
def list_canvas_frames(book_id: Identifier, session: DatabaseSession):
    return get_book_canvas_frames(session, book_id)


@router.post(
    "/books/{book_id}/canvas/frames",
    response_model=CanvasFrameItem,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova moldura manual delimitadora no Canvas do livro",
)
def create_canvas_frame_endpoint(
    book_id: Identifier,
    payload: CanvasFrameCreate,
    session: DatabaseSession,
):
    return create_canvas_frame(session, book_id, payload)


@router.patch(
    "/canvas/frames/{frame_id}",
    response_model=CanvasFrameItem,
    summary="Atualizar título, cor ou dimensões de uma moldura",
)
def update_canvas_frame_endpoint(
    frame_id: Identifier,
    payload: CanvasFrameUpdate,
    session: DatabaseSession,
):
    return update_canvas_frame(session, frame_id, payload)


@router.delete(
    "/canvas/frames/{frame_id}",
    summary="Remover individualmente uma moldura manual do Canvas",
)
def delete_canvas_frame_endpoint(
    frame_id: Identifier,
    session: DatabaseSession,
):
    delete_canvas_frame(session, frame_id)
    return {"success": True, "message": "Moldura removida com sucesso."}

