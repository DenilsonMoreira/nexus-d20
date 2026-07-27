"""complete persistent progression and spells

Revision ID: 0011_progression_spells
Revises: 46da5e423370
Create Date: 2026-07-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_progression_spells"
down_revision: Union[str, None] = "46da5e423370"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "character_class_levels",
        sa.Column("character_id", sa.UUID(), nullable=False),
        sa.Column("class_id", sa.String(length=30), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("subclass_id", sa.String(length=60), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("level BETWEEN 1 AND 20", name=op.f("ck_character_class_levels_level_range")),
        sa.ForeignKeyConstraint(
            ["character_id"], ["characters.id"],
            name=op.f("fk_character_class_levels_character_id_characters"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_character_class_levels")),
        sa.UniqueConstraint("character_id", "class_id", name=op.f("uq_character_class_levels_character_id")),
    )
    op.create_index(op.f("ix_character_class_levels_character_id"), "character_class_levels", ["character_id"])
    op.create_table(
        "character_spells",
        sa.Column("character_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("spell_level", sa.Integer(), nullable=False),
        sa.Column("is_known", sa.Boolean(), nullable=False),
        sa.Column("is_prepared", sa.Boolean(), nullable=False),
        sa.Column("in_spellbook", sa.Boolean(), nullable=False),
        sa.Column("source_class_id", sa.String(length=30), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("spell_level BETWEEN 0 AND 9", name=op.f("ck_character_spells_spell_level_range")),
        sa.ForeignKeyConstraint(
            ["character_id"], ["characters.id"],
            name=op.f("fk_character_spells_character_id_characters"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_character_spells")),
        sa.UniqueConstraint("character_id", "name", name=op.f("uq_character_spells_character_id")),
    )
    op.create_index(op.f("ix_character_spells_character_id"), "character_spells", ["character_id"])
    op.create_table(
        "level_up_events",
        sa.Column("character_id", sa.UUID(), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("result_data", sa.JSON(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["users.id"],
            name=op.f("fk_level_up_events_actor_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["character_id"], ["characters.id"],
            name=op.f("fk_level_up_events_character_id_characters"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_level_up_events")),
        sa.UniqueConstraint("character_id", "idempotency_key", name=op.f("uq_level_up_events_character_id")),
    )
    op.create_index(op.f("ix_level_up_events_character_id"), "level_up_events", ["character_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_level_up_events_character_id"), table_name="level_up_events")
    op.drop_table("level_up_events")
    op.drop_index(op.f("ix_character_spells_character_id"), table_name="character_spells")
    op.drop_table("character_spells")
    op.drop_index(op.f("ix_character_class_levels_character_id"), table_name="character_class_levels")
    op.drop_table("character_class_levels")
