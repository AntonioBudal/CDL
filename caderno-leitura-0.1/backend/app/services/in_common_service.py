"""F0.10.07 (spec 100): leituras e estudos em comum entre amigos.

Privacidade: do lado do amigo entram só os livros e estudos que o visitante já pode ler pelas regras de
`sharing_service` (público ou amigos; estudos também por concessão nominal). Livros privados do amigo nunca
aparecem, nem como contagem.
"""
from __future__ import annotations

import re
import unicodedata

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.user import User
from app.schemas.in_common import InCommonBook, InCommonResponse, InCommonStudy
from app.services.friendship_service import is_blocked_between
from app.services.sharing_service import can_read_study, get_shared_studies_for_user, is_friends_between

MAX_BOOKS = 30
MAX_STUDIES_PER_BOOK = 5

_SURNAME_SUFFIXES = {"junior", "jr", "filho", "neto", "sobrinho"}


def _fold(text: str) -> str:
    """Minúsculas, sem acentos, só letras e dígitos separados por um espaço."""
    decomposed = unicodedata.normalize("NFKD", text or "")
    no_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"[^0-9a-z]+", " ", no_marks.casefold()).strip()


def normalize_title_key(title: str | None) -> str:
    """Chave do título: ignora o subtítulo depois de ':', acentos, caixa, pontuação e espaços repetidos."""
    main = (title or "").split(":", 1)[0]
    return _fold(main)


def first_author_surname_key(author: str | None) -> str:
    """Sobrenome do primeiro autor, normalizado ("Machado de Assis" e "Assis, Machado de" → "assis")."""
    text = (author or "").strip()
    if not text:
        return ""
    first = re.split(r"\s*;\s*|\s+e\s+|\s+and\s+|\s*&\s*", text, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    if "," in first:
        surname = first.split(",", 1)[0]
    else:
        words = first.split()
        if len(words) > 2 and _fold(words[-1]) in _SURNAME_SUFFIXES:
            surname = " ".join(words[-2:])
        else:
            surname = words[-1] if words else ""
    return _fold(surname)


def _authors_compatible(a: str | None, b: str | None) -> bool:
    key_a, key_b = first_author_surname_key(a), first_author_surname_key(b)
    if not key_a or not key_b:
        return True
    return key_a == key_b


def _resolve_target(session: Session, viewer_id: str, username: str) -> User:
    target = session.scalar(select(User).where(func.lower(User.username) == username.strip().lower()))
    not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    if target is None or target.id == viewer_id or is_blocked_between(session, viewer_id, target.id):
        raise not_found
    return target


def get_in_common(session: Session, viewer_id: str, username: str) -> InCommonResponse:
    target = _resolve_target(session, viewer_id, username)

    if not is_friends_between(session, viewer_id, target.id):
        return InCommonResponse(is_friend=False, books=[], books_truncated=False, shared_with_me_total=0)

    my_books = session.execute(
        select(Book.id, Book.title, Book.author)
        .where(Book.user_id == viewer_id, Book.deleted_at.is_(None))
        .order_by(Book.id.asc())
    ).all()
    mine_by_key: dict[str, list[tuple[int, str, str | None]]] = {}
    for book_id, title, author in my_books:
        key = normalize_title_key(title)
        if key:
            mine_by_key.setdefault(key, []).append((book_id, title, author))

    # Amigo aceito: livros "friends" e "public" são legíveis (mesma regra de can_read_book).
    friend_books = session.execute(
        select(Book.id, Book.title, Book.author)
        .where(
            Book.user_id == target.id,
            Book.deleted_at.is_(None),
            Book.visibility.in_(("friends", "public")),
        )
        .order_by(Book.title.asc(), Book.id.asc())
    ).all()

    matches: list[tuple[int, str, str | None, int]] = []
    seen_keys: set[str] = set()
    for f_id, f_title, f_author in friend_books:
        key = normalize_title_key(f_title)
        if not key or key in seen_keys:
            continue
        candidates = [m for m in mine_by_key.get(key, []) if _authors_compatible(m[2], f_author)]
        if not candidates:
            continue
        seen_keys.add(key)
        my_id, _my_title, my_author = candidates[0]
        matches.append((f_id, f_title, f_author or my_author, my_id))

    truncated = len(matches) > MAX_BOOKS
    matches = matches[:MAX_BOOKS]

    books: list[InCommonBook] = []
    for f_id, f_title, author, my_id in matches:
        friend_book = session.get(Book, f_id)
        rows = session.execute(
            select(Study, Chapter.name)
            .join(Chapter, Study.chapter_id == Chapter.id)
            .where(
                Chapter.book_id == f_id,
                Study.user_id == target.id,
                Study.deleted_at.is_(None),
            )
            .order_by(Study.updated_at.desc(), Study.id.desc())
        ).all()
        readable = [(s, c_name) for s, c_name in rows if can_read_study(session, viewer_id, s, friend_book)]
        books.append(
            InCommonBook(
                title=f_title,
                author=author,
                my_book_id=my_id,
                friend_book_id=f_id,
                friend_studies=[
                    InCommonStudy(
                        id=s.id,
                        title=s.title,
                        chapter_name=c_name,
                        book_id=f_id,
                        updated_at=s.updated_at,
                    )
                    for s, c_name in readable[:MAX_STUDIES_PER_BOOK]
                ],
                friend_studies_total=len(readable),
            )
        )

    _items, shared_total = get_shared_studies_for_user(
        session=session, user_id=viewer_id, author=target.username, limit=1, offset=0
    )

    return InCommonResponse(
        is_friend=True,
        books=books,
        books_truncated=truncated,
        shared_with_me_total=shared_total,
    )
