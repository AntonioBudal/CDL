"""F0.11.08 (spec 110): avaliação dos cartões de conceito, por leitor e chave normalizada do léxico."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now


class ConceptReview(Base):
    __tablename__ = "concept_reviews"
    __table_args__ = (
        CheckConstraint(
            "last_rating IS NULL OR last_rating IN ('easy', 'medium', 'hard')",
            name="chk_concept_review_rating",
        ),
        UniqueConstraint("user_id", "concept_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_key: Mapped[str] = mapped_column(String(200), nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    last_rating: Mapped[str | None] = mapped_column(String(20), nullable=True)
    difficulty_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), onupdate=utc_now, nullable=False
    )
