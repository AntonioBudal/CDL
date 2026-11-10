"""ISBN, editora e local de publicação do livro (F0.11.04, spec 106).

Três colunas anuláveis em ``books`` e índice ``(user_id, isbn)``. ``ADD COLUMN`` simples (recriar ``books`` esbarraria
no ``RESTRICT`` de ``chapters``); nenhum dado existente muda.

Revision ID: 0036_book_isbn_publisher
Revises: 0035_inbox_capture_chapter
"""
from alembic import op

revision = "0036_book_isbn_publisher"
down_revision = "0035_inbox_capture_chapter"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE books ADD COLUMN isbn VARCHAR(13)")
    op.execute("ALTER TABLE books ADD COLUMN publisher TEXT")
    op.execute("ALTER TABLE books ADD COLUMN publication_place TEXT")
    op.create_index("ix_books_user_isbn", "books", ["user_id", "isbn"])


def downgrade() -> None:
    op.drop_index("ix_books_user_isbn", table_name="books")
    op.execute("ALTER TABLE books DROP COLUMN publication_place")
    op.execute("ALTER TABLE books DROP COLUMN publisher")
    op.execute("ALTER TABLE books DROP COLUMN isbn")
