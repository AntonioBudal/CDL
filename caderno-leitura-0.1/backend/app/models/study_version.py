from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.study import Study
    from app.models.user import User


class StudyVersion(Base):
    __tablename__ = "study_versions"
    __table_args__ = (
        Index("ix_study_versions_study_id", "study_id"),
        Index("ix_study_versions_user_id", "user_id"),
        Index("ix_study_versions_study_created", "study_id", "created_at"),
        UniqueConstraint("study_id", "version_number", name="uq_study_version_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    concepts: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    references: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    highlights_data: Mapped[str] = mapped_column(Text, default="[]", server_default=text("'[]'"), nullable=False)
    change_summary: Mapped[str] = mapped_column(String(100), default="Edição", server_default=text("'Edição'"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, onupdate=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    study: Mapped[Study] = relationship("Study", back_populates="versions")
    user: Mapped[User | None] = relationship("User")
