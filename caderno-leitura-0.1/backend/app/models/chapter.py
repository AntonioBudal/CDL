from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.study import Study


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="name_not_blank"),
        CheckConstraint("position >= 0", name="position_non_negative"),
        Index("ix_chapters_book_id_position", "book_id", "position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(default=0, server_default=text("0"), nullable=False)

    book: Mapped[Book] = relationship(back_populates="chapters")
    studies: Mapped[list[Study]] = relationship(
        back_populates="chapter", order_by="Study.id", passive_deletes="all"
    )
