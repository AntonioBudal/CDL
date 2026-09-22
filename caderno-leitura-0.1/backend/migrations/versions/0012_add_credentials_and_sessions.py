"""Adicionar credenciais locais e sessoes de usuario.

Revision ID: 0012_add_credentials_and_sessions
Revises: 0011_add_user_and_multiuser_foundation
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_add_credentials_and_sessions"
down_revision = "0011_add_user_and_multiuser_foundation"
branch_labels = None
depends_on = None

CANONICAL_OWNER_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # 1. Adiciona colunas email e role na tabela users
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column(
                "role",
                sa.String(length=20),
                server_default=sa.text("'user'"),
                nullable=False,
            )
        )
        batch_op.create_index("ix_users_email", ["email"], unique=True)

    # 2. Promove o proprietário canônico para a role 'admin'
    op.execute(
        sa.text(f"UPDATE users SET role = 'admin' WHERE id = '{CANONICAL_OWNER_ID}'")
    )

    # 3. Cria a tabela local_credentials
    op.create_table(
        "local_credentials",
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "password_updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # 4. Cria a tabela user_sessions
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("session_token_hash", sa.String(length=64), nullable=False),
        sa.Column("device_name", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "last_activity",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"], unique=False)
    op.create_index(
        "ix_user_sessions_session_token_hash",
        "user_sessions",
        ["session_token_hash"],
        unique=True,
    )
    op.create_index("ix_user_sessions_expires_at", "user_sessions", ["expires_at"], unique=False)


def downgrade() -> None:
    # 1. Remove tabelas dependentes
    op.drop_index("ix_user_sessions_expires_at", table_name="user_sessions")
    op.drop_index("ix_user_sessions_session_token_hash", table_name="user_sessions")
    op.drop_index("ix_user_sessions_user_id", table_name="user_sessions")
    op.drop_table("user_sessions")
    op.drop_table("local_credentials")

    # 2. Reverte colunas na tabela users
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index("ix_users_email")
        batch_op.drop_column("role")
        batch_op.drop_column("email")
