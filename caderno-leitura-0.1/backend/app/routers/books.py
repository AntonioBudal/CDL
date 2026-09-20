from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status
from sqlalchemy import asc, desc, false, or_, select, text

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.models import Book
from app.models.category import book_categories
from app.schemas.book import BookCreate, BookPatch, BookRead
from app.schemas.cover import CoverResponse, CoverUrlRequest
from app.schemas.export import ExportFormat, ExportOptions
from app.services.category_service import assign_book_categories, get_descendant_category_ids
from app.services.cover_service import (
    download_cover_from_url,
    process_and_save_cover,
    remove_book_cover,
    set_book_cover,
)
from app.services.export_service import generate_book_export
from app.services.persistence import (
    check_optimistic_lock,
    commit_changes,
    get_or_404,
    get_user_resource_or_404,
)
from app.services.trash_service import permanent_delete_book, restore_book, trash_book

router = APIRouter(prefix="/books", tags=["Livros"])


@router.get("", response_model=list[BookRead], summary="Listar livros")
def list_books(
    session: DatabaseSession,
    current_user: CurrentUser,
    q: str | None = None,
    category: str | None = None,
    sort: str | None = None,
    order: str = "asc",
):
    query = select(Book).where(Book.deleted_at.is_(None), Book.user_id == current_user.id)

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Book.title.ilike(term),
                Book.author.ilike(term),
                Book.subtitle.ilike(term),
            )
        )

    if category and category.strip():
        cat_id = category.strip()
        descendant_ids = get_descendant_category_ids(session, cat_id)
        if descendant_ids:
            query = query.where(
                Book.id.in_(
                    select(book_categories.c.book_id).where(
                        book_categories.c.category_id.in_(descendant_ids)
                    )
                )
            )
        else:
            query = query.where(text("0 = 1"))

    sort_column = {
        "title": Book.title,
        "author": Book.author,
        "created_at": Book.created_at,
        "updated_at": Book.updated_at,
        "year": Book.year,
        "id": Book.id,
    }.get((sort or "").lower(), Book.id)

    order_fn = desc if (order or "").lower() == "desc" else asc

    if sort in ("author", "year"):
        query = query.order_by(sort_column.is_(None), order_fn(sort_column), Book.id)
    else:
        query = query.order_by(order_fn(sort_column), Book.id)

    return session.scalars(query).all()


@router.get("/{book_id}", response_model=BookRead, summary="Consultar livro")
def get_book(book_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    book = get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return book


@router.post("/{book_id}/trash", response_model=BookRead, summary="Mover livro para a lixeira")
def trash_book_endpoint(book_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return trash_book(session, book_id, user_id=current_user.id)


@router.post("/{book_id}/restore", response_model=BookRead, summary="Restaurar livro da lixeira")
def restore_book_endpoint(book_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return restore_book(session, book_id, user_id=current_user.id)


@router.delete("/{book_id}/permanent", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir livro permanentemente")
def permanent_delete_book_endpoint(book_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    permanent_delete_book(session, book_id, user_id=current_user.id)


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar livro")
def create_book(payload: BookCreate, session: DatabaseSession, current_user: CurrentUser):
    data = payload.model_dump(exclude={"category_ids"})
    book = Book(**data, user_id=current_user.id)
    if payload.category_ids:
        assign_book_categories(session, book, payload.category_ids)
    session.add(book)
    commit_changes(session)
    session.refresh(book)
    return book


@router.patch("/{book_id}", response_model=BookRead, summary="Atualizar metadados do livro")
def update_book(book_id: Identifier, payload: BookPatch, session: DatabaseSession, current_user: CurrentUser):
    book = get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    check_optimistic_lock(book.updated_at, payload.expected_updated_at, "Livro")

    if "category_ids" in payload.model_fields_set:
        assign_book_categories(session, book, payload.category_ids or [])

    changes = payload.model_dump(exclude_unset=True, exclude={"expected_updated_at", "category_ids"})
    for name, value in changes.items():
        setattr(book, name, value)

    commit_changes(session)
    session.refresh(book)
    return book


@router.post("/{book_id}/cover", response_model=CoverResponse, summary="Fazer upload de capa do livro")
async def upload_book_cover(
    book_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    book = get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    data = await file.read()
    filename = process_and_save_cover(data)
    updated_book = set_book_cover(session, book_id, filename)
    return CoverResponse(
        book_id=updated_book.id,
        cover_image=updated_book.cover_image,
        cover_url=f"/api/covers/{updated_book.cover_image}",
        message="Capa atualizada com sucesso.",
    )


@router.post("/{book_id}/cover/url", response_model=CoverResponse, summary="Importar capa por URL direta")
def import_book_cover_url(
    book_id: Identifier,
    payload: CoverUrlRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
):
    book = get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    filename = download_cover_from_url(payload.url)
    updated_book = set_book_cover(session, book_id, filename)
    return CoverResponse(
        book_id=updated_book.id,
        cover_image=updated_book.cover_image,
        cover_url=f"/api/covers/{updated_book.cover_image}",
        message="Capa importada com sucesso.",
    )


@router.delete("/{book_id}/cover", response_model=CoverResponse, summary="Remover capa do livro")
def delete_book_cover(book_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    book = get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    updated_book = remove_book_cover(session, book_id)
    return CoverResponse(
        book_id=updated_book.id,
        cover_image=None,
        cover_url=None,
        message="Capa removida com sucesso.",
    )


@router.get("/{book_id}/export", summary="Exportar anotações e estudos do livro")
def export_book(
    book_id: Identifier,
    session: DatabaseSession,
    current_user: CurrentUser,
    format: ExportFormat = ExportFormat.MARKDOWN,
    include_notes: bool = True,
    include_sections: bool = True,
    include_source: bool = False,
    include_metadata: bool = True,
):
    book = get_user_resource_or_404(session, Book, book_id, current_user.id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    options = ExportOptions(
        format=format,
        include_notes=include_notes,
        include_sections=include_sections,
        include_source=include_source,
        include_metadata=include_metadata,
    )
    content, filename, media_type = generate_book_export(session, book_id, options)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return Response(content=content.encode("utf-8"), media_type=media_type, headers=headers)

