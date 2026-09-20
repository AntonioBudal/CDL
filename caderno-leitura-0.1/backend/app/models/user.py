from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import CheckConstraint, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.study import Study


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(trim(username)) > 0", name="username_not_blank"),
        CheckConstraint("length(trim(display_name)) > 0", name="display_name_not_blank"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="ativo",
        server_default=text("'ativo'"),
        nullable=False,
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
        onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    books: Mapped[list[Book]] = relationship(
        "Book",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    studies: Mapped[list[Study]] = relationship(
        "Study",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
