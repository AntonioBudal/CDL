from fastapi import APIRouter, status
from sqlalchemy import select

from app.dependencies import DatabaseSession
from app.models import Book
from app.schemas.book import BookCreate, BookRead
from app.services.persistence import commit_changes

router = APIRouter(prefix="/books", tags=["Livros"])


@router.get("", response_model=list[BookRead], summary="Listar livros")
def list_books(session: DatabaseSession):
    return session.scalars(select(Book).order_by(Book.id)).all()


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar livro")
def create_book(payload: BookCreate, session: DatabaseSession):
    book = Book(**payload.model_dump())
    session.add(book)
    commit_changes(session)
    return book
