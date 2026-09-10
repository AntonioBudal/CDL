"""Criar livros, capitulos e estudos.

Revision ID: 0001_initial
Revises: None
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("author", sa.Text(), nullable=True),
        sa.CheckConstraint("length(trim(title)) > 0", name=op.f("ck_books_title_not_blank")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_books")),
    )
    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name=op.f("ck_chapters_name_not_blank")),
        sa.CheckConstraint("position >= 0", name=op.f("ck_chapters_position_non_negative")),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], name=op.f("fk_chapters_book_id_books"), ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chapters")),
    )
    op.create_index("ix_chapters_book_id_position", "chapters", ["book_id", "position"])
    op.create_table(
        "studies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chapter_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("source_response", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("summary", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("explanation", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("concepts", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("references", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("notes", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("length(trim(title)) > 0", name=op.f("ck_studies_title_not_blank")),
        sa.CheckConstraint(
            'length(trim(summary || explanation || concepts || "references")) > 0',
            name=op.f("ck_studies_analysis_not_blank"),
        ),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], name=op.f("fk_studies_chapter_id_chapters"), ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_studies")),
    )
    op.create_index("ix_studies_chapter_id", "studies", ["chapter_id"])
    op.execute("PRAGMA optimize")


def downgrade() -> None:
    op.drop_index("ix_studies_chapter_id", table_name="studies")
    op.drop_table("studies")
    op.drop_index("ix_chapters_book_id_position", table_name="chapters")
    op.drop_table("chapters")
    op.drop_table("books")
