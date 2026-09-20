"""Serviço de persistência e regras de negócio para lixeira e soft delete."""
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.types import utc_now
from app.models import Book, Chapter, Study
from app.services.persistence import commit_changes, get_or_404, get_user_resource_or_404


def trash_book(session: Session, book_id: int, user_id: str | None = None) -> Book:
    """Move um livro para a lixeira (soft delete)."""
    if user_id is not None:
        book = get_user_resource_or_404(session, Book, book_id, user_id, "Livro")
    else:
        book = get_or_404(session, Book, book_id, "Livro")
    if book.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Este livro já está na lixeira.")

    book.deleted_at = utc_now()
    commit_changes(session)
    session.refresh(book)
    return book


def restore_book(session: Session, book_id: int, user_id: str | None = None) -> Book:
    """Restaura um livro da lixeira."""
    if user_id is not None:
        book = get_user_resource_or_404(session, Book, book_id, user_id, "Livro")
    else:
        book = get_or_404(session, Book, book_id, "Livro")
    if book.deleted_at is None:
        raise HTTPException(status_code=400, detail="Este livro não está na lixeira.")

    book.deleted_at = None
    commit_changes(session)
    session.refresh(book)
    return book


def permanent_delete_book(session: Session, book_id: int, user_id: str | None = None) -> None:
    """Exclui definitivamente um livro, seus capítulos e estudos subordinados."""
    if user_id is not None:
        book = get_user_resource_or_404(session, Book, book_id, user_id, "Livro")
    else:
        book = get_or_404(session, Book, book_id, "Livro")
    cover_image = book.cover_image

    # Coleta IDs de capítulos para remover estudos vinculados
    chapter_ids = [c.id for c in book.chapters]
    if chapter_ids:
        session.query(Study).filter(Study.chapter_id.in_(chapter_ids)).delete(synchronize_session=False)
        session.query(Chapter).filter(Chapter.id.in_(chapter_ids)).delete(synchronize_session=False)

    session.delete(book)
    commit_changes(session)

    if cover_image:
        from app.services.cover_service import delete_cover_file_if_orphan
        delete_cover_file_if_orphan(session, cover_image, current_book_id=book_id)


def trash_study(session: Session, study_id: int, user_id: str | None = None) -> Study:
    """Move um estudo para a lixeira (soft delete) aplicando cascata lógica em todos os descendentes."""
    if user_id is not None:
        study = get_user_resource_or_404(session, Study, study_id, user_id, "Estudo")
    else:
        study = get_or_404(session, Study, study_id, "Estudo")
    if study.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Este estudo já está na lixeira.")

    from app.services.study_service import get_descendant_ids
    descendant_ids = get_descendant_ids(session, study_id, include_deleted=False)
    all_ids = [study_id] + descendant_ids
    now = utc_now()

    session.query(Study).filter(Study.id.in_(all_ids)).update({"deleted_at": now}, synchronize_session=False)
    commit_changes(session)
    session.refresh(study)
    return study


def restore_study(session: Session, study_id: int, user_id: str | None = None) -> tuple[Study, bool]:
    """Restaura um estudo da lixeira.
    
    Se o livro ancestral estiver na lixeira, executa restauração em cascata
    ascendente, reativando o livro e o respectivo capítulo. Também restaura
    em cascata lógica todos os sub-estudos descendentes subordinados.
    """
    study = (
        session.query(Study)
        .options(joinedload(Study.chapter).joinedload(Chapter.book))
        .filter(Study.id == study_id)
        .first()
    )
    if study is None or (user_id is not None and study.user_id != user_id):
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")

    parent_book_deleted = bool(study.chapter and study.chapter.book and study.chapter.book.deleted_at is not None)
    if study.deleted_at is None and not parent_book_deleted:
        raise HTTPException(status_code=400, detail="Este estudo não está na lixeira.")

    study.deleted_at = None
    book_restored = False

    if parent_book_deleted:
        study.chapter.book.deleted_at = None
        book_restored = True

    from app.services.study_service import get_descendant_ids
    descendant_ids = get_descendant_ids(session, study_id, include_deleted=True)
    if descendant_ids:
        session.query(Study).filter(Study.id.in_(descendant_ids)).update({"deleted_at": None}, synchronize_session=False)

    commit_changes(session)
    session.refresh(study)
    return study, book_restored


def permanent_delete_study(session: Session, study_id: int, user_id: str | None = None) -> None:
    """Exclui definitivamente um estudo."""
    if user_id is not None:
        study = get_user_resource_or_404(session, Study, study_id, user_id, "Estudo")
    else:
        study = get_or_404(session, Study, study_id, "Estudo")
    session.delete(study)
    commit_changes(session)


def get_trash_items(session: Session, user_id: str | None = None, threshold_days: int = 30) -> dict:
    """Retorna itens atualmente na lixeira com contagem de dias restantes até o expurgo."""
    now = datetime.now(UTC)

    # 1. Livros na lixeira
    books_query = session.query(Book).filter(Book.deleted_at.is_not(None))
    if user_id is not None:
        books_query = books_query.filter(Book.user_id == user_id)
    books = books_query.order_by(Book.deleted_at.desc()).all()

    books_data = []
    for b in books:
        del_at = b.deleted_at if b.deleted_at.tzinfo is not None else b.deleted_at.replace(tzinfo=UTC)
        elapsed_days = (now - del_at).days
        days_left = max(0, threshold_days - elapsed_days)

        chap_count = len(b.chapters)
        study_count = sum(len(c.studies) for c in b.chapters)

        books_data.append(
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "deleted_at": del_at,
                "days_until_purge": days_left,
                "chapters_count": chap_count,
                "studies_count": study_count,
            }
        )

    # 2. Estudos descartados individualmente (onde o estudo possui deleted_at preenchido)
    studies_query = (
        session.query(Study)
        .options(joinedload(Study.chapter).joinedload(Chapter.book))
        .filter(Study.deleted_at.is_not(None))
    )
    if user_id is not None:
        studies_query = studies_query.filter(Study.user_id == user_id)
    studies = studies_query.order_by(Study.deleted_at.desc()).all()

    studies_data = []
    for s in studies:
        del_at = s.deleted_at if s.deleted_at.tzinfo is not None else s.deleted_at.replace(tzinfo=UTC)
        elapsed_days = (now - del_at).days
        days_left = max(0, threshold_days - elapsed_days)

        book_id = s.chapter.book.id if s.chapter and s.chapter.book else 0
        book_title = s.chapter.book.title if s.chapter and s.chapter.book else ""
        chap_name = s.chapter.name if s.chapter else ""

        studies_data.append(
            {
                "id": s.id,
                "title": s.title,
                "book_id": book_id,
                "book_title": book_title,
                "chapter_name": chap_name,
                "deleted_at": del_at,
                "days_until_purge": days_left,
            }
        )

    return {
        "books": books_data,
        "studies": studies_data,
        "total_items": len(books_data) + len(studies_data),
    }


def empty_trash(session: Session, user_id: str | None = None) -> tuple[int, int]:
    """Expurga definitivamente todos os itens na lixeira."""
    # 1. Livros descartados
    books_query = session.query(Book).filter(Book.deleted_at.is_not(None))
    if user_id is not None:
        books_query = books_query.filter(Book.user_id == user_id)
    trashed_books = books_query.all()

    purged_books = len(trashed_books)
    cover_images = [b.cover_image for b in trashed_books if b.cover_image]
    for b in trashed_books:
        chapter_ids = [c.id for c in b.chapters]
        if chapter_ids:
            session.query(Study).filter(Study.chapter_id.in_(chapter_ids)).delete(synchronize_session=False)
            session.query(Chapter).filter(Chapter.id.in_(chapter_ids)).delete(synchronize_session=False)
        session.delete(b)

    # 2. Estudos restantes descartados individualmente
    studies_query = session.query(Study).filter(Study.deleted_at.is_not(None))
    if user_id is not None:
        studies_query = studies_query.filter(Study.user_id == user_id)
    trashed_studies = studies_query.all()

    purged_studies = len(trashed_studies)
    for s in trashed_studies:
        session.delete(s)

    commit_changes(session)

    if cover_images:
        from app.services.cover_service import delete_cover_file_if_orphan

        for c in cover_images:
            delete_cover_file_if_orphan(session, c)

    return purged_books, purged_studies


def purge_expired_trash(session: Session, user_id: str | None = None, threshold_days: int = 30) -> tuple[int, int]:
    """Expurga registros na lixeira com mais de `threshold_days` dias."""
    cutoff = datetime.now(UTC) - timedelta(days=threshold_days)

    # 1. Livros expirados
    books_query = session.query(Book).filter(Book.deleted_at.is_not(None), Book.deleted_at < cutoff)
    if user_id is not None:
        books_query = books_query.filter(Book.user_id == user_id)
    expired_books = books_query.all()

    purged_books = len(expired_books)
    cover_images = [b.cover_image for b in expired_books if b.cover_image]
    for b in expired_books:
        chapter_ids = [c.id for c in b.chapters]
        if chapter_ids:
            session.query(Study).filter(Study.chapter_id.in_(chapter_ids)).delete(synchronize_session=False)
            session.query(Chapter).filter(Chapter.id.in_(chapter_ids)).delete(synchronize_session=False)
        session.delete(b)

    # 2. Estudos expirados
    studies_query = (
        session.query(Study)
        .filter(Study.deleted_at.is_not(None), Study.deleted_at < cutoff)
    )
    if user_id is not None:
        studies_query = studies_query.filter(Study.user_id == user_id)
    expired_studies = studies_query.all()

    purged_studies = len(expired_studies)
    for s in expired_studies:
        session.delete(s)

    commit_changes(session)

    if cover_images:
        from app.services.cover_service import delete_cover_file_if_orphan

        for c in cover_images:
            delete_cover_file_if_orphan(session, c)

    return purged_books, purged_studies
