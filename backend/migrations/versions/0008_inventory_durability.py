"""add inventory and durability

Revision ID: 0008_inventory
Revises: 0007_character_details
Create Date: 2026-07-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_inventory"
down_revision: Union[str, None] = "0007_character_details"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "materials",
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("base_points", sa.Integer(), nullable=False),
        sa.Column("craft_domain", sa.String(40), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_materials")),
        sa.UniqueConstraint("code", name=op.f("uq_materials_code")),
    )
    op.create_table(
        "quality_levels",
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("multiplier", sa.Numeric(8, 4), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quality_levels")),
        sa.UniqueConstraint("code", name=op.f("uq_quality_levels_code")),
    )
    materials = sa.table(
        "materials",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("base_points", sa.Integer),
        sa.column("craft_domain", sa.String),
    )
    qualities = sa.table(
        "quality_levels",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("multiplier", sa.Numeric),
    )
    op.bulk_insert(materials, [
        {"id": "00000000-0000-0000-0000-000000000101", "code": "iron", "name": "Ferro", "base_points": 80, "craft_domain": "smithing"},
        {"id": "00000000-0000-0000-0000-000000000102", "code": "steel", "name": "Aço", "base_points": 120, "craft_domain": "smithing"},
        {"id": "00000000-0000-0000-0000-000000000103", "code": "wood", "name": "Madeira", "base_points": 50, "craft_domain": "woodworking"},
        {"id": "00000000-0000-0000-0000-000000000104", "code": "leather", "name": "Couro", "base_points": 60, "craft_domain": "leatherworking"},
    ])
    op.bulk_insert(qualities, [
        {"id": "00000000-0000-0000-0000-000000000201", "code": "poor", "name": "Inferior", "multiplier": 0.75},
        {"id": "00000000-0000-0000-0000-000000000202", "code": "standard", "name": "Comum", "multiplier": 1},
        {"id": "00000000-0000-0000-0000-000000000203", "code": "fine", "name": "Refinada", "multiplier": 1.25},
        {"id": "00000000-0000-0000-0000-000000000204", "code": "masterwork", "name": "Obra-prima", "multiplier": 1.5},
    ])
    op.create_table(
        "item_templates",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("craft_domain", sa.String(40), nullable=False),
        sa.Column("base_damage_die", sa.String(12), nullable=False),
        sa.Column("weight_kg", sa.Numeric(10, 3), nullable=False),
        sa.Column("price_gp", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE", name=op.f("fk_item_templates_campaign_id_campaigns")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_item_templates")),
    )
    op.create_index(op.f("ix_item_templates_campaign_id"), "item_templates", ["campaign_id"])
    op.create_table(
        "item_template_versions",
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quality_level_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("structure_multiplier", sa.Numeric(8, 4), nullable=False),
        sa.Column("magic_multiplier", sa.Numeric(8, 4), nullable=False),
        sa.Column("is_magical", sa.Boolean(), nullable=False),
        sa.Column("auto_repair_percent", sa.Numeric(6, 2), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["template_id"], ["item_templates.id"], ondelete="CASCADE", name=op.f("fk_item_template_versions_template_id_item_templates")),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], name=op.f("fk_item_template_versions_material_id_materials")),
        sa.ForeignKeyConstraint(["quality_level_id"], ["quality_levels.id"], name=op.f("fk_item_template_versions_quality_level_id_quality_levels")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_item_template_versions")),
        sa.UniqueConstraint("template_id", "version_number", name="uq_item_template_version"),
    )
    op.create_index(op.f("ix_item_template_versions_template_id"), "item_template_versions", ["template_id"])
    op.create_table(
        "character_professions",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(40), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE", name=op.f("fk_character_professions_character_id_characters")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_character_professions")),
        sa.UniqueConstraint("character_id", "domain", name="uq_character_profession_domain"),
    )
    op.create_index(op.f("ix_character_professions_character_id"), "character_professions", ["character_id"])
    op.create_table(
        "item_instances",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("current_durability", sa.Integer(), nullable=False),
        sa.Column("maximum_durability", sa.Integer(), nullable=False),
        sa.Column("equipped", sa.Boolean(), nullable=False),
        sa.Column("is_active_weapon", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.CheckConstraint("quantity >= 1", name=op.f("ck_item_instances_quantity_positive")),
        sa.CheckConstraint("current_durability >= 0 AND current_durability <= maximum_durability", name=op.f("ck_item_instances_durability_range")),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE", name=op.f("fk_item_instances_campaign_id_campaigns")),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE", name=op.f("fk_item_instances_character_id_characters")),
        sa.ForeignKeyConstraint(["template_version_id"], ["item_template_versions.id"], name=op.f("fk_item_instances_template_version_id_item_template_versions")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_item_instances")),
    )
    op.create_index(op.f("ix_item_instances_campaign_id"), "item_instances", ["campaign_id"])
    op.create_index(op.f("ix_item_instances_character_id"), "item_instances", ["character_id"])
    op.create_index(op.f("ix_item_instances_template_version_id"), "item_instances", ["template_version_id"])
    op.create_table(
        "durability_events",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_instance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("before_points", sa.Integer(), nullable=False),
        sa.Column("after_points", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE", name=op.f("fk_durability_events_campaign_id_campaigns")),
        sa.ForeignKeyConstraint(["item_instance_id"], ["item_instances.id"], ondelete="CASCADE", name=op.f("fk_durability_events_item_instance_id_item_instances")),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], name=op.f("fk_durability_events_actor_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_durability_events")),
    )
    op.create_index(op.f("ix_durability_events_campaign_id"), "durability_events", ["campaign_id"])
    op.create_index(op.f("ix_durability_events_item_instance_id"), "durability_events", ["item_instance_id"])


def downgrade() -> None:
    for table in ("durability_events", "item_instances", "character_professions", "item_template_versions", "item_templates", "quality_levels", "materials"):
        op.drop_table(table)
