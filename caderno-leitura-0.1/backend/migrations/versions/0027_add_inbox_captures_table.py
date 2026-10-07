"""Adicionar tabela de inbox_captures para caixa de entrada de capturas.

Revision ID: 0027_add_inbox_captures_table
Revises: 0026_add_study_mentions_table
"""
from alembic import op
import sqlalchemy as sa

revision = "0027_add_inbox_captures_table"
down_revision = "0026_add_study_mentions_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inbox_captures",
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
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_hint", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="inbox", nullable=False),
        sa.Column(
            "promoted_study_id",
            sa.Integer(),
            sa.ForeignKey("studies.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
    op.create_index("ix_inbox_captures_user_status", "inbox_captures", ["user_id", "status"])
    op.create_index("ix_inbox_captures_user_created", "inbox_captures", ["user_id", "created_at"])
    op.create_index("ix_inbox_captures_book_id", "inbox_captures", ["book_id"])
    op.create_index("ix_inbox_captures_promoted_study", "inbox_captures", ["promoted_study_id"])


def downgrade() -> None:
    op.drop_index("ix_inbox_captures_promoted_study", table_name="inbox_captures")
    op.drop_index("ix_inbox_captures_book_id", table_name="inbox_captures")
    op.drop_index("ix_inbox_captures_user_created", table_name="inbox_captures")
    op.drop_index("ix_inbox_captures_user_status", table_name="inbox_captures")
    op.drop_table("inbox_captures")
