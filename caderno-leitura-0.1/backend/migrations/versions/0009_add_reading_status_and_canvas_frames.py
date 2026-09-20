"""Adicionar reading_status em studies e tabela canvas_frames.

Revision ID: 0009_add_reading_status_and_canvas_frames
Revises: 0008_add_study_relations
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_add_reading_status_and_canvas_frames"
down_revision = "0008_add_study_relations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Adicionar reading_status em studies
    with op.batch_alter_table("studies") as batch_op:
        batch_op.add_column(
            sa.Column("reading_status", sa.String(length=20), server_default="rascunho", nullable=False)
        )
        batch_op.create_index("ix_studies_reading_status", ["reading_status"])

    # 2. Criar tabela canvas_frames
    op.create_table(
        "canvas_frames",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=32), server_default="neutral", nullable=False),
        sa.Column("pos_x", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("pos_y", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("width", sa.Float(), server_default="400.0", nullable=False),
        sa.Column("height", sa.Float(), server_default="300.0", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("width >= 100.0 AND height >= 80.0", name="ck_canvas_frames_dimensions"),
    )
    op.create_index("ix_canvas_frames_book_id", "canvas_frames", ["book_id"])


def downgrade() -> None:
    op.drop_index("ix_canvas_frames_book_id", table_name="canvas_frames")
    op.drop_table("canvas_frames")

    with op.batch_alter_table("studies") as batch_op:
        batch_op.drop_index("ix_studies_reading_status")
        batch_op.drop_column("reading_status")
