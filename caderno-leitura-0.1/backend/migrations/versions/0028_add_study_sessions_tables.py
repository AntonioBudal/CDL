"""Adicionar tabelas study_sessions e study_session_items para sessões de estudo.

Revision ID: 0028_add_study_sessions_tables
Revises: 0027_add_inbox_captures_table
"""
from alembic import op
import sqlalchemy as sa

revision = "0028_add_study_sessions_tables"
down_revision = "0027_add_inbox_captures_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "study_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            server_default=sa.text("'00000000-0000-0000-0000-000000000001'"),
            nullable=False,
        ),
        sa.Column(
            "book_id",
            sa.Integer(),
            sa.ForeignKey("books.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("scope_type", sa.String(length=30), server_default="quick", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="in_progress", nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("total_items", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("completed_items", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("easy_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("medium_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("hard_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index("ix_study_sessions_user_id", "study_sessions", ["user_id"])
    op.create_index("ix_study_sessions_book_id", "study_sessions", ["book_id"])
    op.create_index("ix_study_sessions_status", "study_sessions", ["status"])
    op.create_index("ix_study_sessions_started_at", "study_sessions", ["started_at"])

    op.create_table(
        "study_session_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column(
            "session_id",
            sa.Integer(),
            sa.ForeignKey("study_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "highlight_id",
            sa.Integer(),
            sa.ForeignKey("study_highlights.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rating", sa.String(length=20), nullable=False),
        sa.Column("time_spent_seconds", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "answered_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index("ix_study_session_items_session_id", "study_session_items", ["session_id"])
    op.create_index("ix_study_session_items_highlight_id", "study_session_items", ["highlight_id"])


def downgrade() -> None:
    op.drop_index("ix_study_session_items_highlight_id", table_name="study_session_items")
    op.drop_index("ix_study_session_items_session_id", table_name="study_session_items")
    op.drop_table("study_session_items")

    op.drop_index("ix_study_sessions_started_at", table_name="study_sessions")
    op.drop_index("ix_study_sessions_status", table_name="study_sessions")
    op.drop_index("ix_study_sessions_book_id", table_name="study_sessions")
    op.drop_index("ix_study_sessions_user_id", table_name="study_sessions")
    op.drop_table("study_sessions")
