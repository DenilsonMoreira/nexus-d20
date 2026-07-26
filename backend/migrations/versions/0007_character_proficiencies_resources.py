"""add character proficiencies and resources

Revision ID: 0007_character_details
Revises: 0006_characters
Create Date: 2026-07-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_character_details"
down_revision: Union[str, None] = "0006_characters"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "character_proficiencies",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
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
            "category IN ('saving_throw', 'skill', 'language', 'tool', "
            "'weapon', 'armor', 'other')",
            name=op.f("ck_character_proficiencies_category_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            name=op.f("fk_character_proficiencies_character_id_characters"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_character_proficiencies")),
        sa.UniqueConstraint(
            "character_id",
            "category",
            "name",
            name=op.f("uq_character_proficiencies_character_id"),
        ),
    )
    op.create_index(
        op.f("ix_character_proficiencies_character_id"),
        "character_proficiencies",
        ["character_id"],
        unique=False,
    )
    op.create_table(
        "character_resources",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("current_value", sa.Integer(), nullable=False),
        sa.Column("maximum_value", sa.Integer(), nullable=False),
        sa.Column("recovery", sa.String(length=30), nullable=False),
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
            "current_value >= 0 AND current_value <= maximum_value",
            name=op.f("ck_character_resources_current_value_range"),
        ),
        sa.CheckConstraint(
            "maximum_value >= 1",
            name=op.f("ck_character_resources_maximum_value_positive"),
        ),
        sa.CheckConstraint(
            "recovery IN ('short_rest', 'long_rest', 'manual')",
            name=op.f("ck_character_resources_recovery_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            name=op.f("fk_character_resources_character_id_characters"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_character_resources")),
        sa.UniqueConstraint(
            "character_id",
            "name",
            name=op.f("uq_character_resources_character_id"),
        ),
    )
    op.create_index(
        op.f("ix_character_resources_character_id"),
        "character_resources",
        ["character_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_character_resources_character_id"),
        table_name="character_resources",
    )
    op.drop_table("character_resources")
    op.drop_index(
        op.f("ix_character_proficiencies_character_id"),
        table_name="character_proficiencies",
    )
    op.drop_table("character_proficiencies")
