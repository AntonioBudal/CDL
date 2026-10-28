"""Criar a tabela encrypted_media (cofre de imagens cifradas, feature 090-B).

Revision ID: 0031_encrypted_media
Revises: 0030_storage_settings
"""
from alembic import op
import sqlalchemy as sa

revision = "0031_encrypted_media"
down_revision = "0030_storage_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "encrypted_media",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("study_id", sa.Integer(), sa.ForeignKey("studies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="SET NULL"), nullable=True),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("plain_size", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=32), nullable=False),
        sa.Column("format_version", sa.Integer(), nullable=False),
        sa.Column("key_epoch", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("keep_forever", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("pending_until", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("kind IN ('notebook_page', 'avatar', 'cover')", name="ck_encrypted_media_kind"),
        sa.CheckConstraint("status IN ('pending', 'active', 'deleting', 'missing')", name="ck_encrypted_media_status"),
        sa.CheckConstraint("kind = 'notebook_page' OR keep_forever = 0", name="ck_encrypted_media_keep_pages_only"),
    )
    op.create_index("ix_encrypted_media_user_status", "encrypted_media", ["user_id", "status"])
    op.create_index("ix_encrypted_media_status_expires", "encrypted_media", ["status", "expires_at"])
    op.create_index("ix_encrypted_media_study", "encrypted_media", ["study_id"])
    op.create_index("ix_encrypted_media_kind_user", "encrypted_media", ["kind", "user_id"])


def downgrade() -> None:
    op.drop_index("ix_encrypted_media_kind_user", table_name="encrypted_media")
    op.drop_index("ix_encrypted_media_study", table_name="encrypted_media")
    op.drop_index("ix_encrypted_media_status_expires", table_name="encrypted_media")
    op.drop_index("ix_encrypted_media_user_status", table_name="encrypted_media")
    op.drop_table("encrypted_media")
