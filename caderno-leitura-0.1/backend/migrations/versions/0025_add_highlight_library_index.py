"""Adicionar indice de consulta transversal em study_highlights.

Revision ID: 0025_add_highlight_library_index
Revises: 0024_add_review_metadata_to_highlights
"""
from alembic import op

revision = "0025_add_highlight_library_index"
down_revision = "0024_add_review_metadata_to_highlights"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("study_highlights") as batch_op:
        batch_op.create_index(
            "ix_study_highlights_user_kind_color",
            ["user_id", "kind", "color"],
        )


def downgrade() -> None:
    with op.batch_alter_table("study_highlights") as batch_op:
        batch_op.drop_index("ix_study_highlights_user_kind_color")
