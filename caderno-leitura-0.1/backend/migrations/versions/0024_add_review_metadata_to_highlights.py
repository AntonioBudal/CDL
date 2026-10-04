"""Adicionar metadados de revisao e indice em study_highlights.

Revision ID: 0024_add_review_metadata_to_highlights
Revises: 0023_normalize_categories
"""
from alembic import op
import sqlalchemy as sa

revision = "0024_add_review_metadata_to_highlights"
down_revision = "0023_normalize_categories"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("study_highlights") as batch_op:
        batch_op.add_column(sa.Column("last_reviewed_at", sa.DateTime(), nullable=True))
        batch_op.add_column(
            sa.Column("review_count", sa.Integer(), server_default=sa.text("0"), nullable=False)
        )
        batch_op.add_column(sa.Column("last_rating", sa.String(length=20), nullable=True))
        batch_op.create_check_constraint(
            "chk_highlight_last_rating",
            "last_rating IS NULL OR last_rating IN ('easy', 'medium', 'hard')",
        )
        batch_op.create_index(
            "ix_study_highlights_review",
            ["user_id", "kind", "last_reviewed_at"],
        )


def downgrade() -> None:
    with op.batch_alter_table("study_highlights") as batch_op:
        batch_op.drop_index("ix_study_highlights_review")
        batch_op.drop_constraint("chk_highlight_last_rating", type_="check")
        batch_op.drop_column("last_rating")
        batch_op.drop_column("review_count")
        batch_op.drop_column("last_reviewed_at")
