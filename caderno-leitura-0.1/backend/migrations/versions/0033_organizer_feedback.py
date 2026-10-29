"""Criar as tabelas do registro de feedback do organizador e do estado do adaptador (feature 091-B).

``organizer_feedback`` guarda um registro ``leitorum-feedback/1`` por estudo salvo pela digitalização ou depois de
organizar. ``organizer_user_state`` só é criada aqui: o adaptador da fatia C a preenche. As duas saem junto com o
estudo e com a conta (``ON DELETE CASCADE``).

Revision ID: 0033_organizer_feedback
Revises: 0032_media_completed_seen
"""
from alembic import op
import sqlalchemy as sa

revision = "0033_organizer_feedback"
down_revision = "0032_media_completed_seen"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizer_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_id", sa.Integer(), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("schema", sa.String(length=32), nullable=False),
        sa.Column("origin", sa.String(length=12), nullable=False),
        sa.Column("reviewed", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("artifact_sha256", sa.String(length=64), server_default=sa.text("''"), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("origin IN ('digitize', 'import')", name="ck_organizer_feedback_origin"),
        sa.UniqueConstraint("study_id", name="uq_organizer_feedback_study"),
    )
    op.create_index("ix_organizer_feedback_user_reviewed", "organizer_feedback", ["user_id", "reviewed"])
    op.create_table(
        "organizer_user_state",
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("artifact_sha256", sa.String(length=64), nullable=False),
        sa.Column("reviewed_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("organizer_user_state")
    op.drop_index("ix_organizer_feedback_user_reviewed", table_name="organizer_feedback")
    op.drop_table("organizer_feedback")
