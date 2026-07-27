"""add note links and media

Revision ID: 0009_notes_media
Revises: 0008_inventory
Create Date: 2026-07-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_notes_media"
down_revision: Union[str, None] = "0008_inventory"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_check_constraint(
        "visibility_allowed", "notes", "visibility IN ('private', 'shared')"
    )
    op.create_index(op.f("ix_notes_campaign_id"), "notes", ["campaign_id"])
    op.create_index(op.f("ix_notes_owner_user_id"), "notes", ["owner_user_id"])
    op.create_table(
        "note_links",
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(40), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE", name=op.f("fk_note_links_note_id_notes")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_note_links")),
        sa.UniqueConstraint("note_id", "entity_type", "entity_id", name=op.f("uq_note_links_note_id")),
    )
    op.create_index(op.f("ix_note_links_note_id"), "note_links", ["note_id"])
    op.create_table(
        "media_assets",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("object_key", sa.String(500), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE", name=op.f("fk_media_assets_campaign_id_campaigns")),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE", name=op.f("fk_media_assets_note_id_notes")),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], name=op.f("fk_media_assets_owner_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_media_assets")),
        sa.UniqueConstraint("object_key", name=op.f("uq_media_assets_object_key")),
    )
    op.create_index(op.f("ix_media_assets_campaign_id"), "media_assets", ["campaign_id"])
    op.create_index(op.f("ix_media_assets_note_id"), "media_assets", ["note_id"])
    op.create_index(op.f("ix_media_assets_owner_user_id"), "media_assets", ["owner_user_id"])


def downgrade() -> None:
    op.drop_table("media_assets")
    op.drop_table("note_links")
    op.drop_index(op.f("ix_notes_owner_user_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_campaign_id"), table_name="notes")
    op.drop_constraint(op.f("ck_notes_visibility_allowed"), "notes", type_="check")
