"""Adicionar deleted_at em books e studies para lixeira e soft delete.

Revision ID: 0003_add_trash_soft_delete
Revises: 0002_add_metadata_concurrency
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_add_trash_soft_delete"
down_revision = "0002_add_metadata_concurrency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("books") as batch_op:
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch_op.create_index("ix_books_deleted_at", ["deleted_at"])

    with op.batch_alter_table("studies") as batch_op:
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch_op.create_index("ix_studies_deleted_at", ["deleted_at"])

    op.execute("PRAGMA optimize")


def downgrade() -> None:
    with op.batch_alter_table("studies") as batch_op:
        batch_op.drop_index("ix_studies_deleted_at")
        batch_op.drop_column("deleted_at")

    with op.batch_alter_table("books") as batch_op:
        batch_op.drop_index("ix_books_deleted_at")
        batch_op.drop_column("deleted_at")
