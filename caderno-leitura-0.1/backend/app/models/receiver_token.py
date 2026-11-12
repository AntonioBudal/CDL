"""F0.11.09 (spec 111): token de recepção de destaques (um por leitor; só o hash é guardado)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now


class ReceiverToken(Base):
    __tablename__ = "receiver_tokens"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    token_hint: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
