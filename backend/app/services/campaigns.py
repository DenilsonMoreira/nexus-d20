import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Campaign, Invite, User
from app.schemas.campaigns import InviteRole
from app.services.auth import token_digest


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
