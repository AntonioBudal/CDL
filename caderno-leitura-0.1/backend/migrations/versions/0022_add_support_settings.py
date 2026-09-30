"""Adicionar tabela de support_settings para parametros globais de apoio financeiro.

Revision ID: 0022_add_support_settings
Revises: 0021_add_study_versions
"""
from alembic import op
import sqlalchemy as sa

revision = "0022_add_support_settings"
down_revision = "0021_add_study_versions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "support_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("pix_enabled", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("pix_key", sa.String(length=255), nullable=True),
        sa.Column("pix_recipient_name", sa.String(length=255), nullable=True),
        sa.Column("pix_qr_code_url", sa.Text(), nullable=True),
        sa.Column("alternative_enabled", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("alternative_label", sa.String(length=100), nullable=True),
        sa.Column("alternative_url", sa.Text(), nullable=True),
        sa.Column("custom_message", sa.Text(), nullable=True),
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
        sa.Column(
            "updated_by_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.CheckConstraint("id = 1", name="ck_support_settings_singleton"),
    )


def downgrade() -> None:
    op.drop_table("support_settings")
