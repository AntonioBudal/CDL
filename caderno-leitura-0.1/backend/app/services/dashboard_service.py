from collections import Counter
from datetime import UTC, date, datetime, timedelta
from typing import Sequence

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session, aliased

from app.models.book import Book
from app.models.category import Category
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.study_relation import StudyRelation
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardSummary,
    HeatmapPoint,
    RecentRelationItem,
    RecentStudyActivityItem,
    TimelineItem,
    UnlinkedStudyItem,
)


def get_heatmap_level(count: int) -> int:
    if count == 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    return 3


def calculate_streak(active_dates: set[date], today: date) -> int:
    """Calcula a sequência ininterrupta de dias ativos até hoje.
    
    Se hoje tiver atividade, inicia a contagem a partir de hoje.
    Se hoje não tiver atividade mas ontem tiver, mantém a sequência ativa a partir de ontem.
    Caso contrário, a sequência é 0.
    """
    if today in active_dates:
        start_date = today
    elif (today - timedelta(days=1)) in active_dates:
        start_date = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    curr = start_date
    while curr in active_dates:
        streak += 1
        curr -= timedelta(days=1)
    return streak


def get_dashboard_data(
    session: Session,
    *,
    tz_offset: int = 0,
    days: int = 365,
    filter_date: str | None = None,
    limit: int = 30,
) -> DashboardResponse:
    # 1. Contagem de Livros e Estudos Ativos
    total_books = session.scalar(
        select(func.count(Book.id)).where(Book.deleted_at.is_(None))
    ) or 0

    total_studies = session.scalar(
        select(func.count(Study.id))
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(Study.deleted_at.is_(None), Book.deleted_at.is_(None))
    ) or 0

    avg_studies = round(total_studies / total_books, 1) if total_books > 0 else 0.0

    # 1.1 Contagem de Categorias
    total_categories = session.scalar(select(func.count(Category.id))) or 0

    # 1.2 Aliases para Relações e Integridade de Soft Delete
    SourceStudy = aliased(Study)
    TargetStudy = aliased(Study)
    SourceChapter = aliased(Chapter)
    TargetChapter = aliased(Chapter)
    SourceBook = aliased(Book)
    TargetBook = aliased(Book)

    # 1.3 Total de Relações Semânticas Ativas (ambos os estudos e livros não excluídos)
    total_relations = session.scalar(
        select(func.count(StudyRelation.id))
        .join(SourceStudy, StudyRelation.source_study_id == SourceStudy.id)
        .join(SourceChapter, SourceStudy.chapter_id == SourceChapter.id)
        .join(SourceBook, SourceChapter.book_id == SourceBook.id)
        .join(TargetStudy, StudyRelation.target_study_id == TargetStudy.id)
        .join(TargetChapter, TargetStudy.chapter_id == TargetChapter.id)
        .join(TargetBook, TargetChapter.book_id == TargetBook.id)
        .where(
            SourceStudy.deleted_at.is_(None),
            SourceBook.deleted_at.is_(None),
            TargetStudy.deleted_at.is_(None),
            TargetBook.deleted_at.is_(None),
        )
    ) or 0

    # 1.4 Estudos Órfãos (sem conexões ativas)
    has_active_relation = exists(
        select(1)
        .select_from(StudyRelation)
        .join(SourceStudy, StudyRelation.source_study_id == SourceStudy.id)
        .join(SourceChapter, SourceStudy.chapter_id == SourceChapter.id)
        .join(SourceBook, SourceChapter.book_id == SourceBook.id)
        .join(TargetStudy, StudyRelation.target_study_id == TargetStudy.id)
        .join(TargetChapter, TargetStudy.chapter_id == TargetChapter.id)
        .join(TargetBook, TargetChapter.book_id == TargetBook.id)
        .where(
            (StudyRelation.source_study_id == Study.id) | (StudyRelation.target_study_id == Study.id),
            SourceStudy.deleted_at.is_(None),
            SourceBook.deleted_at.is_(None),
            TargetStudy.deleted_at.is_(None),
            TargetBook.deleted_at.is_(None),
        )
    )

    unlinked_studies_count = session.scalar(
        select(func.count(Study.id))
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
            ~has_active_relation,
        )
    ) or 0

    # 1.5 Amostra de Estudos Órfãos para Enriquecimento (até 10)
    unlinked_stmt = (
        select(
            Study.id.label("study_id"),
            Study.title.label("title"),
            Book.id.label("book_id"),
            Book.title.label("book_title"),
            Chapter.id.label("chapter_id"),
            Chapter.name.label("chapter_title"),
            Study.reading_status.label("reading_status"),
            Study.created_at.label("created_at"),
        )
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
            ~has_active_relation,
        )
        .order_by(Study.updated_at.desc())
        .limit(10)
    )
    unlinked_studies = [
        UnlinkedStudyItem(
            study_id=row.study_id,
            title=row.title,
            book_id=row.book_id,
            book_title=row.book_title,
            chapter_id=row.chapter_id,
            chapter_title=row.chapter_title,
            reading_status=row.reading_status or "rascunho",
            created_at=row.created_at if row.created_at.tzinfo is not None else row.created_at.replace(tzinfo=UTC),
        )
        for row in session.execute(unlinked_stmt)
    ]

    # 1.6 Estudos Recentes para Retoma Rápida (ordenados por updated_at DESC, até 10)
    recent_studies_stmt = (
        select(
            Study.id.label("study_id"),
            Study.title.label("title"),
            Book.id.label("book_id"),
            Book.title.label("book_title"),
            Chapter.id.label("chapter_id"),
            Chapter.name.label("chapter_title"),
            Study.reading_status.label("reading_status"),
            Study.updated_at.label("updated_at"),
        )
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
        )
        .order_by(Study.updated_at.desc())
        .limit(10)
    )
    recent_studies = [
        RecentStudyActivityItem(
            study_id=row.study_id,
            title=row.title,
            book_id=row.book_id,
            book_title=row.book_title,
            chapter_id=row.chapter_id,
            chapter_title=row.chapter_title,
            reading_status=row.reading_status or "rascunho",
            updated_at=row.updated_at if row.updated_at.tzinfo is not None else row.updated_at.replace(tzinfo=UTC),
        )
        for row in session.execute(recent_studies_stmt)
    ]

    # 1.7 Conexões Semânticas Recentes (até 10)
    latest_relations_stmt = (
        select(
            StudyRelation.id.label("relation_id"),
            StudyRelation.relation_type.label("relation_type"),
            StudyRelation.description.label("description"),
            StudyRelation.created_at.label("created_at"),
            SourceStudy.id.label("source_study_id"),
            SourceStudy.title.label("source_study_title"),
            SourceBook.id.label("source_book_id"),
            SourceBook.title.label("source_book_title"),
            TargetStudy.id.label("target_study_id"),
            TargetStudy.title.label("target_study_title"),
            TargetBook.id.label("target_book_id"),
            TargetBook.title.label("target_book_title"),
        )
        .join(SourceStudy, StudyRelation.source_study_id == SourceStudy.id)
        .join(SourceChapter, SourceStudy.chapter_id == SourceChapter.id)
        .join(SourceBook, SourceChapter.book_id == SourceBook.id)
        .join(TargetStudy, StudyRelation.target_study_id == TargetStudy.id)
        .join(TargetChapter, TargetStudy.chapter_id == TargetChapter.id)
        .join(TargetBook, TargetChapter.book_id == TargetBook.id)
        .where(
            SourceStudy.deleted_at.is_(None),
            SourceBook.deleted_at.is_(None),
            TargetStudy.deleted_at.is_(None),
            TargetBook.deleted_at.is_(None),
        )
        .order_by(StudyRelation.created_at.desc())
        .limit(10)
    )
    latest_relations = [
        RecentRelationItem(
            relation_id=row.relation_id,
            relation_type=row.relation_type,
            description=row.description,
            source_study_id=row.source_study_id,
            source_study_title=row.source_study_title,
            source_book_id=row.source_book_id,
            source_book_title=row.source_book_title,
            target_study_id=row.target_study_id,
            target_study_title=row.target_study_title,
            target_book_id=row.target_book_id,
            target_book_title=row.target_book_title,
            created_at=row.created_at if row.created_at.tzinfo is not None else row.created_at.replace(tzinfo=UTC),
        )
        for row in session.execute(latest_relations_stmt)
    ]

    # 2. Coleta de Eventos para Métricas, Heatmap e Timeline
    offset_delta = timedelta(minutes=tz_offset)
    now_utc = datetime.now(UTC)
    local_today = (now_utc + offset_delta).date()

    all_events: list[TimelineItem] = []

    # 2.1 Livros criados
    books_stmt = select(Book.id, Book.title, Book.created_at).where(Book.deleted_at.is_(None))
    for book_id, book_title, created_at in session.execute(books_stmt):
        ts = created_at if created_at.tzinfo is not None else created_at.replace(tzinfo=UTC)
        all_events.append(
            TimelineItem(
                id=f"book-{book_id}-created",
                entity_type="book",
                action="book_created",
                timestamp=ts,
                title=book_title,
                book_id=book_id,
                book_title=book_title,
                chapter_id=None,
                chapter_title=None,
                study_id=None,
            )
        )

    # 2.2 Estudos criados e editados
    studies_stmt = (
        select(
            Study.id,
            Study.title,
            Study.created_at,
            Study.updated_at,
            Book.id.label("book_id"),
            Book.title.label("book_title"),
            Chapter.id.label("chapter_id"),
            Chapter.name.label("chapter_title"),
        )
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(Study.deleted_at.is_(None), Book.deleted_at.is_(None))
    )
    for row in session.execute(studies_stmt):
        c_ts = row.created_at if row.created_at.tzinfo is not None else row.created_at.replace(tzinfo=UTC)
        all_events.append(
            TimelineItem(
                id=f"study-{row.id}-created",
                entity_type="study",
                action="study_created",
                timestamp=c_ts,
                title=row.title,
                book_id=row.book_id,
                book_title=row.book_title,
                chapter_id=row.chapter_id,
                chapter_title=row.chapter_title,
                study_id=row.id,
            )
        )

        # Edição de anotação/estudo com mais de 60 segundos de intervalo
        if row.updated_at:
            u_ts = row.updated_at if row.updated_at.tzinfo is not None else row.updated_at.replace(tzinfo=UTC)
            if (u_ts - c_ts).total_seconds() > 60:
                all_events.append(
                    TimelineItem(
                        id=f"study-{row.id}-updated",
                        entity_type="study",
                        action="study_updated",
                        timestamp=u_ts,
                        title=row.title,
                        book_id=row.book_id,
                        book_title=row.book_title,
                        chapter_id=row.chapter_id,
                        chapter_title=row.chapter_title,
                        study_id=row.id,
                    )
                )

    # 3. Mapeamento por data local civil
    date_counts: Counter[str] = Counter()
    active_dates: set[date] = set()

    for ev in all_events:
        ev_local_date = (ev.timestamp + offset_delta).date()
        active_dates.add(ev_local_date)
        date_counts[ev_local_date.isoformat()] += 1

    total_reading_days = len(active_dates)
    current_streak = calculate_streak(active_dates, local_today)

    summary = DashboardSummary(
        total_books=total_books,
        total_studies=total_studies,
        total_reading_days=total_reading_days,
        current_streak=current_streak,
        avg_studies_per_book=avg_studies,
        total_relations=total_relations,
        total_categories=total_categories,
        unlinked_studies_count=unlinked_studies_count,
    )

    # 4. Construção do Heatmap (cronológico: do mais antigo para hoje)
    heatmap: list[HeatmapPoint] = []
    start_date = local_today - timedelta(days=days - 1)
    for i in range(days):
        d = start_date + timedelta(days=i)
        d_str = d.isoformat()
        count = date_counts.get(d_str, 0)
        heatmap.append(
            HeatmapPoint(
                date=d_str,
                count=count,
                level=get_heatmap_level(count),
            )
        )

    # 5. Filtragem e ordenação da Timeline
    filtered_events = all_events
    if filter_date:
        filtered_events = [
            ev for ev in all_events
            if (ev.timestamp + offset_delta).date().isoformat() == filter_date
        ]

    # Ordenação cronológica decrescente (mais recente primeiro)
    filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
    timeline = filtered_events[:limit]

    return DashboardResponse(
        summary=summary,
        heatmap=heatmap,
        timeline=timeline,
        recent_studies=recent_studies,
        unlinked_studies=unlinked_studies,
        latest_relations=latest_relations,
    )
