"""Estudo publicado na web (F0.12.02, spec 115).

``studies.published_at`` (anulável; vazio = não publicado). ``ADD COLUMN`` simples (sem chave estrangeira) e índice.
Publicar é uma escolha explícita do dono, separada da visibilidade: nada que já existe passa a ser público na web.

Revision ID: 0040_study_published_at
Revises: 0039_synthesis_notebooks
"""
from alembic import op

revision = "0040_study_published_at"
down_revision = "0039_synthesis_notebooks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE studies ADD COLUMN published_at DATETIME")
    op.create_index("ix_studies_published_at", "studies", ["published_at"])


def downgrade() -> None:
    op.drop_index("ix_studies_published_at", table_name="studies")
    op.execute("ALTER TABLE studies DROP COLUMN published_at")
