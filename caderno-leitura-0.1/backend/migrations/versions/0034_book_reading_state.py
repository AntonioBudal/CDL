"""Estado de leitura do livro e datas de início e fim (F0.11.01, spec 103).

Três colunas anuláveis em ``books``; nenhum dado existente muda (livros antigos ficam sem estado). Usa
``ALTER TABLE ... ADD COLUMN`` simples: recriar ``books`` no SQLite (modo batch) esbarraria nas chaves estrangeiras
de ``chapters`` (``ON DELETE RESTRICT``). O ``CHECK`` do estado vai na própria coluna.

Revision ID: 0034_book_reading_state
Revises: 0033_organizer_feedback
"""
from alembic import op

revision = "0034_book_reading_state"
down_revision = "0033_organizer_feedback"
branch_labels = None
depends_on = None

READING_STATES = ("quero_ler", "lendo", "lido", "abandonado")


def upgrade() -> None:
    allowed = ", ".join(f"'{state}'" for state in READING_STATES)
    op.execute(
        "ALTER TABLE books ADD COLUMN reading_state VARCHAR(20) "
        f"CONSTRAINT chk_book_reading_state CHECK (reading_state IS NULL OR reading_state IN ({allowed}))"
    )
    op.execute("ALTER TABLE books ADD COLUMN reading_started_on DATE")
    op.execute("ALTER TABLE books ADD COLUMN reading_finished_on DATE")
    op.create_index("ix_books_user_reading_state", "books", ["user_id", "reading_state"])


def downgrade() -> None:
    op.drop_index("ix_books_user_reading_state", table_name="books")
    # SQLite >= 3.35 remove colunas sem recriar a tabela (o CHECK pertence à própria coluna).
    op.execute("ALTER TABLE books DROP COLUMN reading_finished_on")
    op.execute("ALTER TABLE books DROP COLUMN reading_started_on")
    op.execute("ALTER TABLE books DROP COLUMN reading_state")
