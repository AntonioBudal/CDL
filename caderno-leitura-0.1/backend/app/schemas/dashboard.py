from datetime import datetime

from app.schemas.common import OutputModel


class DashboardSummary(OutputModel):
    total_books: int = 0
    total_studies: int = 0
    total_reading_days: int = 0
    current_streak: int = 0
    avg_studies_per_book: float = 0.0
    total_relations: int = 0
    total_categories: int = 0
    unlinked_studies_count: int = 0


class RecentStudyActivityItem(OutputModel):
    study_id: int
    title: str
    book_id: int
    book_title: str
    chapter_id: int | None = None
    chapter_title: str | None = None
    reading_status: str = "rascunho"
    updated_at: datetime


class UnlinkedStudyItem(OutputModel):
    study_id: int
    title: str
    book_id: int
    book_title: str
    chapter_id: int | None = None
    chapter_title: str | None = None
    reading_status: str = "rascunho"
    created_at: datetime


class RecentRelationItem(OutputModel):
    relation_id: int
    relation_type: str
    description: str | None = None
    source_study_id: int
    source_study_title: str
    source_book_id: int
    source_book_title: str
    target_study_id: int
    target_study_title: str
    target_book_id: int
    target_book_title: str
    created_at: datetime


class HeatmapPoint(OutputModel):
    date: str
    count: int = 0
    level: int = 0


class TimelineItem(OutputModel):
    id: str
    entity_type: str
    action: str
    timestamp: datetime
    title: str
    book_id: int
    book_title: str
    chapter_id: int | None = None
    chapter_title: str | None = None
    study_id: int | None = None


class DashboardResponse(OutputModel):
    summary: DashboardSummary
    heatmap: list[HeatmapPoint]
    timeline: list[TimelineItem]
    recent_studies: list[RecentStudyActivityItem] = []
    unlinked_studies: list[UnlinkedStudyItem] = []
    latest_relations: list[RecentRelationItem] = []

