from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.models import Book, Chapter
from app.schemas.chapter import ChapterCreate, ChapterMove, ChapterPatch, ChapterRead
from app.schemas.common import SQLITE_MAX_INTEGER
from app.services.persistence import check_optimistic_lock, commit_changes, get_user_resource_or_404

router = APIRouter(prefix="/books/{book_id}/chapters", tags=["Capítulos"])


@router.get("", response_model=list[ChapterRead], summary="Listar capítulos de um livro")
def list_chapters(book_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    book = get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return session.scalars(
        select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.position, Chapter.id)
    ).all()


@router.post("", response_model=ChapterRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar capítulo")
def create_chapter(
    book_id: Identifier,
    payload: ChapterCreate,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    book = get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    position = payload.position
    if position is None:
        last_position = session.scalar(select(func.max(Chapter.position)).where(Chapter.book_id == book_id))
        position = 0 if last_position is None else last_position + 1
        if position > SQLITE_MAX_INTEGER:
            raise HTTPException(status_code=409, detail="Não há posição disponível após o último capítulo.")
    chapter = Chapter(book_id=book_id, name=payload.name, position=position)
    session.add(chapter)
    commit_changes(session)
    return chapter


@router.patch("/{chapter_id}", response_model=ChapterRead, summary="Renomear capítulo")
def update_chapter(
    book_id: Identifier,
    chapter_id: Identifier,
    payload: ChapterPatch,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    chapter = session.scalar(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    if chapter is None:
        raise HTTPException(status_code=404, detail="Capítulo não encontrado.")

    check_optimistic_lock(chapter.updated_at, payload.expected_updated_at, "Capítulo")

    if payload.name is not None:
        chapter.name = payload.name

    commit_changes(session)
    session.refresh(chapter)
    return chapter


@router.post("/{chapter_id}/move", response_model=list[ChapterRead], summary="Mover posição do capítulo")
def move_chapter(
    book_id: Identifier,
    chapter_id: Identifier,
    payload: ChapterMove,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    chapters = list(
        session.scalars(
            select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.position, Chapter.id)
        ).all()
    )
    current_idx = next((i for i, ch in enumerate(chapters) if ch.id == chapter_id), None)
    if current_idx is None:
        raise HTTPException(status_code=404, detail="Capítulo não encontrado.")

    if payload.direction == "up":
        if current_idx == 0:
            raise HTTPException(status_code=400, detail="Capítulo já está no topo da lista.")
        target_idx = current_idx - 1
    elif payload.direction == "down":
        if current_idx == len(chapters) - 1:
            raise HTTPException(status_code=400, detail="Capítulo já está no final da lista.")
        target_idx = current_idx + 1
    else:
        raise HTTPException(status_code=400, detail="Direção inválida.")

    chapters[current_idx], chapters[target_idx] = chapters[target_idx], chapters[current_idx]
    for pos, ch in enumerate(chapters):
        ch.position = pos

    commit_changes(session)
    return chapters
