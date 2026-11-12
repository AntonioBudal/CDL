"""F0.11.07 (spec 109): fontes para o validador de paráfrase.

Só entra **texto do livro** que o próprio leitor guardou: as capturas da Mesa do mesmo livro (inclusive as vindas do
Kindle/Kobo) e as citações literais (destaques `kind="quote"`) dos outros estudos do mesmo livro. As citações literais
do próprio estudo voltam à parte como **citação declarada**: frases que as contêm não são verificadas.

O fichamento (`source_response`) fica de fora de propósito: na importação ele é o texto que vira as seções e na
digitalização é a página manuscrita do leitor; compará-lo acusaria o texto do próprio leitor.
A comparação em si é feita no navegador.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Book, Chapter, InboxCapture, Study, StudyHighlight
from app.schemas.paraphrase import DeclaredQuote, ParaphraseSource, ParaphraseSources

MAX_CAPTURES = 2000
MAX_QUOTES = 2000


def _not_found(label: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} não encontrado.")


def _book_sources(
    session: Session, user_id: str, book_id: int, chapter_id: int, exclude_study_id: int | None
) -> list[ParaphraseSource]:
    captures = session.scalars(
        select(InboxCapture)
        .where(InboxCapture.user_id == user_id, InboxCapture.book_id == book_id)
        .order_by(InboxCapture.id)
        .limit(MAX_CAPTURES)
    ).all()
    sources = [
        ParaphraseSource(
            kind="capture",
            label="Captura deste capítulo" if row.chapter_id == chapter_id else "Captura deste livro",
            text=row.content,
        )
        for row in captures
        if row.content and row.content.strip()
    ]
    quote_query = (
        select(StudyHighlight.selected_text, Study.title)
        .join(Study, StudyHighlight.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .where(
            Chapter.book_id == book_id,
            Study.user_id == user_id,
            Study.deleted_at.is_(None),
            StudyHighlight.user_id == user_id,
            StudyHighlight.kind == "quote",
        )
        .order_by(StudyHighlight.id)
        .limit(MAX_QUOTES)
    )
    if exclude_study_id is not None:
        quote_query = quote_query.where(Study.id != exclude_study_id)
    sources.extend(
        ParaphraseSource(kind="quote", label=f"Citação literal em «{title}»", text=text)
        for text, title in session.execute(quote_query).all()
        if text and text.strip()
    )
    return sources


def study_paraphrase_sources(session: Session, user_id: str, study_id: int) -> ParaphraseSources:
    """Fontes de um estudo do próprio leitor, fora da lixeira (senão 404, sem revelar que existe)."""
    row = session.execute(
        select(Study, Chapter.book_id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            Study.id == study_id,
            Study.user_id == user_id,
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
    ).first()
    if row is None:
        raise _not_found("Estudo")
    study, book_id = row
    declared = session.execute(
        select(StudyHighlight.section, StudyHighlight.selected_text)
        .where(
            StudyHighlight.study_id == study.id,
            StudyHighlight.user_id == user_id,
            StudyHighlight.kind == "quote",
        )
        .order_by(StudyHighlight.id)
    ).all()
    return ParaphraseSources(
        sources=_book_sources(session, user_id, book_id, study.chapter_id, study.id),
        declared_quotes=[DeclaredQuote(section=section, text=text) for section, text in declared if text and text.strip()],
    )


def chapter_paraphrase_sources(session: Session, user_id: str, chapter_id: int) -> ParaphraseSources:
    """Fontes do livro de um capítulo do próprio leitor (para a importação, antes de o estudo existir)."""
    chapter = session.scalar(
        select(Chapter)
        .join(Book, Chapter.book_id == Book.id)
        .where(Chapter.id == chapter_id, Book.user_id == user_id, Book.deleted_at.is_(None))
    )
    if chapter is None:
        raise _not_found("Capítulo")
    return ParaphraseSources(sources=_book_sources(session, user_id, chapter.book_id, chapter.id, None), declared_quotes=[])
