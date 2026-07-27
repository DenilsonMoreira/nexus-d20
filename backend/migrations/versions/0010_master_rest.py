"""add master dashboard and long rest state

Revision ID: 0010_master_rest
Revises: 0009_notes_media
Create Date: 2026-07-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_master_rest"
down_revision: Union[str, None] = "0009_notes_media"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.add_column("characters", sa.Column("is_active_group", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("characters", sa.Column("hit_dice_current", sa.Integer(), server_default="1", nullable=False))
    op.add_column("characters", sa.Column("hit_dice_max", sa.Integer(), server_default="1", nullable=False))
    op.add_column("characters", sa.Column("exhaustion_level", sa.Integer(), server_default="0", nullable=False))
    op.add_column("characters", sa.Column("hidden_fatigue", sa.Integer(), server_default="0", nullable=False))
    op.create_check_constraint("hit_dice_range", "characters", "hit_dice_current >= 0 AND hit_dice_current <= hit_dice_max")
    op.create_check_constraint("hit_dice_max_positive", "characters", "hit_dice_max >= 1")
    op.create_check_constraint("exhaustion_range", "characters", "exhaustion_level BETWEEN 0 AND 6")
    op.create_check_constraint("hidden_fatigue_positive", "characters", "hidden_fatigue >= 0")
    op.create_table(
        "character_spell_slots",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("current_value", sa.Integer(), nullable=False),
        sa.Column("maximum_value", sa.Integer(), nullable=False),
        *timestamps(),
        sa.CheckConstraint("level BETWEEN 1 AND 9", name=op.f("ck_character_spell_slots_level_range")),
        sa.CheckConstraint("current_value >= 0 AND current_value <= maximum_value", name=op.f("ck_character_spell_slots_current_value_range")),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE", name=op.f("fk_character_spell_slots_character_id_characters")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_character_spell_slots")),
        sa.UniqueConstraint("character_id", "level", name=op.f("uq_character_spell_slots_character_id")),
    )
    op.create_index(op.f("ix_character_spell_slots_character_id"), "character_spell_slots", ["character_id"])
    op.create_table(
        "character_conditions",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("expires_on_long_rest", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE", name=op.f("fk_character_conditions_character_id_characters")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_character_conditions")),
    )
    op.create_index(op.f("ix_character_conditions_character_id"), "character_conditions", ["character_id"])
    op.create_table(
        "long_rest_events",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(120), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("result_data", sa.JSON(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE", name=op.f("fk_long_rest_events_campaign_id_campaigns")),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE", name=op.f("fk_long_rest_events_character_id_characters")),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], name=op.f("fk_long_rest_events_actor_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_long_rest_events")),
        sa.UniqueConstraint("campaign_id", "idempotency_key", name=op.f("uq_long_rest_events_campaign_id")),
    )
    op.create_index(op.f("ix_long_rest_events_campaign_id"), "long_rest_events", ["campaign_id"])
    op.create_index(op.f("ix_long_rest_events_character_id"), "long_rest_events", ["character_id"])


def downgrade() -> None:
    op.drop_table("long_rest_events")
    op.drop_table("character_conditions")
    op.drop_table("character_spell_slots")
    for constraint in ("hidden_fatigue_positive", "exhaustion_range", "hit_dice_max_positive", "hit_dice_range"):
        op.drop_constraint(op.f(f"ck_characters_{constraint}"), "characters", type_="check")
    for column in ("hidden_fatigue", "exhaustion_level", "hit_dice_max", "hit_dice_current", "is_active_group"):
        op.drop_column("characters", column)
