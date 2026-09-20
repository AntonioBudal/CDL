from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import DEFAULT_OWNER_ID
from app.db.base import Base
from app.db.types import UTCDateTime, utc_now


class SearchHistory(Base):
    __tablename__ = "search_history"
    __table_args__ = (
        Index("ix_search_history_user_query", "user_id", "query", unique=True),
        Index("ix_search_history_user_updated", "user_id", "updated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=DEFAULT_OWNER_ID,
        server_default=text(f"'{DEFAULT_OWNER_ID}'"),
        nullable=False,
    )
    query: Mapped[str] = mapped_column(String(255), nullable=False)
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
