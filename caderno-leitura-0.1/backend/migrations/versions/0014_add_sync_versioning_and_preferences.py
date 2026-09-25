"""Adicionar versionamento OCC e tabela user_preferences para sincronizacao multidispositivo.

Revision ID: 0014_add_sync_versioning_and_preferences
Revises: 0013_add_external_identities
"""
from alembic import op
import sqlalchemy as sa

revision = "0014_add_sync_versioning_and_preferences"
down_revision = "0013_add_external_identities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Tabela user_preferences
    op.create_table(
        "user_preferences",
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "active_superclass",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'mecanica'"),
        ),
        sa.Column(
            "superclass_intensity",
            sa.Float(),
            nullable=False,
            server_default=sa.text("1.0"),
        ),
        sa.Column(
            "preferred_view_mode",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'grid'"),
        ),
        sa.Column(
            "tree_collapsed_state",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column(
            "font_family",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'garamond'"),
        ),
        sa.Column(
            "font_scale",
            sa.Float(),
            nullable=False,
            server_default=sa.text("1.0"),
        ),
        sa.Column(
            "theme_mode",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'dark'"),
        ),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # 2. studies: coluna version e indice de sync
    op.add_column(
        "studies",
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.create_index(
        "ix_studies_sync",
        "studies",
        ["user_id", "updated_at"],
        unique=False,
    )

    # 3. books: coluna version e indice de sync
    op.add_column(
        "books",
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.create_index(
        "ix_books_sync",
        "books",
        ["user_id", "updated_at"],
        unique=False,
    )

    # 4. study_canvas_nodes: coluna version e indice de sync
    op.add_column(
        "study_canvas_nodes",
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.create_index(
        "ix_canvas_nodes_sync",
        "study_canvas_nodes",
        ["user_id", "updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_canvas_nodes_sync", table_name="study_canvas_nodes")
    with op.batch_alter_table("study_canvas_nodes") as batch_op:
        batch_op.drop_column("version")

    op.drop_index("ix_books_sync", table_name="books")
    with op.batch_alter_table("books") as batch_op:
        batch_op.drop_column("version")

    op.drop_index("ix_studies_sync", table_name="studies")
    with op.batch_alter_table("studies") as batch_op:
        batch_op.drop_column("version")

    op.drop_table("user_preferences")
