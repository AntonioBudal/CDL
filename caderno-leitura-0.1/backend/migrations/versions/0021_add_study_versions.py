"""Adicionar tabela de study_versions para historico automatico.

Revision ID: 0021_add_study_versions
Revises: 0020_add_study_highlights
"""
from alembic import op
import sqlalchemy as sa

revision = "0021_add_study_versions"
down_revision = "0020_add_study_highlights"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "study_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column(
            "study_id",
            sa.Integer(),
            sa.ForeignKey("studies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("explanation", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("concepts", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("references", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("notes", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("highlights_data", sa.Text(), server_default=sa.text("'[]'"), nullable=False),
        sa.Column("change_summary", sa.String(length=100), server_default=sa.text("'Edição'"), nullable=False),
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
        sa.UniqueConstraint("study_id", "version_number", name="uq_study_version_number"),
    )
    op.create_index("ix_study_versions_study_id", "study_versions", ["study_id"])
    op.create_index("ix_study_versions_user_id", "study_versions", ["user_id"])
    op.create_index("ix_study_versions_study_created", "study_versions", ["study_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_study_versions_study_created", table_name="study_versions")
    op.drop_index("ix_study_versions_user_id", table_name="study_versions")
    op.drop_index("ix_study_versions_study_id", table_name="study_versions")
    op.drop_table("study_versions")
