"""Peso de dificuldade dos itens de revisão e avaliações dos cartões de conceito (F0.11.08, spec 110).

``study_highlights.difficulty_weight`` (anulável; vazio = nunca avaliado) é preenchido a partir de ``last_rating``
(difícil 0,75, médio 0,5, fácil 0,25). ``ADD COLUMN`` simples: a coluna não tem chave estrangeira.
``concept_reviews`` guarda a avaliação de cada cartão de conceito por leitor e chave normalizada do léxico.

Revision ID: 0037_review_difficulty_concepts
Revises: 0036_book_isbn_publisher
"""
from alembic import op
import sqlalchemy as sa

revision = "0037_review_difficulty_concepts"
down_revision = "0036_book_isbn_publisher"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE study_highlights ADD COLUMN difficulty_weight FLOAT")
    op.execute(
        "UPDATE study_highlights SET difficulty_weight = CASE last_rating "
        "WHEN 'hard' THEN 0.75 WHEN 'medium' THEN 0.5 WHEN 'easy' THEN 0.25 END "
        "WHERE last_rating IS NOT NULL"
    )
    op.create_table(
        "concept_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_concept_reviews_user_id_users"),
            nullable=False,
        ),
        sa.Column("concept_key", sa.String(length=200), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("review_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("last_rating", sa.String(length=20), nullable=True),
        sa.Column("difficulty_weight", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "last_rating IS NULL OR last_rating IN ('easy', 'medium', 'hard')",
            name="ck_concept_reviews_chk_concept_review_rating",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_concept_reviews"),
        sa.UniqueConstraint("user_id", "concept_key", name="uq_concept_reviews_user_id"),
    )


def downgrade() -> None:
    op.drop_table("concept_reviews")
    op.execute("ALTER TABLE study_highlights DROP COLUMN difficulty_weight")
