from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.core.config import DEFAULT_OWNER_ID
from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.study import Study
    from app.models.user import User


class StudyHighlight(Base):
    __tablename__ = "study_highlights"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('highlight', 'note', 'quote', 'hidden', 'question')",
            name="chk_highlight_kind",
        ),
        CheckConstraint(
            "section IN ('summary', 'explanation', 'concepts', 'references', 'source_response')",
            name="chk_highlight_section",
        ),
        CheckConstraint("length(trim(selected_text)) > 0", name="chk_highlight_text_not_blank"),
        CheckConstraint("start_offset >= 0", name="chk_highlight_start_offset_non_negative"),
        CheckConstraint("end_offset >= start_offset", name="chk_highlight_offsets_valid"),
        CheckConstraint(
            "last_rating IS NULL OR last_rating IN ('easy', 'medium', 'hard')",
            name="chk_highlight_last_rating",
        ),
        Index("ix_study_highlights_study_id", "study_id"),
        Index("ix_study_highlights_user_id", "user_id"),
        Index("ix_study_highlights_study_section", "study_id", "section"),
        Index("ix_study_highlights_review", "user_id", "kind", "last_reviewed_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=DEFAULT_OWNER_ID,
        server_default=text(f"'{DEFAULT_OWNER_ID}'"),
        nullable=False,
    )
    section: Mapped[str] = mapped_column(String(30), nullable=False)
    start_offset: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    selected_text: Mapped[str] = mapped_column(Text, nullable=False)
    prefix: Mapped[str] = mapped_column(String(150), default="", server_default=text("''"), nullable=False)
    suffix: Mapped[str] = mapped_column(String(150), default="", server_default=text("''"), nullable=False)
    color: Mapped[str] = mapped_column(String(30), default="yellow", server_default=text("'yellow'"), nullable=False)
    kind: Mapped[str] = mapped_column(String(30), default="highlight", server_default=text("'highlight'"), nullable=False)
    note: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    last_rating: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, onupdate=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    study: Mapped[Study] = relationship(
        "Study",
        backref=backref("highlights", cascade="all, delete-orphan", passive_deletes=True),
    )
    user: Mapped[User] = relationship("User")
