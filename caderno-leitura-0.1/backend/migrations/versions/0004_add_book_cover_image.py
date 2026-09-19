"""Adicionar cover_image em books.

Revision ID: 0004_add_book_cover_image
Revises: 0003_add_trash_soft_delete
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_add_book_cover_image"
down_revision = "0003_add_trash_soft_delete"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("books") as batch_op:
        batch_op.add_column(sa.Column("cover_image", sa.Text(), nullable=True))

    op.execute("PRAGMA optimize")


def downgrade() -> None:
    with op.batch_alter_table("books") as batch_op:
        batch_op.drop_column("cover_image")
