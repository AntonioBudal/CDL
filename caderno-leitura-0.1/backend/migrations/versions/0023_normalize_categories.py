"""Normalizar categorias para taxonomia plana e canônica.

Revision ID: 0023_normalize_categories
Revises: 0022_add_support_settings
"""
from __future__ import annotations

import re
import unicodedata
from alembic import op
import sqlalchemy as sa

revision = "0023_normalize_categories"
down_revision = "0022_add_support_settings"
branch_labels = None
depends_on = None

# Catálogo canônico oficial incorporado diretamente para garantir migração autônoma e determinística
CANONICAL_DEFS = [
    ("antropologia", "Antropologia"),
    ("arte", "Arte"),
    ("biografia", "Biografia"),
    ("ciencia", "Ciência"),
    ("cinema", "Cinema"),
    ("critica", "Crítica"),
    ("direito", "Direito"),
    ("economia", "Economia"),
    ("educacao", "Educação"),
    ("ensaio", "Ensaio"),
    ("ficcao", "Ficção"),
    ("filosofia", "Filosofia"),
    ("historia", "História"),
    ("linguistica", "Linguística"),
    ("literatura", "Literatura"),
    ("medicina", "Medicina"),
    ("musica", "Música"),
    ("poesia", "Poesia"),
    ("politica", "Política"),
    ("psicologia", "Psicologia"),
    ("religiao", "Religião"),
    ("sociologia", "Sociologia"),
    ("teatro", "Teatro"),
    ("tecnologia", "Tecnologia"),
]

LEGACY_MAPPINGS: dict[str, list[str]] = {
    # Plurais simples
    "filosofias": ["filosofia"],
    "historias": ["historia"],
    "ciencias": ["ciencia"],
    "literaturas": ["literatura"],
    "ficcoes": ["ficcao"],
    "poesias": ["poesia"],
    "artes": ["arte"],
    "direitos": ["direito"],
    "economias": ["economia"],
    "politicas": ["politica"],
    "sociologias": ["sociologia"],
    "psicologias": ["psicologia"],
    "tecnologias": ["tecnologia"],
    "religioes": ["religiao"],
    "biografias": ["biografia"],
    "educacoes": ["educacao"],
    # Compostos e legados distributivos
    "ciencias sociais e humanas": ["ciencia", "sociologia"],
    "ciencias sociais": ["sociologia"],
    "ciencias humanas": ["historia", "filosofia"],
    "ciencias naturais": ["ciencia"],
    "ciencias exatas": ["ciencia"],
    "historias de ficcao": ["historia", "ficcao"],
    "ficcao cientifica": ["ficcao", "ciencia"],
    "teorias politicas modernas": ["politica"],
    "ciencia politica": ["politica"],
    "artes visuais": ["arte"],
    "historia da arte": ["historia", "arte"],
    "filosofia politica": ["filosofia", "politica"],
    "filosofia da mente": ["filosofia", "psicologia"],
    "historia e filosofia": ["historia", "filosofia"],
    "estudos literarios": ["literatura"],
    "teoria literaria": ["literatura"],
    "psicanalise": ["psicologia"],
}


def _strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalize_for_search(text: str) -> str:
    clean = re.sub(r"[^\w\s-]", "", _strip_accents(text.strip().lower()))
    return re.sub(r"\s+", " ", clean).strip()


def upgrade() -> None:
    # 1. Adicionar colunas e índice na tabela categories via batch_alter_table (compatível com SQLite)
    with op.batch_alter_table("categories") as batch_op:
        batch_op.add_column(
            sa.Column("normalized_name", sa.Text(), server_default=sa.text("''"), nullable=False)
        )
        batch_op.add_column(
            sa.Column("is_canonical", sa.Boolean(), server_default=sa.text("0"), nullable=False)
        )
        batch_op.create_index("ix_categories_normalized_name", ["normalized_name"])

    conn = op.get_bind()

    # 2. Aplanar todas as categorias existentes (parent_id = NULL, is_canonical = 0)
    conn.execute(sa.text("UPDATE categories SET parent_id = NULL, is_canonical = 0"))

    # 3. Obter categorias existentes
    existing_rows = conn.execute(
        sa.text("SELECT id, name FROM categories")
    ).fetchall()
    existing_ids = {row[0] for row in existing_rows}
    canon_slugs = {c_id for c_id, _ in CANONICAL_DEFS}

    # 4. Inserir ou atualizar termos do catálogo canônico oficial (is_canonical = 1)
    for c_id, c_name in CANONICAL_DEFS:
        norm = _normalize_for_search(c_name)
        if c_id not in existing_ids:
            conn.execute(
                sa.text(
                    "INSERT INTO categories (id, name, normalized_name, is_canonical, parent_id, path) "
                    "VALUES (:id, :name, :norm, 1, NULL, :id)"
                ),
                {"id": c_id, "name": c_name, "norm": norm},
            )
        else:
            conn.execute(
                sa.text(
                    "UPDATE categories "
                    "SET name = :name, normalized_name = :norm, is_canonical = 1, parent_id = NULL, path = :id "
                    "WHERE id = :id"
                ),
                {"id": c_id, "name": c_name, "norm": norm},
            )

    # 5. Atualizar normalized_name e path para categorias não canônicas
    for row in existing_rows:
        cat_id, cat_name = row[0], row[1]
        if cat_id not in canon_slugs:
            norm = _normalize_for_search(cat_name)
            conn.execute(
                sa.text(
                    "UPDATE categories "
                    "SET normalized_name = :norm, path = :id "
                    "WHERE id = :id"
                ),
                {"id": cat_id, "norm": norm},
            )

    # 6. Migração distributiva em book_categories
    book_cats = conn.execute(
        sa.text("SELECT book_id, category_id FROM book_categories")
    ).fetchall()

    cat_map = {row[0]: row[1] for row in existing_rows}
    current_pairs = {(b_id, c_id) for b_id, c_id in book_cats}

    for b_id, c_id in book_cats:
        c_name = cat_map.get(c_id, c_id)
        norm_name = _normalize_for_search(c_name)
        norm_id = _normalize_for_search(c_id)

        target_slugs: list[str] = []
        if norm_name in LEGACY_MAPPINGS:
            target_slugs = LEGACY_MAPPINGS[norm_name]
        elif norm_id in LEGACY_MAPPINGS:
            target_slugs = LEGACY_MAPPINGS[norm_id]
        elif c_id in canon_slugs:
            continue

        if target_slugs:
            for t_slug in target_slugs:
                if (b_id, t_slug) not in current_pairs:
                    conn.execute(
                        sa.text(
                            "INSERT INTO book_categories (book_id, category_id) "
                            "VALUES (:book_id, :category_id)"
                        ),
                        {"book_id": b_id, "category_id": t_slug},
                    )
                    current_pairs.add((b_id, t_slug))

            conn.execute(
                sa.text(
                    "DELETE FROM book_categories WHERE book_id = :book_id AND category_id = :category_id"
                ),
                {"book_id": b_id, "category_id": c_id},
            )
            current_pairs.discard((b_id, c_id))

    op.execute("PRAGMA optimize")


def downgrade() -> None:
    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_index("ix_categories_normalized_name")
        batch_op.drop_column("is_canonical")
        batch_op.drop_column("normalized_name")
