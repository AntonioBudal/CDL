"""Adicionar categorias e taxonomia de livros.

Revision ID: 0005_add_categories_and_taxonomy
Revises: 0004_add_book_cover_image
"""
import json
from pathlib import Path
from alembic import op
import sqlalchemy as sa

revision = "0005_add_categories_and_taxonomy"
down_revision = "0004_add_book_cover_image"
branch_labels = None
depends_on = None


def upgrade() -> None:
    categories_table = op.create_table(
        "categories",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("parent_id", sa.Text(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("length(trim(id)) > 0", name="category_id_not_blank"),
        sa.CheckConstraint("length(trim(name)) > 0", name="category_name_not_blank"),
    )
    op.create_index("ix_categories_parent_id", "categories", ["parent_id"])
    op.create_index("ix_categories_path", "categories", ["path"])

    op.create_table(
        "book_categories",
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("category_id", sa.Text(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), primary_key=True),
    )
    op.create_index("ix_book_categories_category_book", "book_categories", ["category_id", "book_id"])

    # Carregar catálogo inicial canônico se disponível
    json_path = Path(__file__).resolve().parents[2] / "app" / "data" / "canonical_categories.json"
    if json_path.is_file():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_cats = json.load(f)

            # Construir mapa de nomes e caminhos
            cat_map = {c["id"]: c for c in raw_cats}
            rows = []
            for c in raw_cats:
                # Construir caminho hierárquico
                parts = [c["name"]]
                curr = c
                visited = {c["id"]}
                while curr.get("parent_id") and curr["parent_id"] in cat_map:
                    pid = curr["parent_id"]
                    if pid in visited:
                        break
                    visited.add(pid)
                    curr = cat_map[pid]
                    parts.append(curr["name"])
                path = " / ".join(reversed(parts))
                rows.append({
                    "id": c["id"],
                    "name": c["name"],
                    "parent_id": c.get("parent_id"),
                    "path": path,
                })

            if rows:
                op.bulk_insert(categories_table, rows)
        except Exception:
            pass

    op.execute("PRAGMA optimize")


def downgrade() -> None:
    op.drop_table("book_categories")
    op.drop_table("categories")
