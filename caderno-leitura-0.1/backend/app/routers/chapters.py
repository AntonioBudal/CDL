from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.dependencies import DatabaseSession, Identifier
from app.models import Book, Chapter
from app.schemas.chapter import ChapterCreate, ChapterRead
from app.schemas.common import SQLITE_MAX_INTEGER
from app.services.persistence import commit_changes, get_or_404

router = APIRouter(prefix="/books/{book_id}/chapters", tags=["Capítulos"])


@router.get("", response_model=list[ChapterRead], summary="Listar capítulos de um livro")
def list_chapters(book_id: Identifier, session: DatabaseSession):
    get_or_404(session, Book, book_id, "Livro")
    return session.scalars(
        select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.position, Chapter.id)
    ).all()


@router.post("", response_model=ChapterRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar capítulo")
def create_chapter(book_id: Identifier, payload: ChapterCreate, session: DatabaseSession):
    get_or_404(session, Book, book_id, "Livro")
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
