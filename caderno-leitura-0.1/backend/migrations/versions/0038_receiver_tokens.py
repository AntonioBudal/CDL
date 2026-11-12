"""Token de recepção de destaques (F0.11.09, spec 111).

Um por leitor; só o hash SHA-256 é guardado, mais o começo do token para o leitor reconhecê-lo. Sai junto com a conta.

Revision ID: 0038_receiver_tokens
Revises: 0037_review_difficulty_concepts
"""
from alembic import op
import sqlalchemy as sa

revision = "0038_receiver_tokens"
down_revision = "0037_review_difficulty_concepts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "receiver_tokens",
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_receiver_tokens_user_id_users"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("token_hint", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id", name="pk_receiver_tokens"),
        sa.UniqueConstraint("token_hash", name="uq_receiver_tokens_token_hash"),
    )


def downgrade() -> None:
    op.drop_table("receiver_tokens")
