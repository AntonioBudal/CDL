from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import DEFAULT_OWNER_ID
from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.chapter import Chapter
    from app.models.user import User


class Study(Base):
    __tablename__ = "studies"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
        CheckConstraint(
            'length(trim(summary || explanation || concepts || "references")) > 0',
            name="analysis_not_blank",
        ),
        Index("ix_studies_chapter_id", "chapter_id"),
        Index("ix_studies_deleted_at", "deleted_at"),
        Index("ix_studies_parent_study_id", "parent_study_id"),
        Index("ix_studies_chapter_parent_position", "chapter_id", "parent_study_id", "position"),
        Index("ix_studies_reading_status", "reading_status"),
        Index("ix_studies_user_id", "user_id"),
        Index("ix_studies_user_deleted", "user_id", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=DEFAULT_OWNER_ID,
        server_default=text(f"'{DEFAULT_OWNER_ID}'"),
        nullable=False,
    )
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id", ondelete="RESTRICT"), nullable=False)
    parent_study_id: Mapped[int | None] = mapped_column(ForeignKey("studies.id", ondelete="SET NULL"), nullable=True)
    position: Mapped[int] = mapped_column(default=0, server_default=text("0"), nullable=False)
    reading_status: Mapped[str] = mapped_column(String(20), default="rascunho", server_default=text("'rascunho'"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    source_response: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    concepts: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    references: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"), nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime(), default=None, server_default=None, nullable=True
    )

    chapter: Mapped[Chapter] = relationship(back_populates="studies")
    parent: Mapped[Study | None] = relationship("Study", remote_side="Study.id", back_populates="children")
    children: Mapped[list[Study]] = relationship("Study", back_populates="parent", order_by="Study.position")
    user: Mapped[User] = relationship(back_populates="studies")
