"""Capítulo da captura da Mesa de Triagem (bandeja por capítulo, F0.11.02, spec 104).

``inbox_captures.chapter_id`` anulável, com ``ON DELETE SET NULL``: excluído o capítulo, a captura fica só com o
livro. ``ADD COLUMN`` simples (o SQLite aceita ``REFERENCES`` em coluna nova com padrão nulo); nenhum dado muda.

Revision ID: 0035_inbox_capture_chapter
Revises: 0034_book_reading_state
"""
from alembic import op

revision = "0035_inbox_capture_chapter"
down_revision = "0034_book_reading_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE inbox_captures ADD COLUMN chapter_id INTEGER "
        "REFERENCES chapters(id) ON DELETE SET NULL"
    )
    op.create_index(
        "ix_inbox_captures_user_chapter_status", "inbox_captures", ["user_id", "chapter_id", "status"]
    )


def downgrade() -> None:
    op.drop_index("ix_inbox_captures_user_chapter_status", table_name="inbox_captures")
    # SQLite >= 3.35: DROP COLUMN direto (a coluna não é chave nem está em índice depois do drop acima).
    op.execute("ALTER TABLE inbox_captures DROP COLUMN chapter_id")
