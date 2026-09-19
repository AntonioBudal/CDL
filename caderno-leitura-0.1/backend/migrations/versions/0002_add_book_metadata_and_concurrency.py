"""Adicionar metadados de livros e controle de concorrência.

Revision ID: 0002_add_metadata_concurrency
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_add_metadata_concurrency"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("books") as batch_op:
        batch_op.add_column(sa.Column("subtitle", sa.Text(), server_default=sa.text("''"), nullable=False))
        batch_op.add_column(sa.Column("year", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
        batch_op.create_check_constraint("ck_books_year_range", "year IS NULL OR (year >= 1000 AND year <= 2100)")

    with op.batch_alter_table("chapters") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))

    op.execute("PRAGMA optimize")


def downgrade() -> None:
    with op.batch_alter_table("chapters") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")

    with op.batch_alter_table("books") as batch_op:
        batch_op.drop_constraint("ck_books_year_range", type_="check")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("year")
        batch_op.drop_column("subtitle")
