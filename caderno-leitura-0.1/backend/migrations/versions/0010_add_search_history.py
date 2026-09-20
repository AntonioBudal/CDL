"""Criar tabela search_history para buscas recentes.

Revision ID: 0010_add_search_history
Revises: 0009_add_reading_status_and_canvas_frames
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_add_search_history"
down_revision = "0009_add_reading_status_and_canvas_frames"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("query", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_search_history_query", "search_history", ["query"], unique=True)
    op.create_index("ix_search_history_updated_at", "search_history", ["updated_at"])


def downgrade() -> None:
    op.drop_index("ix_search_history_updated_at", table_name="search_history")
    op.drop_index("ix_search_history_query", table_name="search_history")
    op.drop_table("search_history")
