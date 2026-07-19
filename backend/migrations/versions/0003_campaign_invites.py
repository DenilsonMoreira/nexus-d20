"""add campaign invitations and archival

Revision ID: 0003_campaign_invites
Revises: 0002_sessions
Create Date: 2026-07-19
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_campaign_invites"
down_revision: Union[str, None] = "0002_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("is_archived", sa.Boolean(), nullable=True))
    op.execute("UPDATE campaigns SET is_archived = false WHERE is_archived IS NULL")
    op.alter_column("campaigns", "is_archived", nullable=False)
    op.create_table(
        "invites",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invited_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], name="fk_invites_campaign_id_campaigns"),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.id"], name="fk_invites_invited_by_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_invites"),
    )
    op.create_index("ix_invites_campaign_id", "invites", ["campaign_id"], unique=False)
    op.create_index("ix_invites_email", "invites", ["email"], unique=False)
    op.create_index("ix_invites_token_hash", "invites", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_invites_token_hash", table_name="invites")
    op.drop_index("ix_invites_email", table_name="invites")
    op.drop_index("ix_invites_campaign_id", table_name="invites")
    op.drop_table("invites")
    op.drop_column("campaigns", "is_archived")
