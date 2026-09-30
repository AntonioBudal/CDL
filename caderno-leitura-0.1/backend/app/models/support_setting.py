from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class SupportSetting(Base):
    """Configurações globais de apoio financeiro voluntário ao Leitorum (tabela singleton)."""
    __tablename__ = "support_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_support_settings_singleton"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    pix_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"), nullable=False)
    pix_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pix_recipient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pix_qr_code_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    alternative_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"), nullable=False)
    alternative_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    alternative_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=utc_now,
        nullable=False,
    )
    updated_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    updated_by_user: Mapped[User | None] = relationship("User", foreign_keys=[updated_by_user_id])
