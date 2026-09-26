"""Adicionar tabela friendships para gestão de amizades e bloqueios sociais.

Revision ID: 0016_add_friendships_table
Revises: 0015_add_user_profile
"""
from alembic import op
import sqlalchemy as sa

revision = "0016_add_friendships_table"
down_revision = "0015_add_user_profile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "friendships",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column(
            "user_id_a",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id_b",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column(
            "action_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("user_id_a", "user_id_b", name="uq_friendships_pair"),
        sa.CheckConstraint("user_id_a < user_id_b", name="ck_friendships_ordered_pair"),
        sa.CheckConstraint("user_id_a != user_id_b", name="ck_friendships_no_self"),
    )
    op.create_index("ix_friendships_user_id_a", "friendships", ["user_id_a"])
    op.create_index("ix_friendships_user_id_b", "friendships", ["user_id_b"])
    op.create_index("ix_friendships_action_user_id", "friendships", ["action_user_id"])
    op.create_index(
        "ix_friendships_status_action",
        "friendships",
        ["status", "action_user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_friendships_status_action", table_name="friendships")
    op.drop_index("ix_friendships_action_user_id", table_name="friendships")
    op.drop_index("ix_friendships_user_id_b", table_name="friendships")
    op.drop_index("ix_friendships_user_id_a", table_name="friendships")
    op.drop_table("friendships")
