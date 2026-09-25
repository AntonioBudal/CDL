from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import DEFAULT_OWNER_ID
from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.study import Study
    from app.models.user import User


class StudyCanvasNode(Base):
    __tablename__ = "study_canvas_nodes"
    __table_args__ = (
        UniqueConstraint("study_id", "book_id", name="uq_canvas_node_study_book"),
        Index("ix_canvas_nodes_book_study", "book_id", "study_id"),
        Index("ix_canvas_nodes_user_id", "user_id"),
        Index("ix_canvas_nodes_sync", "user_id", "updated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=DEFAULT_OWNER_ID,
        server_default=text(f"'{DEFAULT_OWNER_ID}'"),
        nullable=False,
    )
    study_id: Mapped[int] = mapped_column(
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    pos_x: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0.0"), nullable=False)
    pos_y: Mapped[float] = mapped_column(Float, default=0.0, server_default=text("0.0"), nullable=False)
    width: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    height: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    z_index: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    color_tag: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    study: Mapped[Study] = relationship("Study", backref="canvas_node", passive_deletes=True)
    book: Mapped[Book] = relationship("Book", backref="canvas_nodes", passive_deletes=True)
