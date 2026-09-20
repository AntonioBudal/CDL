"""Adicionar tabela study_relations para conexões semânticas entre estudos.

Revision ID: 0008_add_study_relations
Revises: 0007_add_study_canvas_nodes
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_add_study_relations"
down_revision = "0007_add_study_canvas_nodes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "study_relations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("source_study_id", sa.Integer(), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_study_id", sa.Integer(), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("source_study_id != target_study_id", name="ck_study_relations_no_self"),
        sa.CheckConstraint(
            "relation_type IN ('relacionado_com', 'complementa', 'contradiz', 'depende_de', 'mesmo_tema', 'desdobramento_de')",
            name="ck_study_relations_type",
        ),
        sa.UniqueConstraint("source_study_id", "target_study_id", "relation_type", name="uq_study_relations_src_tgt_type"),
    )
    op.create_index("ix_study_relations_source", "study_relations", ["source_study_id"])
    op.create_index("ix_study_relations_target", "study_relations", ["target_study_id"])


def downgrade() -> None:
    op.drop_index("ix_study_relations_target", table_name="study_relations")
    op.drop_index("ix_study_relations_source", table_name="study_relations")
    op.drop_table("study_relations")
