"""Capítulo da captura da Mesa de Triagem (bandeja por capítulo, F0.11.02, spec 104).

``inbox_captures.chapter_id`` anulável, com ``ON DELETE SET NULL``: excluído o capítulo, a captura fica só com o
livro. Nenhum dado muda.

Modo batch (recria ``inbox_captures`` copiando as linhas): o SQLite só guarda o **nome** de uma chave estrangeira
declarada na tabela, e o nome precisa seguir a convenção do metadata (``fk_<tabela>_<coluna>_<alvo>``) para o
``alembic check`` bater com o modelo. É seguro porque nenhuma tabela aponta para ``inbox_captures``. (Na primeira
versão desta migração a chave ia na própria coluna, sem nome; corrigido no fecho do lote 1 do 0.11, antes de a
migração ser aplicada no banco ativo.)

Revision ID: 0035_inbox_capture_chapter
Revises: 0034_book_reading_state
"""
from alembic import op
import sqlalchemy as sa

revision = "0035_inbox_capture_chapter"
down_revision = "0034_book_reading_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("inbox_captures", recreate="always") as batch:
        batch.add_column(sa.Column("chapter_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_inbox_captures_chapter_id_chapters", "chapters", ["chapter_id"], ["id"], ondelete="SET NULL"
        )
    op.create_index(
        "ix_inbox_captures_user_chapter_status", "inbox_captures", ["user_id", "chapter_id", "status"]
    )


def downgrade() -> None:
    op.drop_index("ix_inbox_captures_user_chapter_status", table_name="inbox_captures")
    with op.batch_alter_table("inbox_captures", recreate="always") as batch:
        batch.drop_constraint("fk_inbox_captures_chapter_id_chapters", type_="foreignkey")
        batch.drop_column("chapter_id")
