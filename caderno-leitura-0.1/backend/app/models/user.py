from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import CheckConstraint, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.external_identity import ExternalIdentity
    from app.models.local_credential import LocalCredential
    from app.models.study import Study
    from app.models.user_preference import UserPreference
    from app.models.user_profile import UserProfile
    from app.models.user_session import UserSession


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(trim(username)) > 0", name="username_not_blank"),
        CheckConstraint("length(trim(display_name)) > 0", name="display_name_not_blank"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        server_default=text("'user'"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="ativo",
        server_default=text("'ativo'"),
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

    credential: Mapped[LocalCredential | None] = relationship(
        "LocalCredential",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        passive_deletes=True,
    )
    external_identities: Mapped[list[ExternalIdentity]] = relationship(
        "ExternalIdentity",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sessions: Mapped[list[UserSession]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    books: Mapped[list[Book]] = relationship(
        "Book",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    studies: Mapped[list[Study]] = relationship(
        "Study",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    profile: Mapped[UserProfile | None] = relationship(
        "UserProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        passive_deletes=True,
    )

    @property
    def has_password(self) -> bool:
        return self.credential is not None

    @property
    def has_google(self) -> bool:
        if not hasattr(self, "external_identities") or self.external_identities is None:
            return False
        return any(ident.provider == "google" for ident in self.external_identities)

