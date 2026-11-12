"""F0.11.08 (spec 110): Memória do Dia.

Um destaque ou estudo do próprio leitor criado há pelo menos 30 dias. Preferência: mesmo dia e mês em ano anterior
("aniversário"); depois o mesmo dia do mês em mês anterior; senão uma escolha fixa do dia (semente "leitor + data").
Lacunas (``hidden``) ficam de fora para não estragar a revisão; lixeira também.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Book, Chapter, Study, StudyHighlight
from app.schemas.dashboard import DailyMemoryRead

MIN_AGE_DAYS = 30
MAX_TEXT = 280


@dataclass
class _Candidate:
    kind: str
    id: int
    created_local: date
    text: str
    study_id: int
    study_title: str
    book_id: int
    book_title: str
    created_at: datetime


def plain_excerpt(text: str | None, limit: int = MAX_TEXT) -> str:
    value = text or ""
    value = re.sub(r"\[\[conceito:\s*([^\]|]*?)\s*\]\]", r"\1", value, flags=re.I)
    value = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", r"\1", value)
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", value)
    value = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"^\s{0,3}(#{1,6}|>|[-*+]|\d+[.)])\s+", "", value, flags=re.M)
    value = re.sub(r"[*_`~]+", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= limit:
        return value
    cut = value[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return f"{cut}…"


def _local(value: datetime, offset: timedelta) -> date:
    aware = value if value.tzinfo else value.replace(tzinfo=UTC)
    return (aware.astimezone(UTC) + offset).date()


def _candidates(session: Session, user_id: str, limit_utc: datetime, offset: timedelta) -> list[_Candidate]:
    found: list[_Candidate] = []
    highlights = session.execute(
        select(
            StudyHighlight.id, StudyHighlight.selected_text, StudyHighlight.created_at,
            Study.id, Study.title, Book.id, Book.title,
        )
        .join(Study, StudyHighlight.study_id == Study.id)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            StudyHighlight.user_id == user_id,
            StudyHighlight.kind != "hidden",
            StudyHighlight.created_at <= limit_utc,
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
    ).all()
    for hl_id, text, created, study_id, study_title, book_id, book_title in highlights:
        excerpt = plain_excerpt(text)
        if excerpt:
            found.append(_Candidate("highlight", hl_id, _local(created, offset), excerpt, study_id, study_title,
                                    book_id, book_title, created))
    studies = session.execute(
        select(Study.id, Study.title, Study.summary, Study.explanation, Study.created_at, Book.id, Book.title)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            Study.user_id == user_id,
            Study.created_at <= limit_utc,
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
    ).all()
    for study_id, title, summary, explanation, created, book_id, book_title in studies:
        excerpt = plain_excerpt(summary) or plain_excerpt(explanation)
        if excerpt:
            found.append(_Candidate("study", study_id, _local(created, offset), excerpt, study_id, title,
                                    book_id, book_title, created))
    found.sort(key=lambda c: (c.kind, c.id))
    return found


def daily_memory(
    session: Session, user_id: str, *, tz_offset: int = 0, now: datetime | None = None
) -> DailyMemoryRead | None:
    offset = timedelta(minutes=tz_offset)
    current = now or datetime.now(UTC)
    today = (current.astimezone(UTC) + offset).date()
    candidates = _candidates(session, user_id, current - timedelta(days=MIN_AGE_DAYS), offset)
    if not candidates:
        return None
    rng = random.Random(f"{user_id}:{today.isoformat()}")
    tiers = (
        ("anniversary", [c for c in candidates if (c.created_local.month, c.created_local.day) == (today.month, today.day)
                         and c.created_local.year < today.year]),
        ("month", [c for c in candidates if c.created_local.day == today.day]),
        ("random", candidates),
    )
    for reason, pool in tiers:
        if pool:
            chosen = rng.choice(pool)
            return DailyMemoryRead(
                kind=chosen.kind,
                text=chosen.text,
                study_id=chosen.study_id,
                study_title=chosen.study_title,
                book_id=chosen.book_id,
                book_title=chosen.book_title,
                created_at=chosen.created_at,
                reason=reason,
            )
    return None
