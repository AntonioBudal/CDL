"""Criar a tabela storage_settings (identidade da pasta de armazenamento, feature 090-A).

Revision ID: 0030_storage_settings
Revises: 0029_add_template_id_to_studies
"""
from alembic import op
import sqlalchemy as sa

revision = "0030_storage_settings"
down_revision = "0029_add_template_id_to_studies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "storage_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("storage_id", sa.String(length=36), nullable=False),
        sa.Column("media_key_fingerprint", sa.String(length=16), nullable=True),
        sa.Column("media_key_epoch", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_storage_settings_singleton"),
    )


def downgrade() -> None:
    op.drop_table("storage_settings")
