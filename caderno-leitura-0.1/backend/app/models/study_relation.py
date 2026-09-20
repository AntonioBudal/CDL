from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utc_now

if TYPE_CHECKING:
    from app.models.study import Study


class StudyRelation(Base):
    __tablename__ = "study_relations"
    __table_args__ = (
        CheckConstraint("source_study_id != target_study_id", name="ck_study_relations_no_self"),
        CheckConstraint(
            "relation_type IN ('relacionado_com', 'complementa', 'contradiz', 'depende_de', 'mesmo_tema', 'desdobramento_de')",
            name="ck_study_relations_type",
        ),
        UniqueConstraint("source_study_id", "target_study_id", "relation_type", name="uq_study_relations_src_tgt_type"),
        Index("ix_study_relations_source", "source_study_id"),
        Index("ix_study_relations_target", "target_study_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("studies.id", ondelete="CASCADE"),
        nullable=False,
    )
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    source_study: Mapped[Study] = relationship(
        "Study",
        foreign_keys=[source_study_id],
        backref=backref("outbound_relations", cascade="all, delete-orphan", passive_deletes=True),
        passive_deletes=True,
    )
    target_study: Mapped[Study] = relationship(
        "Study",
        foreign_keys=[target_study_id],
        backref=backref("inbound_relations", cascade="all, delete-orphan", passive_deletes=True),
        passive_deletes=True,
    )
