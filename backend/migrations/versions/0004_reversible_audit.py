"""add reversible audit metadata

Revision ID: 0004_reversible_audit
Revises: 0003_campaign_invites
Create Date: 2026-07-19
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_reversible_audit"
down_revision: Union[str, None] = "0003_campaign_invites"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audit_logs", sa.Column("is_reversible", sa.Boolean(), nullable=True))
    op.execute("UPDATE audit_logs SET is_reversible = false WHERE is_reversible IS NULL")
    op.alter_column("audit_logs", "is_reversible", nullable=False)
    op.add_column("audit_logs", sa.Column("reversed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "audit_logs",
        sa.Column("reversed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("audit_logs", sa.Column("reversal_reason", sa.Text(), nullable=True))
    op.add_column(
        "audit_logs", sa.Column("reversal_of_id", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_foreign_key(
        "fk_audit_logs_reversed_by_user_id_users",
        "audit_logs",
        "users",
        ["reversed_by_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_audit_logs_reversal_of_id_audit_logs",
        "audit_logs",
        "audit_logs",
        ["reversal_of_id"],
        ["id"],
    )
    op.create_index(
        "ix_audit_logs_reversal_of_id", "audit_logs", ["reversal_of_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_reversal_of_id", table_name="audit_logs")
    op.drop_constraint(
        "fk_audit_logs_reversal_of_id_audit_logs", "audit_logs", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_audit_logs_reversed_by_user_id_users", "audit_logs", type_="foreignkey"
    )
    op.drop_column("audit_logs", "reversal_of_id")
    op.drop_column("audit_logs", "reversal_reason")
    op.drop_column("audit_logs", "reversed_by_user_id")
    op.drop_column("audit_logs", "reversed_at")
    op.drop_column("audit_logs", "is_reversible")
