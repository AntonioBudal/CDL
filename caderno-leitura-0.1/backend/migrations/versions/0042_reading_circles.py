"""Círculos de leitura com trava anti-spoiler (F0.12.07, spec 120).

Só cria quatro tabelas novas (círculos, partes, membros e mensagens). Nada que já existe muda.

Revision ID: 0042_reading_circles
Revises: 0041_image_occlusion_cards
"""
from alembic import op
import sqlalchemy as sa

revision = "0042_reading_circles"
down_revision = "0041_image_occlusion_cards"
branch_labels = None
depends_on = None


def _timestamps():
    return [
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "reading_circles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.String(length=36),
                  sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_reading_circles_owner_id_users"),
                  nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("book_title", sa.Text(), nullable=False),
        sa.Column("book_author", sa.Text(), nullable=True),
        sa.Column("isbn", sa.String(length=13), nullable=True),
        sa.Column("source_book_id", sa.Integer(),
                  sa.ForeignKey("books.id", ondelete="SET NULL", name="fk_reading_circles_source_book_id_books"),
                  nullable=True),
        *_timestamps(),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_reading_circles"),
    )
    op.create_index("ix_reading_circles_owner_id", "reading_circles", ["owner_id"])

    op.create_table(
        "reading_circle_parts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("circle_id", sa.Integer(),
                  sa.ForeignKey("reading_circles.id", ondelete="CASCADE",
                                name="fk_reading_circle_parts_circle_id_reading_circles"),
                  nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.CheckConstraint("position >= 1", name="ck_reading_circle_parts_chk_circle_part_position"),
        sa.PrimaryKeyConstraint("id", name="pk_reading_circle_parts"),
        sa.UniqueConstraint("circle_id", "position", name="uq_reading_circle_parts_circle_id"),
    )

    op.create_table(
        "reading_circle_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("circle_id", sa.Integer(),
                  sa.ForeignKey("reading_circles.id", ondelete="CASCADE",
                                name="fk_reading_circle_members_circle_id_reading_circles"),
                  nullable=False),
        sa.Column("user_id", sa.String(length=36),
                  sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_reading_circle_members_user_id_users"),
                  nullable=False),
        sa.Column("role", sa.String(length=10), server_default=sa.text("'member'"), nullable=False),
        sa.Column("status", sa.String(length=10), server_default=sa.text("'invited'"), nullable=False),
        sa.Column("progress", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("finished", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("invited_by", sa.String(length=36),
                  sa.ForeignKey("users.id", ondelete="SET NULL", name="fk_reading_circle_members_invited_by_users"),
                  nullable=True),
        *_timestamps(),
        sa.Column("joined_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("role IN ('owner', 'member')", name="ck_reading_circle_members_chk_circle_member_role"),
        sa.CheckConstraint("status IN ('invited', 'active')",
                           name="ck_reading_circle_members_chk_circle_member_status"),
        sa.CheckConstraint("progress >= 0", name="ck_reading_circle_members_chk_circle_member_progress"),
        sa.PrimaryKeyConstraint("id", name="pk_reading_circle_members"),
        sa.UniqueConstraint("circle_id", "user_id", name="uq_reading_circle_members_circle_id"),
    )
    op.create_index("ix_reading_circle_members_user_id", "reading_circle_members", ["user_id"])

    op.create_table(
        "reading_circle_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("circle_id", sa.Integer(),
                  sa.ForeignKey("reading_circles.id", ondelete="CASCADE",
                                name="fk_reading_circle_posts_circle_id_reading_circles"),
                  nullable=False),
        sa.Column("part_id", sa.Integer(),
                  sa.ForeignKey("reading_circle_parts.id", ondelete="CASCADE",
                                name="fk_reading_circle_posts_part_id_reading_circle_parts"),
                  nullable=False),
        sa.Column("author_id", sa.String(length=36),
                  sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_reading_circle_posts_author_id_users"),
                  nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        *_timestamps(),
        sa.Column("edited_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("length(trim(body)) > 0", name="ck_reading_circle_posts_chk_circle_post_body"),
        sa.PrimaryKeyConstraint("id", name="pk_reading_circle_posts"),
    )
    op.create_index("ix_reading_circle_posts_part_id", "reading_circle_posts", ["part_id"])
    op.create_index("ix_reading_circle_posts_circle_id", "reading_circle_posts", ["circle_id"])


def downgrade() -> None:
    op.drop_index("ix_reading_circle_posts_circle_id", table_name="reading_circle_posts")
    op.drop_index("ix_reading_circle_posts_part_id", table_name="reading_circle_posts")
    op.drop_table("reading_circle_posts")
    op.drop_index("ix_reading_circle_members_user_id", table_name="reading_circle_members")
    op.drop_table("reading_circle_members")
    op.drop_table("reading_circle_parts")
    op.drop_index("ix_reading_circles_owner_id", table_name="reading_circles")
    op.drop_table("reading_circles")
