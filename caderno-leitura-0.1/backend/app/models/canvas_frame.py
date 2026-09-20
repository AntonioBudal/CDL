from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.core.config import DEFAULT_OWNER_ID
from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.user import User


class CanvasFrame(Base):
    __tablename__ = "canvas_frames"
    __table_args__ = (
        CheckConstraint("width >= 100.0 AND height >= 80.0", name="ck_canvas_frames_dimensions"),
        Index("ix_canvas_frames_book_id", "book_id"),
        Index("ix_canvas_frames_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=DEFAULT_OWNER_ID,
        server_default=text(f"'{DEFAULT_OWNER_ID}'"),
        nullable=False,
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(32), default="neutral", server_default=text("'neutral'"), nullable=False)
    pos_x: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0.0"), nullable=False)
    pos_y: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0.0"), nullable=False)
    width: Mapped[float] = mapped_column(Float, default=400.0, server_default=text("400.0"), nullable=False)
    height: Mapped[float] = mapped_column(Float, default=300.0, server_default=text("300.0"), nullable=False)
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

    book: Mapped[Book] = relationship(
        "Book",
        backref=backref("canvas_frames", cascade="all, delete-orphan", passive_deletes=True),
        passive_deletes=True,
    )
