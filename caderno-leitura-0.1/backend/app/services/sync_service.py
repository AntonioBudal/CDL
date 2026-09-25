from __future__ import annotations

from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.study import Study
from app.models.study_canvas_node import StudyCanvasNode
from app.models.user_preference import UserPreference
from app.schemas.book import BookRead
from app.schemas.preferences import UserPreferenceRead
from app.schemas.study import StudyRead
from app.schemas.study_canvas_node import CanvasNodeRead
from app.schemas.sync import SyncChangesResponse, SyncDeletedItems, SyncUpdatedItems


def get_sync_changes(
    session: Session,
    user_id: str,
    since: datetime | None = None,
) -> SyncChangesResponse:
    """Retorna o feed incremental de alterações e exclusões estritamente isolado pelo user_id."""
    server_time = datetime.now(UTC)

    if since is not None and since.tzinfo is None:
        since = since.replace(tzinfo=UTC)

    # 1. Consulta de Livros (Books)
    stmt_books = select(Book).where(
        Book.user_id == user_id,
        Book.deleted_at.is_(None),
    )
    if since is not None:
        stmt_books = stmt_books.where(Book.updated_at > since)
    stmt_books = stmt_books.order_by(Book.id)
    books = session.scalars(stmt_books).all()
    books_read = [BookRead.model_validate(b) for b in books]

    # 2. Consulta de Estudos (Studies)
    stmt_studies = select(Study).where(
        Study.user_id == user_id,
        Study.deleted_at.is_(None),
    )
    if since is not None:
        stmt_studies = stmt_studies.where(Study.updated_at > since)
    stmt_studies = stmt_studies.order_by(Study.id)
    studies = session.scalars(stmt_studies).all()
    studies_read = [StudyRead.model_validate(s) for s in studies]

    # 3. Consulta de Nós Espaciais do Canvas (Canvas Nodes)
    stmt_canvas = (
        select(StudyCanvasNode)
        .join(Study, StudyCanvasNode.study_id == Study.id)
        .where(
            StudyCanvasNode.user_id == user_id,
            Study.deleted_at.is_(None),
        )
    )
    if since is not None:
        stmt_canvas = stmt_canvas.where(StudyCanvasNode.updated_at > since)
    stmt_canvas = stmt_canvas.order_by(StudyCanvasNode.id)
    canvas_nodes = session.scalars(stmt_canvas).all()
    canvas_nodes_read = [CanvasNodeRead.model_validate(cn) for cn in canvas_nodes]

    # 4. Preferências do Usuário (Preferences)
    pref = session.get(UserPreference, user_id)
    pref_read: UserPreferenceRead | None = None
    if pref is not None:
        if since is None or (pref.updated_at is not None and pref.updated_at > since):
            pref_read = UserPreferenceRead.model_validate(pref)

    # 5. Tombstones de Itens Excluídos (Deleted Items)
    deleted_book_ids: list[int] = []
    deleted_study_ids: list[int] = []

    if since is not None:
        stmt_del_books = select(Book.id).where(
            Book.user_id == user_id,
            Book.deleted_at.is_not(None),
            Book.deleted_at > since,
        )
        deleted_book_ids = list(session.scalars(stmt_del_books).all())

        stmt_del_studies = select(Study.id).where(
            Study.user_id == user_id,
            Study.deleted_at.is_not(None),
            Study.deleted_at > since,
        )
        deleted_study_ids = list(session.scalars(stmt_del_studies).all())

    return SyncChangesResponse(
        server_time=server_time,
        updated=SyncUpdatedItems(
            books=books_read,
            studies=studies_read,
            canvas_nodes=canvas_nodes_read,
            preferences=pref_read,
        ),
        deleted=SyncDeletedItems(
            book_ids=deleted_book_ids,
            study_ids=deleted_study_ids,
        ),
    )
