from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.chapter import Chapter


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)

    chapters: Mapped[list[Chapter]] = relationship(
        back_populates="book",
        order_by="(Chapter.position, Chapter.id)",
        passive_deletes="all",
    )
