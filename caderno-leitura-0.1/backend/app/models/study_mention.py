from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.core.config import DEFAULT_OWNER_ID
from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.study import Study
    from app.models.user import User


class StudyMention(Base):
    __tablename__ = "study_mentions"
    __table_args__ = (
        Index("ix_study_mentions_target_user", "target_study_id", "user_id"),
        Index("ix_study_mentions_source_user", "source_study_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=DEFAULT_OWNER_ID,
        server_default=text(f"'{DEFAULT_OWNER_ID}'"),
        nullable=False,
    )
    source_study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    section: Mapped[str] = mapped_column(String(30), nullable=False)
    mention_text: Mapped[str] = mapped_column(Text, nullable=False)
    context_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    source_study: Mapped[Study] = relationship(
        "Study",
        foreign_keys=[source_study_id],
        backref=backref("outbound_mentions", cascade="all, delete-orphan", passive_deletes=True),
        passive_deletes=True,
    )
    target_study: Mapped[Study] = relationship(
        "Study",
        foreign_keys=[target_study_id],
        backref=backref("inbound_mentions", cascade="all, delete-orphan", passive_deletes=True),
        passive_deletes=True,
    )
    user: Mapped[User] = relationship("User")
