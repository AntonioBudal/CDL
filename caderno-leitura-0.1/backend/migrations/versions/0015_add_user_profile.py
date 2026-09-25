"""Adicionar tabela user_profiles para perfil e governança de privacidade.

Revision ID: 0015_add_user_profile
Revises: 0014_add_sync_versioning_and_preferences
"""
from alembic import op
import sqlalchemy as sa

revision = "0015_add_user_profile"
down_revision = "0014_add_sync_versioning_and_preferences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "username",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "display_name",
            sa.String(length=60),
            nullable=False,
        ),
        sa.Column(
            "avatar_url",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "bio",
            sa.String(length=280),
            nullable=True,
        ),
        sa.Column(
            "profile_visibility",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'public'"),
        ),
        sa.Column(
            "dashboard_visibility",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'private'"),
        ),
        sa.Column(
            "is_discoverable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "show_reading_stats",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint("profile_visibility IN ('public', 'friends', 'private')", name="chk_profile_visibility"),
        sa.CheckConstraint("dashboard_visibility IN ('public', 'friends', 'private')", name="chk_dashboard_visibility"),
        sa.CheckConstraint("length(trim(username)) >= 3 AND length(trim(username)) <= 30", name="chk_username_length"),
        sa.CheckConstraint("length(trim(display_name)) >= 1 AND length(trim(display_name)) <= 60", name="chk_display_name_length"),
        sa.CheckConstraint("bio IS NULL OR length(bio) <= 280", name="chk_bio_length"),
    )
    op.create_index("ix_user_profiles_username", "user_profiles", ["username"], unique=True)

    # Auto-provisionamento idempotente para contas de usuários existentes no banco
    op.execute(
        """
        INSERT OR IGNORE INTO user_profiles (
            user_id, username, display_name, profile_visibility, dashboard_visibility, is_discoverable, show_reading_stats
        )
        SELECT id, username, display_name, 'public', 'private', 1, 1 FROM users
        """
    )


def downgrade() -> None:
    op.drop_index("ix_user_profiles_username", table_name="user_profiles")
    op.drop_table("user_profiles")
