from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        CheckConstraint("profile_visibility IN ('public', 'friends', 'private')", name="chk_profile_visibility"),
        CheckConstraint("dashboard_visibility IN ('public', 'friends', 'private')", name="chk_dashboard_visibility"),
        CheckConstraint("length(trim(username)) >= 3 AND length(trim(username)) <= 30", name="chk_username_length"),
        CheckConstraint("length(trim(display_name)) >= 1 AND length(trim(display_name)) <= 60", name="chk_display_name_length"),
        CheckConstraint("bio IS NULL OR length(bio) <= 280", name="chk_bio_length"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    bio: Mapped[str | None] = mapped_column(
        String(280),
        nullable=True,
    )
    profile_visibility: Mapped[str] = mapped_column(
        String(20),
        default="public",
        server_default=text("'public'"),
        nullable=False,
    )
    dashboard_visibility: Mapped[str] = mapped_column(
        String(20),
        default="private",
        server_default=text("'private'"),
        nullable=False,
    )
    is_discoverable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("1"),
        nullable=False,
    )
    show_reading_stats: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("1"),
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

    user: Mapped[User] = relationship(
        "User",
        back_populates="profile",
    )
