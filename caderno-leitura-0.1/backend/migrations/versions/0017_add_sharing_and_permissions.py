"""Adicionar colunas de visibilidade e tabela resource_permissions para controle de acesso (ACL).

Revision ID: 0017_add_sharing_and_permissions
Revises: 0016_add_friendships_table
"""
from alembic import op
import sqlalchemy as sa

revision = "0017_add_sharing_and_permissions"
down_revision = "0016_add_friendships_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Adiciona campo visibility em books com padrão 'private'
    with op.batch_alter_table("books") as batch_op:
        batch_op.add_column(
            sa.Column(
                "visibility",
                sa.String(length=20),
                server_default=sa.text("'private'"),
                nullable=False,
            )
        )
        batch_op.create_index("ix_books_visibility", ["visibility"])

    # 2. Adiciona campo visibility em studies com padrão 'inherit'
    with op.batch_alter_table("studies") as batch_op:
        batch_op.add_column(
            sa.Column(
                "visibility",
                sa.String(length=20),
                server_default=sa.text("'inherit'"),
                nullable=False,
            )
        )
        batch_op.create_index("ix_studies_visibility", ["visibility"])

    # 3. Cria tabela de ACL nominal resource_permissions
    op.create_table(
        "resource_permissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("resource_type", sa.String(length=20), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column(
            "granted_to_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("can_view", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint("resource_type", "resource_id", "granted_to_user_id", name="uq_resource_permission"),
        sa.CheckConstraint("resource_type IN ('study', 'book')", name="chk_resource_permission_type"),
    )
    op.create_index("ix_resource_permissions_target", "resource_permissions", ["resource_type", "resource_id"])
    op.create_index("ix_resource_permissions_granted", "resource_permissions", ["granted_to_user_id"])


def downgrade() -> None:
    op.drop_index("ix_resource_permissions_granted", table_name="resource_permissions")
    op.drop_index("ix_resource_permissions_target", table_name="resource_permissions")
    op.drop_table("resource_permissions")

    with op.batch_alter_table("studies") as batch_op:
        batch_op.drop_index("ix_studies_visibility")
        batch_op.drop_column("visibility")

    with op.batch_alter_table("books") as batch_op:
        batch_op.drop_index("ix_books_visibility")
        batch_op.drop_column("visibility")
