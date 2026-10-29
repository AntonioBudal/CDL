from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now


class OrganizerFeedback(Base):
    """Registro ``leitorum-feedback/1`` de um estudo salvo pela digitalização ou depois de organizar (feature 091-B).

    ``payload`` é o JSON do registro: a sugestão do organizador contra as 4 seções salvas e as correções de leitura.
    Fica no banco local, sai junto com o estudo e com a conta (``CASCADE``) e não entra em exportação.
    ``reviewed`` marca organização salva, não revertida: é o que conta para ligar o adaptador (fatia C).
    """

    __tablename__ = "organizer_feedback"
    __table_args__ = (
        CheckConstraint("origin IN ('digitize', 'import')", name="ck_organizer_feedback_origin"),
        UniqueConstraint("study_id", name="uq_organizer_feedback_study"),
        Index("ix_organizer_feedback_user_reviewed", "user_id", "reviewed"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    study_id: Mapped[int] = mapped_column(Integer, ForeignKey("studies.id", ondelete="CASCADE"), nullable=False)
    schema: Mapped[str] = mapped_column(String(32), nullable=False)
    origin: Mapped[str] = mapped_column(String(12), nullable=False)
    reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("0"))
    artifact_sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="", server_default=text("''"))
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )


class OrganizerUserState(Base):
    """Estado incremental do adaptador do organizador, um por usuário (criado na 091-B, usado na fatia C)."""

    __tablename__ = "organizer_user_state"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    artifact_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    reviewed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    state: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, server_default=text("CURRENT_TIMESTAMP"), onupdate=utc_now, nullable=False
    )
