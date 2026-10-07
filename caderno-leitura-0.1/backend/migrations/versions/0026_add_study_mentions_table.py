"""Adicionar tabela de study_mentions para backlinks e mencoes entre estudos.

Revision ID: 0026_add_study_mentions_table
Revises: 0025_add_highlight_library_index
"""
from alembic import op
import sqlalchemy as sa

revision = "0026_add_study_mentions_table"
down_revision = "0025_add_highlight_library_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "study_mentions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            server_default=sa.text("'00000000-0000-0000-0000-000000000001'"),
            nullable=False,
        ),
        sa.Column(
            "source_study_id",
            sa.Integer(),
            sa.ForeignKey("studies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_study_id",
            sa.Integer(),
            sa.ForeignKey("studies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("section", sa.String(length=30), nullable=False),
        sa.Column("mention_text", sa.Text(), nullable=False),
        sa.Column("context_snippet", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index("ix_study_mentions_target_user", "study_mentions", ["target_study_id", "user_id"])
    op.create_index("ix_study_mentions_source_user", "study_mentions", ["source_study_id", "user_id"])


def downgrade() -> None:
    op.drop_index("ix_study_mentions_source_user", table_name="study_mentions")
    op.drop_index("ix_study_mentions_target_user", table_name="study_mentions")
    op.drop_table("study_mentions")
