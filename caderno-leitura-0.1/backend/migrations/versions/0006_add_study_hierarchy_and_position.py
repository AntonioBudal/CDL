"""Adicionar hierarquia e ordenacao em estudos.

Revision ID: 0006_add_study_hierarchy_and_position
Revises: 0005_add_categories_and_taxonomy
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_add_study_hierarchy_and_position"
down_revision = "0005_add_categories_and_taxonomy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("studies") as batch_op:
        batch_op.add_column(
            sa.Column(
                "parent_study_id",
                sa.Integer(),
                sa.ForeignKey("studies.id", ondelete="SET NULL"),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "position",
                sa.Integer(),
                server_default=sa.text("0"),
                nullable=False,
            )
        )
        batch_op.create_index("ix_studies_parent_study_id", ["parent_study_id"])
        batch_op.create_index(
            "ix_studies_chapter_parent_position",
            ["chapter_id", "parent_study_id", "position"],
        )


def downgrade() -> None:
    with op.batch_alter_table("studies") as batch_op:
        batch_op.drop_index("ix_studies_chapter_parent_position")
        batch_op.drop_index("ix_studies_parent_study_id")
        batch_op.drop_column("position")
        batch_op.drop_column("parent_study_id")
