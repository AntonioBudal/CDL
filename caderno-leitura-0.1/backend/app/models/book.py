from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.chapter import Chapter


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
        CheckConstraint("year IS NULL OR (year >= 1000 AND year <= 2100)", name="year_range"),
        Index("ix_books_deleted_at", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    subtitle: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
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
    cover_image: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    chapters: Mapped[list[Chapter]] = relationship(
        back_populates="book",
        order_by="(Chapter.position, Chapter.id)",
        passive_deletes="all",
    )
    categories: Mapped[list[Category]] = relationship(
        "Category",
        secondary="book_categories",
        back_populates="books",
        order_by="Category.path",
    )
