"""Cartões de oclusão de imagem (F0.12.06, spec 119).

Só cria a tabela ``image_occlusion_cards``: um retângulo (coordenadas relativas 0–1) sobre uma imagem do cofre ligada a
um estudo, com os campos de revisão. Nada que já existe muda. Apagar a imagem ou o estudo apaga os cartões (CASCADE).

Revision ID: 0041_image_occlusion_cards
Revises: 0040_study_published_at
"""
from alembic import op
import sqlalchemy as sa

revision = "0041_image_occlusion_cards"
down_revision = "0040_study_published_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "image_occlusion_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_image_occlusion_cards_user_id_users"),
            nullable=False,
        ),
        sa.Column(
            "study_id",
            sa.Integer(),
            sa.ForeignKey("studies.id", ondelete="CASCADE", name="fk_image_occlusion_cards_study_id_studies"),
            nullable=False,
        ),
        sa.Column(
            "media_id",
            sa.String(length=36),
            sa.ForeignKey(
                "encrypted_media.id", ondelete="CASCADE", name="fk_image_occlusion_cards_media_id_encrypted_media"
            ),
            nullable=False,
        ),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("label", sa.String(length=200), server_default=sa.text("''"), nullable=False),
        sa.Column("position", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("review_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("last_rating", sa.String(length=20), nullable=True),
        sa.Column("difficulty_weight", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "x >= 0 AND y >= 0 AND width > 0 AND height > 0 AND x + width <= 1.000001 AND y + height <= 1.000001",
            name="ck_image_occlusion_cards_chk_occlusion_box",
        ),
        sa.CheckConstraint(
            "last_rating IS NULL OR last_rating IN ('easy', 'medium', 'hard')",
            name="ck_image_occlusion_cards_chk_occlusion_rating",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_image_occlusion_cards"),
    )
    op.create_index("ix_image_occlusion_cards_media_id", "image_occlusion_cards", ["media_id"])
    op.create_index("ix_image_occlusion_cards_user_id", "image_occlusion_cards", ["user_id"])
    op.create_index("ix_image_occlusion_cards_study_id", "image_occlusion_cards", ["study_id"])


def downgrade() -> None:
    op.drop_index("ix_image_occlusion_cards_study_id", table_name="image_occlusion_cards")
    op.drop_index("ix_image_occlusion_cards_user_id", table_name="image_occlusion_cards")
    op.drop_index("ix_image_occlusion_cards_media_id", table_name="image_occlusion_cards")
    op.drop_table("image_occlusion_cards")
