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
    from app.models.study import Study
    from app.models.user import User


class InboxCapture(Base):
    __tablename__ = "inbox_captures"
    __table_args__ = (
        Index("ix_inbox_captures_user_status", "user_id", "status"),
        Index("ix_inbox_captures_user_created", "user_id", "created_at"),
        Index("ix_inbox_captures_book_id", "book_id"),
        Index("ix_inbox_captures_promoted_study", "promoted_study_id"),
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
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="inbox",
        server_default=text("'inbox'"),
        nullable=False,
    )
    promoted_study_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("studies.id", ondelete="SET NULL"),
        nullable=True,
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
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped[User] = relationship("User")
    book: Mapped[Book | None] = relationship("Book")
    promoted_study: Mapped[Study | None] = relationship("Study")
