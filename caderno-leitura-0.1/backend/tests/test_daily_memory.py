"""F0.11.08 (spec 110): Memória do Dia. Só dados fictícios; banco em tmp_path."""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.db.base import Base
from app.models import Book, Chapter, Study, StudyHighlight, User
from app.services.daily_memory import daily_memory, plain_excerpt

NOW = datetime(2026, 11, 12, 15, tzinfo=UTC)


def _session(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 'memoria.db').as_posix()}")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    session.add(User(id=DEFAULT_OWNER_ID, username=DEFAULT_OWNER_USERNAME, display_name="Dona Fictícia", role="admin",
                     status="ativo"))
    session.add(User(id="outro", username="outro", display_name="Outro Fictício", role="user", status="ativo"))
    session.commit()
    return session


def _study(session, created, user=DEFAULT_OWNER_ID, summary="Resumo **fictício** com [[conceito:Mímese]].", book_title="Livro de Teste"):
    book = Book(user_id=user, title=book_title)
    session.add(book)
    session.flush()
    chapter = Chapter(book_id=book.id, name="Capítulo 1", position=0)
    session.add(chapter)
    session.flush()
    study = Study(user_id=user, chapter_id=chapter.id, title="Estudo de Teste", summary=summary, created_at=created)
    session.add(study)
    session.commit()
    return book, study


def _highlight(session, study, created, text="Trecho fictício destacado.", kind="highlight"):
    hl = StudyHighlight(study_id=study.id, user_id=study.user_id, section="summary", selected_text=text, kind=kind,
                        created_at=created)
    session.add(hl)
    session.commit()
    return hl


def test_plain_excerpt():
    assert plain_excerpt("- **Termo** e [[conceito:Mímese]] e [[Outro|3]]") == "Termo e Mímese e Outro"
    long = "palavra " * 80
    out = plain_excerpt(long)
    assert len(out) <= 280 and out.endswith("…")


def test_nothing_old_enough_returns_none(tmp_path):
    session = _session(tmp_path)
    assert daily_memory(session, DEFAULT_OWNER_ID, now=NOW) is None
    _study(session, datetime(2026, 10, 20, tzinfo=UTC))
    assert daily_memory(session, DEFAULT_OWNER_ID, now=NOW) is None, "menos de 30 dias"


def test_anniversary_then_month_then_stable_random(tmp_path):
    session = _session(tmp_path)
    _, random_study = _study(session, datetime(2026, 3, 3, tzinfo=UTC))
    _, month_study = _study(session, datetime(2026, 8, 12, 10, tzinfo=UTC), summary="Do mesmo dia do mês.")
    first = daily_memory(session, DEFAULT_OWNER_ID, now=NOW)
    assert (first.reason, first.study_id, first.text) == ("month", month_study.id, "Do mesmo dia do mês.")

    _, anniversary = _study(session, datetime(2025, 11, 12, 9, tzinfo=UTC))
    hl = _highlight(session, anniversary, datetime(2025, 11, 12, 9, tzinfo=UTC), text="Lacuna escondida.", kind="hidden")
    got = daily_memory(session, DEFAULT_OWNER_ID, now=NOW)
    assert got.reason == "anniversary" and got.kind == "study" and got.study_id == anniversary.id
    assert got.text == "Resumo fictício com Mímese."
    assert "Lacuna" not in got.text, "lacuna fica de fora"
    session.delete(hl)
    _highlight(session, anniversary, datetime(2025, 11, 12, 9, tzinfo=UTC))
    picks = {daily_memory(session, DEFAULT_OWNER_ID, now=NOW).kind for _ in range(3)}
    assert len(picks) == 1, "a escolha do dia é estável"

    # sem aniversário nem mês: sorteio fixo do dia
    other_day = datetime(2026, 11, 13, 15, tzinfo=UTC)
    again = [daily_memory(session, DEFAULT_OWNER_ID, now=other_day) for _ in range(3)]
    assert {a.reason for a in again} == {"random"} and len({(a.kind, a.study_id) for a in again}) == 1
    assert random_study.id in {s.id for s in session.query(Study).all()}


def test_trash_and_other_users_are_excluded(tmp_path):
    session = _session(tmp_path)
    _study(session, datetime(2025, 11, 12, tzinfo=UTC), user="outro")
    assert daily_memory(session, DEFAULT_OWNER_ID, now=NOW) is None
    _, study = _study(session, datetime(2025, 11, 12, tzinfo=UTC))
    session.execute(update(Study).where(Study.id == study.id).values(deleted_at=NOW))
    session.commit()
    assert daily_memory(session, DEFAULT_OWNER_ID, now=NOW) is None


def test_local_date_uses_tz_offset(tmp_path):
    session = _session(tmp_path)
    # 12/11/2025 01:00 UTC é 11/11 às 22:00 em UTC-3
    _study(session, datetime(2025, 11, 12, 1, tzinfo=UTC))
    late = datetime(2026, 11, 12, 1, 30, tzinfo=UTC)  # 11/11 às 22:30 em UTC-3
    assert daily_memory(session, DEFAULT_OWNER_ID, tz_offset=-180, now=late).reason == "anniversary"
    assert daily_memory(session, DEFAULT_OWNER_ID, tz_offset=0, now=late).reason == "anniversary"
    assert daily_memory(session, DEFAULT_OWNER_ID, tz_offset=-180, now=NOW).reason != "anniversary"
