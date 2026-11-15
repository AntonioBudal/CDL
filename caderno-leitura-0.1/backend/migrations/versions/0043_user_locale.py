"""Idioma da interface nas preferências (F0.12.09, spec 122).

``user_preferences.locale`` (``'pt-BR'`` ou ``'en'``, padrão ``'pt-BR'``). ``ADD COLUMN`` simples com padrão: as
preferências que já existem ficam em português, como estão hoje.

Revision ID: 0043_user_locale
Revises: 0042_reading_circles
"""
from alembic import op

revision = "0043_user_locale"
down_revision = "0042_reading_circles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE user_preferences ADD COLUMN locale VARCHAR(10) NOT NULL DEFAULT 'pt-BR'")


def downgrade() -> None:
    op.execute("ALTER TABLE user_preferences DROP COLUMN locale")
