"""Adicionar tabela de study_highlights para destaques e acoes contextuais.

Revision ID: 0020_add_study_highlights
Revises: 0019_add_audit_logs_and_user_lifecycle
"""
from alembic import op
import sqlalchemy as sa

revision = "0020_add_study_highlights"
down_revision = "0019_add_audit_logs_and_user_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "study_highlights",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column(
            "study_id",
            sa.Integer(),
            sa.ForeignKey("studies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            server_default=sa.text("'00000000-0000-0000-0000-000000000001'"),
            nullable=False,
        ),
        sa.Column("section", sa.String(length=30), nullable=False),
        sa.Column("start_offset", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("end_offset", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("selected_text", sa.Text(), nullable=False),
        sa.Column("prefix", sa.String(length=150), server_default=sa.text("''"), nullable=False),
        sa.Column("suffix", sa.String(length=150), server_default=sa.text("''"), nullable=False),
        sa.Column("color", sa.String(length=30), server_default=sa.text("'yellow'"), nullable=False),
        sa.Column("kind", sa.String(length=30), server_default=sa.text("'highlight'"), nullable=False),
        sa.Column("note", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "kind IN ('highlight', 'note', 'quote', 'hidden', 'question')",
            name="chk_highlight_kind",
        ),
        sa.CheckConstraint(
            "section IN ('summary', 'explanation', 'concepts', 'references', 'source_response')",
            name="chk_highlight_section",
        ),
        sa.CheckConstraint("length(trim(selected_text)) > 0", name="chk_highlight_text_not_blank"),
        sa.CheckConstraint("start_offset >= 0", name="chk_highlight_start_offset_non_negative"),
        sa.CheckConstraint("end_offset >= start_offset", name="chk_highlight_offsets_valid"),
    )
    op.create_index("ix_study_highlights_study_id", "study_highlights", ["study_id"])
    op.create_index("ix_study_highlights_user_id", "study_highlights", ["user_id"])
    op.create_index("ix_study_highlights_study_section", "study_highlights", ["study_id", "section"])


def downgrade() -> None:
    op.drop_index("ix_study_highlights_study_section", table_name="study_highlights")
    op.drop_index("ix_study_highlights_user_id", table_name="study_highlights")
    op.drop_index("ix_study_highlights_study_id", table_name="study_highlights")
    op.drop_table("study_highlights")
