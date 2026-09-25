from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    active_superclass: Mapped[str] = mapped_column(
        String(30),
        default="mecanica",
        server_default=text("'mecanica'"),
        nullable=False,
    )
    superclass_intensity: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        server_default=text("1.0"),
        nullable=False,
    )
    preferred_view_mode: Mapped[str] = mapped_column(
        String(20),
        default="grid",
        server_default=text("'grid'"),
        nullable=False,
    )
    tree_collapsed_state: Mapped[str] = mapped_column(
        Text,
        default="[]",
        server_default=text("'[]'"),
        nullable=False,
    )
    font_family: Mapped[str] = mapped_column(
        String(30),
        default="garamond",
        server_default=text("'garamond'"),
        nullable=False,
    )
    font_scale: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        server_default=text("1.0"),
        nullable=False,
    )
    theme_mode: Mapped[str] = mapped_column(
        String(20),
        default="dark",
        server_default=text("'dark'"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default=text("1"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    user: Mapped[User] = relationship("User", backref="preferences", uselist=False)
