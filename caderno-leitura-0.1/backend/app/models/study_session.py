from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import DEFAULT_OWNER_ID
from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.study_highlight import StudyHighlight
    from app.models.user import User


class StudySession(Base):
    __tablename__ = "study_sessions"
    __table_args__ = (
        Index("ix_study_sessions_user_id", "user_id"),
        Index("ix_study_sessions_book_id", "book_id"),
        Index("ix_study_sessions_status", "status"),
        Index("ix_study_sessions_started_at", "started_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=DEFAULT_OWNER_ID,
        server_default=text(f"'{DEFAULT_OWNER_ID}'"),
        nullable=False,
    )
    book_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("books.id", ondelete="SET NULL"),
        nullable=True,
    )
    scope_type: Mapped[str] = mapped_column(
        String(30),
        default="quick",
        server_default=text("'quick'"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="in_progress",
        server_default=text("'in_progress'"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime(),
        nullable=True,
    )
    total_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    completed_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    easy_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    medium_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    hard_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    user: Mapped[User] = relationship("User")
    book: Mapped[Book | None] = relationship("Book")
    items: Mapped[list[StudySessionItem]] = relationship(
        "StudySessionItem",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StudySessionItem.id.asc()",
    )


class StudySessionItem(Base):
    __tablename__ = "study_session_items"
    __table_args__ = (
        Index("ix_study_session_items_session_id", "session_id"),
        Index("ix_study_session_items_highlight_id", "highlight_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    highlight_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study_highlights.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    time_spent_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    answered_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    session: Mapped[StudySession] = relationship("StudySession", back_populates="items")
    highlight: Mapped[StudyHighlight] = relationship("StudyHighlight")
