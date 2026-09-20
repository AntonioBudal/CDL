"""Adicionar tabela study_canvas_nodes para layout espacial 2D isolado.

Revision ID: 0007_add_study_canvas_nodes
Revises: 0006_add_study_hierarchy_and_position
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_add_study_canvas_nodes"
down_revision = "0006_add_study_hierarchy_and_position"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "study_canvas_nodes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), nullable=False),
        sa.Column("pos_x", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("pos_y", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("width", sa.Float(), nullable=True),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("z_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("color_tag", sa.String(length=32), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("study_id", "book_id", name="uq_canvas_node_study_book"),
    )
    op.create_index("ix_canvas_nodes_book_study", "study_canvas_nodes", ["book_id", "study_id"])


def downgrade() -> None:
    op.drop_index("ix_canvas_nodes_book_study", table_name="study_canvas_nodes")
    op.drop_table("study_canvas_nodes")
