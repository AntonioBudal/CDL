"""Adicionar coluna template_id na tabela studies.

Revision ID: 0029_add_template_id_to_studies
Revises: 0028_add_study_sessions_tables
"""
from alembic import op
import sqlalchemy as sa

revision = "0029_add_template_id_to_studies"
down_revision = "0028_add_study_sessions_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("studies") as batch_op:
        batch_op.add_column(
            sa.Column(
                "template_id",
                sa.String(length=30),
                server_default=sa.text("'classico'"),
                nullable=True,
            )
        )
        batch_op.create_index("ix_studies_template_id", ["template_id"])


def downgrade() -> None:
    with op.batch_alter_table("studies") as batch_op:
        batch_op.drop_index("ix_studies_template_id")
        batch_op.drop_column("template_id")
