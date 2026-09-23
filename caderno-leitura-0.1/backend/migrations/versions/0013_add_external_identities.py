"""Adicionar tabela de identidades externas (Google GIS).

Revision ID: 0013_add_external_identities
Revises: 0012_add_credentials_and_sessions
"""
from alembic import op
import sqlalchemy as sa

revision = "0013_add_external_identities"
down_revision = "0012_add_credentials_and_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "external_identities",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "provider",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'google'"),
        ),
        sa.Column("provider_subject", sa.String(length=255), nullable=False),
        sa.Column("email_at_link", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_external_identities_provider_sub"),
    )
    op.create_index("ix_external_identities_user_id", "external_identities", ["user_id"], unique=False)
    op.create_index(
        "ix_external_identities_provider_sub",
        "external_identities",
        ["provider", "provider_subject"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_external_identities_provider_sub", table_name="external_identities")
    op.drop_index("ix_external_identities_user_id", table_name="external_identities")
    op.drop_table("external_identities")
