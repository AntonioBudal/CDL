from __future__ import annotations

import html
import re
import unicodedata
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.orm import Session

from app.db.session import sqlite_unaccent
from app.db.types import utc_now
from app.models.book import Book
from app.models.category import book_categories
from app.models.chapter import Chapter
from app.models.search_history import SearchHistory
from app.models.study import Study
from app.schemas.search import (
    SearchHistoryItem,
    SearchHistoryResponse,
    SearchMatchItem,
    SearchResponse,
)

ACCENT_MAP: dict[str, str] = {
    "a": "[aáàãâäAÁÀÃÂÄ]",
    "e": "[eéèêëEÉÈÊË]",
    "i": "[iíìîïIÍÌÎÏ]",
    "o": "[oóòõôöOÓÒÕÔÖ]",
    "u": "[uúùûüUÚÙÛÜ]",
    "c": "[cçCÇ]",
}


def term_to_accent_regex(term: str) -> str:
    """Converte um termo em expressão regular insensível a acentuação e maiúsculas."""
    unaccented = sqlite_unaccent(term)
    parts = []
    for char in unaccented:
        if char in ACCENT_MAP:
            parts.append(ACCENT_MAP[char])
        else:
            parts.append(re.escape(char))
    return "".join(parts)


def highlight_terms(text: str, terms: list[str]) -> str:
    """Destaca os termos no texto sanitizado com <mark class="search-highlight">."""
    escaped_text = html.escape(text)
    for term in sorted(terms, key=len, reverse=True):
        if not term.strip():
            continue
        pattern = term_to_accent_regex(term.strip())
        escaped_text = re.sub(
            f"({pattern})",
            r'<mark class="search-highlight">\1</mark>',
            escaped_text,
            flags=re.IGNORECASE,
        )
    return escaped_text


def generate_snippet(text: str, terms: list[str], max_len: int = 140) -> str:
    """Extrai uma janela contextual de ~140 caracteres ao redor do primeiro match."""
    if not text:
        return ""

    norm_text = sqlite_unaccent(text)
    first_idx = -1

    for term in terms:
        clean_t = sqlite_unaccent(term)
        if not clean_t:
            continue
        idx = norm_text.find(clean_t)
        if idx != -1 and (first_idx == -1 or idx < first_idx):
            first_idx = idx

    if first_idx == -1:
        # Nenhum match direto no texto do estudo (match pode ter ocorrido no livro/capítulo)
        raw_slice = text[:max_len].strip()
        if len(text) > max_len:
            raw_slice += " …"
        return highlight_terms(raw_slice, terms)

    # Janela de contexto
    start = max(0, first_idx - 45)
    end = min(len(text), first_idx + 95)

    # Ajustar para fronteira de palavras quando possível
    if start > 0:
        space_idx = text.find(" ", start)
        if space_idx != -1 and space_idx < first_idx:
            start = space_idx + 1

    if end < len(text):
        space_idx = text.rfind(" ", first_idx, end)
        if space_idx != -1 and space_idx > first_idx:
            end = space_idx

    slice_content = text[start:end].strip()
    prefix = "… " if start > 0 else ""
    suffix = " …" if end < len(text) else ""

    return highlight_terms(f"{prefix}{slice_content}{suffix}", terms)


def determine_matched_field(
    study: Study,
    book_title: str,
    chapter_name: str,
    terms: list[str],
) -> tuple[str, str]:
    """Identifica o campo com maior relevância e retorna (rótulo_do_campo, texto_para_snippet)."""
    candidates = [
        ("Título", study.title or ""),
        ("Resumo", study.summary or ""),
        ("Conceitos", study.concepts or ""),
        ("Explicação", study.explanation or ""),
        ("Anotações", study.notes or ""),
        ("Referências", study.references or ""),
        ("Capítulo", chapter_name or ""),
        ("Livro", book_title or ""),
    ]

    for label, content in candidates:
        norm_content = sqlite_unaccent(content)
        for term in terms:
            clean_t = sqlite_unaccent(term)
            if clean_t and clean_t in norm_content:
                # Se for livro ou capítulo, usamos o resumo ou título do estudo como contexto
                if label in ("Capítulo", "Livro"):
                    snippet_content = study.summary or study.title or content
                    return label, snippet_content
                return label, content

    # Fallback
    return "Estudo", study.summary or study.title or ""


class SearchService:
    @staticmethod
    def search_studies(
        session: Session,
        query: str,
        mode: Literal["and", "or"] = "and",
        book_id: int | None = None,
        category_id: str | None = None,
        limit: int = 20,
    ) -> SearchResponse:
        clean_q = query.strip()
        if len(clean_q) < 2:
            return SearchResponse(query=clean_q, mode=mode, total=0, results=[], suggest_or=False)

        terms = [t for t in clean_q.split() if t]
        if not terms:
            return SearchResponse(query=clean_q, mode=mode, total=0, results=[], suggest_or=False)

        fields = [
            Study.title,
            Study.summary,
            Study.explanation,
            Study.concepts,
            Study.references,
            Study.notes,
            Book.title,
            Chapter.name,
        ]

        def build_term_condition(t: str):
            unaccented_term = f"%{sqlite_unaccent(t)}%"
            return or_(*[func.unaccent(f).like(unaccented_term) for f in fields])

        # Base query com joins e isolamento de soft delete
        base_stmt = (
            select(Study, Book.id.label("book_id"), Book.title.label("book_title"), Chapter.id.label("chap_id"), Chapter.name.label("chap_name"))
            .join(Chapter, Study.chapter_id == Chapter.id)
            .join(Book, Chapter.book_id == Book.id)
            .where(
                Study.deleted_at.is_(None),
                Book.deleted_at.is_(None),
            )
        )

        if book_id is not None:
            base_stmt = base_stmt.where(Book.id == book_id)

        if category_id is not None:
            base_stmt = base_stmt.where(
                Book.id.in_(
                    select(book_categories.c.book_id).where(book_categories.c.category_id == category_id)
                )
            )

        # Condição de termos (AND ou OR)
        term_conditions = [build_term_condition(t) for t in terms]
        if mode == "and":
            active_condition = and_(*term_conditions)
        else:
            active_condition = or_(*term_conditions)

        search_stmt = base_stmt.where(active_condition).order_by(Study.updated_at.desc()).limit(limit)
        rows = session.execute(search_stmt).all()

        results: list[SearchMatchItem] = []
        for study, b_id, b_title, c_id, c_name in rows:
            label, content_for_snippet = determine_matched_field(study, b_title, c_name, terms)
            snippet = generate_snippet(content_for_snippet, terms)
            results.append(
                SearchMatchItem(
                    study_id=study.id,
                    study_title=study.title,
                    book_id=b_id,
                    book_title=b_title,
                    chapter_id=c_id,
                    chapter_name=c_name,
                    reading_status=study.reading_status or "rascunho",
                    matched_field=label,
                    snippet=snippet,
                    updated_at=study.updated_at,
                )
            )

        suggest_or = False
        if mode == "and" and len(results) == 0 and len(terms) > 1:
            # Verifica se uma busca OR retornaria algum resultado
            or_check_stmt = base_stmt.where(or_(*term_conditions)).limit(1)
            or_has_results = session.execute(or_check_stmt).first() is not None
            if or_has_results:
                suggest_or = True

        # Registra no histórico se houve resultados
        if len(results) > 0:
            try:
                SearchService.record_search_query(session, clean_q)
            except Exception:
                # Falha no histórico não pode quebrar a busca
                session.rollback()

        return SearchResponse(
            query=clean_q,
            mode=mode,
            total=len(results),
            results=results,
            suggest_or=suggest_or,
        )

    @staticmethod
    def record_search_query(session: Session, query: str) -> SearchHistory:
        """Registra ou atualiza um termo no histórico com retenção máxima de 10 registros."""
        clean_q = query.strip()
        if not clean_q:
            raise ValueError("O termo de busca não pode ser vazio.")

        now = datetime.now(timezone.utc)
        history_item = session.execute(
            select(SearchHistory).where(SearchHistory.query == clean_q)
        ).scalar_one_or_none()

        if history_item is not None:
            history_item.updated_at = now
        else:
            history_item = SearchHistory(query=clean_q, created_at=now, updated_at=now)
            session.add(history_item)

        session.commit()
        session.refresh(history_item)

        # Política de retenção de 10 itens
        all_ids = session.execute(
            select(SearchHistory.id).order_by(SearchHistory.updated_at.desc())
        ).scalars().all()

        if len(all_ids) > 10:
            to_delete_ids = all_ids[10:]
            session.execute(
                delete(SearchHistory).where(SearchHistory.id.in_(to_delete_ids))
            )
            session.commit()

        return history_item

    @staticmethod
    def get_recent_searches(session: Session, limit: int = 10) -> SearchHistoryResponse:
        """Retorna as buscas mais recentes em ordem cronológica decrescente."""
        stmt = select(SearchHistory).order_by(SearchHistory.updated_at.desc()).limit(limit)
        items = session.execute(stmt).scalars().all()
        return SearchHistoryResponse(
            items=[
                SearchHistoryItem(
                    id=item.id,
                    query=item.query,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
                for item in items
            ]
        )

    @staticmethod
    def delete_search_query(session: Session, history_id: int) -> bool:
        """Remove um item específico do histórico."""
        item = session.get(SearchHistory, history_id)
        if item is None:
            return False
        session.delete(item)
        session.commit()
        return True

    @staticmethod
    def clear_all_searches(session: Session) -> int:
        """Esvazia todo o histórico de buscas."""
        result = session.execute(delete(SearchHistory))
        session.commit()
        return result.rowcount or 0
