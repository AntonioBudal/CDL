from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.user import User


class Friendship(Base):
    """Modelo relacional que representa vínculos de amizade e bloqueio entre usuários.

    Os usuários são sempre armazenados de forma normalizada onde user_id_a < user_id_b,
    garantindo unicidade estrita por par e prevenindo registros duplicados no SQLite.
    """

    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("user_id_a", "user_id_b", name="uq_friendships_pair"),
        CheckConstraint("user_id_a < user_id_b", name="ck_friendships_ordered_pair"),
        CheckConstraint("user_id_a != user_id_b", name="ck_friendships_no_self"),
        Index("ix_friendships_status_action", "status", "action_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id_a: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id_b: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )  # 'pending', 'accepted', 'blocked'
    action_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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

    user_a: Mapped[User] = relationship(
        "User",
        foreign_keys=[user_id_a],
        lazy="joined",
    )
    user_b: Mapped[User] = relationship(
        "User",
        foreign_keys=[user_id_b],
        lazy="joined",
    )
    action_user: Mapped[User] = relationship(
        "User",
        foreign_keys=[action_user_id],
        lazy="joined",
    )

    @staticmethod
    def normalize_pair(id_1: str, id_2: str) -> tuple[str, str]:
        """Normaliza dois IDs de usuário em ordem estrita (menor, maior)."""
        if id_1 == id_2:
            raise ValueError("Não é permitido estabelecer relação com o mesmo usuário.")
        return (id_1, id_2) if id_1 < id_2 else (id_2, id_1)
