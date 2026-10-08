"""Serviço de gerenciamento de Sessões Estruturadas de Estudo (F0.7.14)."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.book import Book
from app.models.study_highlight import StudyHighlight
from app.models.study_session import StudySession, StudySessionItem
from app.schemas.review import ReviewItemRead
from app.schemas.study_session import (
    StudySessionDetailResponse,
    StudySessionItemResponse,
    StudySessionResponse,
    StudySessionSummaryResponse,
)
from app.services.persistence import commit_changes
from app.services.review_service import get_review_items, record_review_rating


def _to_session_response(study_session: StudySession) -> StudySessionResponse:
    book_title = study_session.book.title if study_session.book else None
    return StudySessionResponse(
        id=study_session.id,
        user_id=study_session.user_id,
        book_id=study_session.book_id,
        book_title=book_title,
        scope_type=study_session.scope_type,  # type: ignore[arg-type]
        status=study_session.status,  # type: ignore[arg-type]
        started_at=study_session.started_at,
        completed_at=study_session.completed_at,
        total_items=study_session.total_items,
        completed_items=study_session.completed_items,
        easy_count=study_session.easy_count,
        medium_count=study_session.medium_count,
        hard_count=study_session.hard_count,
        duration_seconds=study_session.duration_seconds,
    )


def start_study_session(
    session: Session,
    user_id: str,
    scope_type: str = "quick",
    book_id: int | None = None,
    limit: int = 10,
) -> StudySessionDetailResponse:
    """Inicializa um bloco delimitado de estudo com escopo definido e seleção de cartões."""
    safe_limit = min(max(1, limit), 100)
    target_book_id = book_id if scope_type == "book" else None

    # Busca cartões elegíveis de active recall priorizados
    items = get_review_items(
        session=session,
        user_id=user_id,
        book_id=target_book_id,
        limit=safe_limit,
    )

    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum item pendente de revisão encontrado para este escopo.",
        )

    # Criação da sessão com total dinâmico de itens
    study_session = StudySession(
        user_id=user_id,
        book_id=target_book_id,
        scope_type=scope_type,
        status="in_progress",
        started_at=utc_now(),
        total_items=len(items),
        completed_items=0,
        easy_count=0,
        medium_count=0,
        hard_count=0,
        duration_seconds=0,
    )
    session.add(study_session)
    commit_changes(session)
    session.refresh(study_session)

    base_response = _to_session_response(study_session)
    return StudySessionDetailResponse(
        **base_response.model_dump(),
        items=[],
        pending_cards=items,
    )


def get_study_session(
    session: Session,
    user_id: str,
    session_id: int,
) -> StudySessionDetailResponse:
    """Retorna os detalhes e cartões de uma sessão de estudo."""
    stmt = select(StudySession).where(
        StudySession.id == session_id,
        StudySession.user_id == user_id,
    )
    study_session = session.scalar(stmt)
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de estudo não encontrada.",
        )

    answered_items = [
        StudySessionItemResponse.model_validate(it) for it in study_session.items
    ]

    pending_cards: list[ReviewItemRead] = []
    if study_session.status == "in_progress":
        answered_hl_ids = {it.highlight_id for it in study_session.items}
        all_candidates = get_review_items(
            session=session,
            user_id=user_id,
            book_id=study_session.book_id if study_session.scope_type == "book" else None,
            limit=study_session.total_items + len(answered_hl_ids),
        )
        pending_cards = [c for c in all_candidates if c.id not in answered_hl_ids]
        # Limita ao restante dos itens previstos
        remaining_needed = max(0, study_session.total_items - len(answered_items))
        pending_cards = pending_cards[:remaining_needed]

    base_response = _to_session_response(study_session)
    return StudySessionDetailResponse(
        **base_response.model_dump(),
        items=answered_items,
        pending_cards=pending_cards,
    )


def record_session_item(
    session: Session,
    user_id: str,
    session_id: int,
    highlight_id: int,
    rating: str,
    time_spent_seconds: int = 0,
) -> StudySessionItemResponse:
    """Registra atomicamente a resposta a um cartão, avançando a repetição espaçada."""
    if rating not in ("easy", "medium", "hard"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Classificação inválida. Deve ser 'easy', 'medium' ou 'hard'.",
        )

    stmt = select(StudySession).where(
        StudySession.id == session_id,
        StudySession.user_id == user_id,
    )
    study_session = session.scalar(stmt)
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de estudo não encontrada.",
        )

    if study_session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A sessão já foi finalizada ou interrompida.",
        )

    # Atualiza atomicamente os carimbos em study_highlights
    record_review_rating(
        session=session,
        user_id=user_id,
        highlight_id=highlight_id,
        rating=rating,
    )

    # Cria o registro do item na sessão
    safe_time = max(0, time_spent_seconds)
    item = StudySessionItem(
        session_id=study_session.id,
        highlight_id=highlight_id,
        rating=rating,
        time_spent_seconds=safe_time,
        answered_at=utc_now(),
    )
    session.add(item)

    # Atualiza contadores acumulados da sessão
    study_session.completed_items += 1
    study_session.duration_seconds += safe_time
    if rating == "easy":
        study_session.easy_count += 1
    elif rating == "medium":
        study_session.medium_count += 1
    elif rating == "hard":
        study_session.hard_count += 1

    # Se completou todos os itens planejados, fecha formalmente
    if study_session.completed_items >= study_session.total_items:
        study_session.status = "completed"
        study_session.completed_at = utc_now()

    commit_changes(session)
    session.refresh(item)
    return StudySessionItemResponse.model_validate(item)


def complete_study_session(
    session: Session,
    user_id: str,
    session_id: int,
    duration_seconds: int | None = None,
) -> StudySessionSummaryResponse:
    """Conclui formalmente a sessão de estudo e retorna seu resumo estatístico consolidado."""
    stmt = select(StudySession).where(
        StudySession.id == session_id,
        StudySession.user_id == user_id,
    )
    study_session = session.scalar(stmt)
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de estudo não encontrada.",
        )

    if study_session.status == "in_progress":
        study_session.status = "completed"
        study_session.completed_at = utc_now()

    if duration_seconds is not None and duration_seconds > 0:
        study_session.duration_seconds = duration_seconds

    commit_changes(session)
    session.refresh(study_session)

    return get_study_session_summary(session, user_id, session_id)


def interrupt_study_session(
    session: Session,
    user_id: str,
    session_id: int,
) -> StudySessionResponse:
    """Marca uma sessão como interrompida preservando os itens já respondidos (Q1: A)."""
    stmt = select(StudySession).where(
        StudySession.id == session_id,
        StudySession.user_id == user_id,
    )
    study_session = session.scalar(stmt)
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de estudo não encontrada.",
        )

    if study_session.status == "in_progress":
        study_session.status = "interrupted"
        study_session.completed_at = utc_now()
        commit_changes(session)
        session.refresh(study_session)

    return _to_session_response(study_session)


def get_study_session_summary(
    session: Session,
    user_id: str,
    session_id: int,
) -> StudySessionSummaryResponse:
    """Calcula e retorna o resumo consolidado de auditoria e aprendizado da sessão."""
    stmt = select(StudySession).where(
        StudySession.id == session_id,
        StudySession.user_id == user_id,
    )
    study_session = session.scalar(stmt)
    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de estudo não encontrada.",
        )

    total_answered = study_session.completed_items
    if total_answered > 0:
        # Ponderação de retenção: Fácil (100%), Médio (75%), Difícil (25%)
        raw_score = (
            study_session.easy_count * 1.0
            + study_session.medium_count * 0.75
            + study_session.hard_count * 0.25
        )
        accuracy_rate = round((raw_score / total_answered) * 100, 1)
    else:
        accuracy_rate = 0.0

    next_reviews_summary = {
        "easy": study_session.easy_count,
        "medium": study_session.medium_count,
        "hard": study_session.hard_count,
    }

    return StudySessionSummaryResponse(
        session=_to_session_response(study_session),
        accuracy_rate=accuracy_rate,
        next_reviews_summary=next_reviews_summary,
    )


def get_study_sessions_history(
    session: Session,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
) -> list[StudySessionResponse]:
    """Retorna histórico de sessões do usuário com ordenação cronológica decrescente."""
    safe_limit = min(max(1, limit), 100)
    safe_offset = max(0, offset)

    stmt = (
        select(StudySession)
        .where(StudySession.user_id == user_id)
        .order_by(StudySession.started_at.desc())
        .limit(safe_limit)
        .offset(safe_offset)
    )
    sessions = session.scalars(stmt).all()
    return [_to_session_response(s) for s in sessions]
