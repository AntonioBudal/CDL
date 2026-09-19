from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, Table, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.book import Book

book_categories = Table(
    "book_categories",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Text, ForeignKey("categories.id", ondelete="RESTRICT"), primary_key=True),
    Index("ix_book_categories_category_book", "category_id", "book_id"),
)


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint("length(trim(id)) > 0", name="category_id_not_blank"),
        CheckConstraint("length(trim(name)) > 0", name="category_name_not_blank"),
        Index("ix_categories_parent_id", "parent_id"),
        Index("ix_categories_path", "path"),
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True, default=None
    )
    path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    parent: Mapped[Category | None] = relationship(
        "Category", remote_side=[id], back_populates="children"
    )
    children: Mapped[list[Category]] = relationship(
        "Category", back_populates="parent", order_by="Category.name"
    )
    books: Mapped[list[Book]] = relationship(
        "Book", secondary=book_categories, back_populates="categories"
    )
