"""Marcar quando o job viu o estudo da foto concluído (retenção, feature 090-C).

Revision ID: 0032_media_completed_seen
Revises: 0031_encrypted_media
"""
from alembic import op
import sqlalchemy as sa

revision = "0032_media_completed_seen"
down_revision = "0031_encrypted_media"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Coluna anulável: ADD COLUMN simples, sem recriar a tabela.
    op.add_column("encrypted_media", sa.Column("completed_seen_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("encrypted_media") as batch:
        batch.drop_column("completed_seen_at")
