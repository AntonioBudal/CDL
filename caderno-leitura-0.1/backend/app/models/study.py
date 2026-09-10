from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.chapter import Chapter


class Study(Base):
    __tablename__ = "studies"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
        CheckConstraint(
            'length(trim(summary || explanation || concepts || "references")) > 0',
            name="analysis_not_blank",
        ),
        Index("ix_studies_chapter_id", "chapter_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id", ondelete="RESTRICT"), nullable=False)
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

    chapter: Mapped[Chapter] = relationship(back_populates="studies")
