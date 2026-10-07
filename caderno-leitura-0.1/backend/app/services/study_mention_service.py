"""Serviço para extração de menções textuais [[...]] e backlinks entre estudos."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.study_mention import StudyMention
from app.schemas.study_mention import (
    BacklinkItemRead,
    BacklinksResponse,
    StudyCandidateOption,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Expressão regular para capturar menções no formato [[Título]] ou [[Título|id]]
MENTION_REGEX = re.compile(r"\[\[([^\]|]+?)(?:\s*\|\s*([^\]]+?))?\]\]")

STUDY_TEXT_SECTIONS = ("summary", "explanation", "concepts", "references", "notes")


def extract_context_snippet(full_text: str, match_start: int, match_end: int, max_len: int = 180) -> str:
    """Extrai um fragmento contextual de aproximadamente ~180 caracteres em torno da menção."""
    target_len = match_end - match_start
    avail_margin = max(30, (max_len - target_len) // 2)
    start = max(0, match_start - avail_margin)
    end = min(len(full_text), match_end + avail_margin)

    raw_slice = full_text[start:end]
    clean_snippet = " ".join(raw_slice.split())
    if start > 0 and not clean_snippet.startswith("..."):
        clean_snippet = f"...{clean_snippet}"
    if end < len(full_text) and not clean_snippet.endswith("..."):
        clean_snippet = f"{clean_snippet}..."
    return clean_snippet


def extract_mentions_from_study_text(text: str) -> list[tuple[str, int | None, str]]:
    """Extrai todas as menções [[...]] do texto.
    
    Retorna lista de tuplas: (título_mencionado, id_explicito_opcional, snippet_contextual).
    """
    if not text:
        return []

    results: list[tuple[str, int | None, str]] = []
    for match in MENTION_REGEX.finditer(text):
        raw_title = match.group(1).strip()
        if not raw_title:
            continue
        raw_id = match.group(2).strip() if match.group(2) else None
        explicit_id = int(raw_id) if raw_id and raw_id.isdigit() else None
        snippet = extract_context_snippet(text, match.start(), match.end())
        results.append((raw_title, explicit_id, snippet))
    return results


def sync_study_mentions(session: Session, study: Study, user_id: str) -> None:
    """Extrai menções das seções de texto do estudo e sincroniza a tabela study_mentions."""
    # 1. Remover menções de saída anteriores originadas deste estudo
    existing_mentions = session.scalars(
        select(StudyMention).where(
            StudyMention.source_study_id == study.id,
            StudyMention.user_id == user_id,
        )
    ).all()
    for em in existing_mentions:
        session.delete(em)

    # 2. Percorrer as seções de texto e coletar novas menções
    for section_name in STUDY_TEXT_SECTIONS:
        section_content = getattr(study, section_name, None)
        if not section_content or not isinstance(section_content, str):
            continue

        mentions = extract_mentions_from_study_text(section_content)
        for title, explicit_id, snippet in mentions:
            target_id: int | None = None

            if explicit_id is not None:
                # Verificação determinística por ID
                candidate = session.get(Study, explicit_id)
                if candidate is not None and candidate.user_id == user_id and candidate.id != study.id:
                    target_id = candidate.id
            else:
                # Resolução por título (case-insensitive)
                stmt = (
                    select(Study.id)
                    .where(
                        Study.user_id == user_id,
                        func.lower(Study.title) == title.lower(),
                        Study.id != study.id,
                    )
                    .order_by(Study.deleted_at.is_(None).desc(), Study.updated_at.desc())
                    .limit(1)
                )
                target_id = session.scalars(stmt).first()

            if target_id is not None:
                mention_record = StudyMention(
                    user_id=user_id,
                    source_study_id=study.id,
                    target_study_id=target_id,
                    section=section_name,
                    mention_text=title,
                    context_snippet=snippet,
                )
                session.add(mention_record)


def get_study_backlinks(session: Session, study_id: int, user_id: str) -> BacklinksResponse:
    """Retorna referências reversas (estudos que mencionam o estudo indicado)."""
    target_study = session.get(Study, study_id)
    if target_study is None or target_study.deleted_at is not None or target_study.user_id != user_id:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")

    stmt = (
        select(StudyMention)
        .options(
            selectinload(StudyMention.source_study)
            .selectinload(Study.chapter)
            .selectinload(Chapter.book)
        )
        .join(Study, StudyMention.source_study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            StudyMention.target_study_id == study_id,
            StudyMention.user_id == user_id,
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
        .order_by(StudyMention.created_at.desc(), StudyMention.id.desc())
    )

    mentions = list(session.scalars(stmt).all())
    items: list[BacklinkItemRead] = []
    for mention in mentions:
        source_study = mention.source_study
        chapter = source_study.chapter if source_study else None
        book = chapter.book if chapter else None

        items.append(
            BacklinkItemRead(
                id=mention.id,
                source_study_id=mention.source_study_id,
                source_study_title=source_study.title if source_study else "",
                book_id=book.id if book else 0,
                book_title=book.title if book else "",
                chapter_id=chapter.id if chapter else 0,
                chapter_name=chapter.name if chapter else "",
                section=mention.section,
                mention_text=mention.mention_text,
                context_snippet=mention.context_snippet,
                created_at=mention.created_at,
            )
        )

    return BacklinksResponse(items=items, total=len(items))


def search_study_candidates(
    session: Session,
    user_id: str,
    query: str = "",
    exclude_study_id: int | None = None,
    limit: int = 10,
) -> list[StudyCandidateOption]:
    """Busca estudos ativos do usuário como candidatos para autocomplete no editor ou relações."""
    clean_limit = min(max(1, limit), 50)
    stmt = (
        select(Study)
        .options(
            selectinload(Study.chapter).selectinload(Chapter.book)
        )
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            Study.user_id == user_id,
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
    )

    if exclude_study_id is not None:
        stmt = stmt.where(Study.id != exclude_study_id)

    if query and query.strip():
        search_term = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Study.title.ilike(search_term),
                Chapter.name.ilike(search_term),
                Book.title.ilike(search_term),
            )
        )

    stmt = stmt.order_by(Study.title.asc(), Study.updated_at.desc()).limit(clean_limit)
    studies = list(session.scalars(stmt).all())

    results: list[StudyCandidateOption] = []
    for study in studies:
        chapter = study.chapter
        book = chapter.book if chapter else None
        ch_name = chapter.name if chapter else ""
        results.append(
            StudyCandidateOption(
                id=study.id,
                title=study.title,
                book_id=book.id if book else 0,
                book_title=book.title if book else "",
                chapter_id=chapter.id if chapter else 0,
                chapter_name=ch_name,
                chapter_title=ch_name,
            )
        )

    return results
