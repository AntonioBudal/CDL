from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class ResourcePermission(Base):
    """Modelo relacional de controle de acesso nominal (ACL) por recurso.

    Permite concessões nominais de leitura para estudos ou livros para a granularidade 'custom'.
    """

    __tablename__ = "resource_permissions"
    __table_args__ = (
        UniqueConstraint("resource_type", "resource_id", "granted_to_user_id", name="uq_resource_permission"),
        CheckConstraint("resource_type IN ('study', 'book')", name="chk_resource_permission_type"),
        Index("ix_resource_permissions_target", "resource_type", "resource_id"),
        Index("ix_resource_permissions_granted", "granted_to_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resource_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'study' | 'book'
    resource_id: Mapped[int] = mapped_column(Integer, nullable=False)
    granted_to_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    can_view: Mapped[bool] = mapped_column(
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

    granted_to_user: Mapped[User] = relationship("User", foreign_keys=[granted_to_user_id])
