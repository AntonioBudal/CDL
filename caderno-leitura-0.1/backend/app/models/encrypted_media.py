from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now


class EncryptedMedia(Base):
    """Imagem do usuário guardada cifrada no cofre (feature 090; arquivo ``vault/<aa>/<id>.enc``).

    Apagar uma mídia nunca toca no estudo nem no livro: ``study_id`` e ``book_id`` usam ``SET NULL``.
    ``byte_size`` (tamanho do ``.enc``) é o que conta na cota. Os campos de retenção são usados na fatia C.
    """

    __tablename__ = "encrypted_media"
    __table_args__ = (
        CheckConstraint("kind IN ('notebook_page', 'avatar', 'cover')", name="ck_encrypted_media_kind"),
        CheckConstraint("status IN ('pending', 'active', 'deleting', 'missing')", name="ck_encrypted_media_status"),
        CheckConstraint("kind = 'notebook_page' OR keep_forever = 0", name="ck_encrypted_media_keep_pages_only"),
        Index("ix_encrypted_media_user_status", "user_id", "status"),
        Index("ix_encrypted_media_status_expires", "status", "expires_at"),
        Index("ix_encrypted_media_study", "study_id"),
        Index("ix_encrypted_media_kind_user", "kind", "user_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(12), nullable=False, default="pending")
    study_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("studies.id", ondelete="SET NULL"), nullable=True)
    book_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("books.id", ondelete="SET NULL"), nullable=True)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    plain_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    width: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    height: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_type: Mapped[str] = mapped_column(String(32), nullable=False, default="image/webp")
    format_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    key_epoch: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    keep_forever: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("0"))
    expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    pending_until: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, server_default=text("CURRENT_TIMESTAMP"), onupdate=utc_now, nullable=False
    )
