"""add basic character sheets

Revision ID: 0006_characters
Revises: 0005_password_reset
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_characters"
down_revision: Union[str, None] = "0005_password_reset"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "characters",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("race_name", sa.String(length=120), nullable=False),
        sa.Column("class_name", sa.String(length=120), nullable=False),
        sa.Column("subclass_name", sa.String(length=120), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("background", sa.String(length=160), nullable=False),
        sa.Column("alignment", sa.String(length=80), nullable=False),
        sa.Column("hit_points_current", sa.Integer(), nullable=False),
        sa.Column("hit_points_max", sa.Integer(), nullable=False),
        sa.Column("temporary_hit_points", sa.Integer(), nullable=False),
        sa.Column("armor_class", sa.Integer(), nullable=False),
        sa.Column("initiative", sa.Integer(), nullable=False),
        sa.Column("speed_meters", sa.Integer(), nullable=False),
        sa.Column("strength", sa.Integer(), nullable=False),
        sa.Column("dexterity", sa.Integer(), nullable=False),
        sa.Column("constitution", sa.Integer(), nullable=False),
        sa.Column("intelligence", sa.Integer(), nullable=False),
        sa.Column("wisdom", sa.Integer(), nullable=False),
        sa.Column("charisma", sa.Integer(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "strength BETWEEN 1 AND 30 AND dexterity BETWEEN 1 AND 30 "
            "AND constitution BETWEEN 1 AND 30 AND intelligence BETWEEN 1 AND 30 "
            "AND wisdom BETWEEN 1 AND 30 AND charisma BETWEEN 1 AND 30",
            name=op.f("ck_characters_ability_scores_range"),
        ),
        sa.CheckConstraint(
            "armor_class BETWEEN 0 AND 99",
            name=op.f("ck_characters_armor_class_range"),
        ),
        sa.CheckConstraint(
            "hit_points_current >= 0 AND hit_points_current <= hit_points_max",
            name=op.f("ck_characters_hit_points_range"),
        ),
        sa.CheckConstraint(
            "hit_points_max >= 1",
            name=op.f("ck_characters_hit_points_max_positive"),
        ),
        sa.CheckConstraint(
            "initiative BETWEEN -20 AND 30",
            name=op.f("ck_characters_initiative_range"),
        ),
        sa.CheckConstraint("level BETWEEN 1 AND 20", name=op.f("ck_characters_level_range")),
        sa.CheckConstraint(
            "speed_meters BETWEEN 0 AND 999",
            name=op.f("ck_characters_speed_meters_range"),
        ),
        sa.CheckConstraint(
            "temporary_hit_points >= 0",
            name=op.f("ck_characters_temporary_hit_points_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["campaigns.id"],
            name=op.f("fk_characters_campaign_id_campaigns"),
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_characters_owner_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_characters")),
    )
    op.create_index(
        op.f("ix_characters_campaign_id"), "characters", ["campaign_id"], unique=False
    )
    op.create_index(
        op.f("ix_characters_owner_user_id"), "characters", ["owner_user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_characters_owner_user_id"), table_name="characters")
    op.drop_index(op.f("ix_characters_campaign_id"), table_name="characters")
    op.drop_table("characters")
