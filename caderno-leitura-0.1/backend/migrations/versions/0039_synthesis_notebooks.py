"""Cadernos de síntese com transclusão (F0.11.11, spec 113).

Tabela nova, do próprio leitor e fora de qualquer livro; o texto guarda marcas ``![[…]]`` que a leitura resolve na
hora (nada copiado). ``deleted_at`` = lixeira própria das sínteses (30 dias). Sai junto com a conta.

Revision ID: 0039_synthesis_notebooks
Revises: 0038_receiver_tokens
"""
from alembic import op
import sqlalchemy as sa

revision = "0039_synthesis_notebooks"
down_revision = "0038_receiver_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "synthesis_notebooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_synthesis_notebooks_user_id_users"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("body", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_synthesis_notebooks_chk_synthesis_title_not_blank"),
        sa.PrimaryKeyConstraint("id", name="pk_synthesis_notebooks"),
    )
    op.create_index("ix_synthesis_notebooks_user_deleted", "synthesis_notebooks", ["user_id", "deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_synthesis_notebooks_user_deleted", table_name="synthesis_notebooks")
    op.drop_table("synthesis_notebooks")
