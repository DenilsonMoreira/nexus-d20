import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog, Campaign, Invite, User
from app.schemas.campaigns import InviteRole
from app.services.auth import token_digest


def record_audit(
    db: AsyncSession,
    *,
    campaign: Campaign,
    actor: User,
    action: str,
    entity_type: str,
    after_data: dict[str, object] | None = None,
    before_data: dict[str, object] | None = None,
) -> None:
    db.add(
        AuditLog(
            campaign_id=campaign.id,
            actor_user_id=actor.id,
            entity_type=entity_type,
            entity_id=campaign.id,
            action=action,
            before_data=before_data,
            after_data=after_data,
            reason=None,
        )
    )


def create_invite(
    db: AsyncSession,
    *,
    campaign: Campaign,
    actor: User,
    email: str,
    role: InviteRole,
) -> tuple[Invite, str]:
    token = secrets.token_urlsafe(48)
    invite = Invite(
        campaign_id=campaign.id,
        invited_by_user_id=actor.id,
        email=email,
        role=role,
        token_hash=token_digest(token),
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db.add(invite)
    return invite, token
