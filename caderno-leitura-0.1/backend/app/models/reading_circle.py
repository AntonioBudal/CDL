"""F0.12.07 (spec 120): círculos de leitura com trava anti-spoiler.

O círculo tem **partes próprias** (iguais para todos os membros; os capítulos de cada leitor não se comparam). Cada
membro diz em que parte está (``progress`` = posição da parte; 0 = não comecei) ou que terminou (``finished``). As
mensagens de uma parte só chegam a quem está nela ou adiante — a trava é aplicada no servidor.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now


class ReadingCircle(Base):
    __tablename__ = "reading_circles"
    __table_args__ = (Index("ix_reading_circles_owner_id", "owner_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    book_title: Mapped[str] = mapped_column(Text, nullable=False)
    book_author: Mapped[str | None] = mapped_column(Text, nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(13), nullable=True)
    source_book_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), onupdate=utc_now, nullable=False
    )


class ReadingCirclePart(Base):
    __tablename__ = "reading_circle_parts"
    __table_args__ = (
        UniqueConstraint("circle_id", "position"),
        CheckConstraint("position >= 1", name="chk_circle_part_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    circle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reading_circles.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)


class ReadingCircleMember(Base):
    __tablename__ = "reading_circle_members"
    __table_args__ = (
        UniqueConstraint("circle_id", "user_id"),
        CheckConstraint("role IN ('owner', 'member')", name="chk_circle_member_role"),
        CheckConstraint("status IN ('invited', 'active')", name="chk_circle_member_status"),
        CheckConstraint("progress >= 0", name="chk_circle_member_progress"),
        Index("ix_reading_circle_members_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    circle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reading_circles.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(10), default="member", server_default=text("'member'"), nullable=False)
    status: Mapped[str] = mapped_column(String(10), default="invited", server_default=text("'invited'"), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    finished: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"), nullable=False)
    invited_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    joined_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)


class ReadingCirclePost(Base):
    __tablename__ = "reading_circle_posts"
    __table_args__ = (
        CheckConstraint("length(trim(body)) > 0", name="chk_circle_post_body"),
        Index("ix_reading_circle_posts_part_id", "part_id"),
        Index("ix_reading_circle_posts_circle_id", "circle_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    circle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reading_circles.id", ondelete="CASCADE"), nullable=False
    )
    part_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reading_circle_parts.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    edited_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
