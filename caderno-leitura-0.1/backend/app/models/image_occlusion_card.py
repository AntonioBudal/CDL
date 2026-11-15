"""F0.12.06 (spec 119): cartões de oclusão de imagem — um retângulo sobre uma imagem do estudo é um cartão de revisão.

Coordenadas relativas (0–1 da largura e da altura da imagem), então valem em qualquer tamanho de tela. Os campos de
revisão são os mesmos dos cartões de conceito (nota, contagem e peso de dificuldade).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now


class ImageOcclusionCard(Base):
    __tablename__ = "image_occlusion_cards"
    __table_args__ = (
        CheckConstraint(
            "x >= 0 AND y >= 0 AND width > 0 AND height > 0 AND x + width <= 1.000001 AND y + height <= 1.000001",
            name="chk_occlusion_box",
        ),
        CheckConstraint(
            "last_rating IS NULL OR last_rating IN ('easy', 'medium', 'hard')",
            name="chk_occlusion_rating",
        ),
        Index("ix_image_occlusion_cards_media_id", "media_id"),
        Index("ix_image_occlusion_cards_user_id", "user_id"),
        Index("ix_image_occlusion_cards_study_id", "study_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    study_id: Mapped[int] = mapped_column(Integer, ForeignKey("studies.id", ondelete="CASCADE"), nullable=False)
    media_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("encrypted_media.id", ondelete="CASCADE"), nullable=False
    )
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    label: Mapped[str] = mapped_column(String(200), default="", server_default=text("''"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
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
