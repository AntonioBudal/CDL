"""Criar tabela users e adicionar fundacao multiusuario.

Revision ID: 0011_add_user_and_multiuser_foundation
Revises: 0010_add_search_history
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_add_user_and_multiuser_foundation"
down_revision = "0010_add_search_history"
branch_labels = None
depends_on = None

CANONICAL_OWNER_ID = "00000000-0000-0000-0000-000000000001"
CANONICAL_OWNER_USERNAME = "proprietario"
CANONICAL_OWNER_DISPLAY_NAME = "Proprietário do Caderno"


def upgrade() -> None:
    # 1. Cria a tabela users
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default=sa.text("'ativo'"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("length(trim(username)) > 0", name="username_not_blank"),
        sa.CheckConstraint("length(trim(display_name)) > 0", name="display_name_not_blank"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # 2. Provisiona o proprietário canônico para absorver o acervo pré-existente
    users_table = sa.table(
        "users",
        sa.column("id", sa.String),
        sa.column("username", sa.String),
        sa.column("display_name", sa.Text),
        sa.column("status", sa.String),
    )
    op.bulk_insert(
        users_table,
        [
            {
                "id": CANONICAL_OWNER_ID,
                "username": CANONICAL_OWNER_USERNAME,
                "display_name": CANONICAL_OWNER_DISPLAY_NAME,
                "status": "ativo",
            }
        ],
    )

    # 3. Adiciona user_id às tabelas de conteúdo com server_default apontando para o proprietário
    with op.batch_alter_table("books", recreate="auto") as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.String(length=36),
                nullable=False,
                server_default=CANONICAL_OWNER_ID,
            )
        )
        batch_op.create_foreign_key("fk_books_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
        batch_op.create_index("ix_books_user_id", ["user_id"])
        batch_op.create_index("ix_books_user_deleted", ["user_id", "deleted_at"])

    with op.batch_alter_table("studies", recreate="auto") as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.String(length=36),
                nullable=False,
                server_default=CANONICAL_OWNER_ID,
            )
        )
        batch_op.create_foreign_key("fk_studies_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
        batch_op.create_index("ix_studies_user_id", ["user_id"])
        batch_op.create_index("ix_studies_user_deleted", ["user_id", "deleted_at"])

    # Categorias taxonômicas em modelo híbrido (categorias do sistema têm user_id IS NULL)
    with op.batch_alter_table("categories", recreate="auto") as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.String(length=36),
                nullable=True,
                server_default=None,
            )
        )
        batch_op.create_foreign_key("fk_categories_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
        batch_op.create_index("ix_categories_user_id", ["user_id"])

    with op.batch_alter_table("study_relations", recreate="auto") as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.String(length=36),
                nullable=False,
                server_default=CANONICAL_OWNER_ID,
            )
        )
        batch_op.create_foreign_key("fk_study_relations_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
        batch_op.create_index("ix_study_relations_user_id", ["user_id"])

    with op.batch_alter_table("study_canvas_nodes", recreate="auto") as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.String(length=36),
                nullable=False,
                server_default=CANONICAL_OWNER_ID,
            )
        )
        batch_op.create_foreign_key("fk_study_canvas_nodes_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
        batch_op.create_index("ix_canvas_nodes_user_id", ["user_id"])

    with op.batch_alter_table("canvas_frames", recreate="auto") as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.String(length=36),
                nullable=False,
                server_default=CANONICAL_OWNER_ID,
            )
        )
        batch_op.create_foreign_key("fk_canvas_frames_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
        batch_op.create_index("ix_canvas_frames_user_id", ["user_id"])

    with op.batch_alter_table("search_history", recreate="auto") as batch_op:
        batch_op.drop_index("ix_search_history_query")
        batch_op.drop_index("ix_search_history_updated_at")
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.String(length=36),
                nullable=False,
                server_default=CANONICAL_OWNER_ID,
            )
        )
        batch_op.create_foreign_key("fk_search_history_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
        batch_op.create_index("ix_search_history_user_query", ["user_id", "query"], unique=True)
        batch_op.create_index("ix_search_history_user_updated", ["user_id", "updated_at"])


def downgrade() -> None:
    with op.batch_alter_table("search_history", recreate="auto") as batch_op:
        batch_op.drop_index("ix_search_history_user_updated")
        batch_op.drop_index("ix_search_history_user_query")
        batch_op.drop_constraint("fk_search_history_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
        batch_op.create_index("ix_search_history_query", ["query"], unique=True)
        batch_op.create_index("ix_search_history_updated_at", ["updated_at"])

    with op.batch_alter_table("canvas_frames", recreate="auto") as batch_op:
        batch_op.drop_index("ix_canvas_frames_user_id")
        batch_op.drop_constraint("fk_canvas_frames_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("study_canvas_nodes", recreate="auto") as batch_op:
        batch_op.drop_index("ix_canvas_nodes_user_id")
        batch_op.drop_constraint("fk_study_canvas_nodes_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("study_relations", recreate="auto") as batch_op:
        batch_op.drop_index("ix_study_relations_user_id")
        batch_op.drop_constraint("fk_study_relations_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("categories", recreate="auto") as batch_op:
        batch_op.drop_index("ix_categories_user_id")
        batch_op.drop_constraint("fk_categories_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("studies", recreate="auto") as batch_op:
        batch_op.drop_index("ix_studies_user_deleted")
        batch_op.drop_index("ix_studies_user_id")
        batch_op.drop_constraint("fk_studies_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("books", recreate="auto") as batch_op:
        batch_op.drop_index("ix_books_user_deleted")
        batch_op.drop_index("ix_books_user_id")
        batch_op.drop_constraint("fk_books_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
