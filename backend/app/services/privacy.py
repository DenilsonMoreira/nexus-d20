import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AuditLog,
    Campaign,
    CampaignMember,
    Character,
    DashboardLayout,
    MediaAsset,
    Note,
    PasswordResetToken,
    Session,
    User,
)
from app.services.auth import hash_password


async def export_account_data(db: AsyncSession, user: User) -> dict[str, Any]:
    memberships = list(
        (
            await db.execute(
                select(CampaignMember, Campaign)
                .join(Campaign, Campaign.id == CampaignMember.campaign_id)
                .where(CampaignMember.user_id == user.id)
            )
        ).all()
    )
    characters = list(
        (await db.scalars(select(Character).where(Character.owner_user_id == user.id))).all()
    )
    notes = list((await db.scalars(select(Note).where(Note.owner_user_id == user.id))).all())
    audits = list(
        (
            await db.scalars(
                select(AuditLog)
                .where(AuditLog.actor_user_id == user.id)
                .order_by(AuditLog.created_at)
            )
        ).all()
    )
    return {
        "profile": {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "created_at": user.created_at.isoformat(),
        },
        "campaigns": [
            {
                "id": str(campaign.id),
                "name": campaign.name,
                "role": member.role,
                "is_archived": campaign.is_archived,
            }
            for member, campaign in memberships
        ],
        "characters": [
            {
                "id": str(character.id),
                "campaign_id": str(character.campaign_id),
                "name": character.name,
                "level": character.level,
                "class_name": character.class_name,
            }
            for character in characters
        ],
        "notes": [
            {
                "id": str(note.id),
                "campaign_id": str(note.campaign_id),
                "title": note.title,
                "body": note.body,
                "visibility": note.visibility,
            }
            for note in notes
        ],
        "audit_events": [
            {
                "id": str(audit.id),
                "campaign_id": str(audit.campaign_id),
                "action": audit.action,
                "created_at": audit.created_at.isoformat(),
            }
            for audit in audits
        ],
    }


async def delete_account_data(db: AsyncSession, user: User) -> list[str]:
    media_keys = list(
        (
            await db.scalars(
                select(MediaAsset.object_key)
                .join(Note, Note.id == MediaAsset.note_id)
                .where(Note.owner_user_id == user.id)
            )
        ).all()
    )
    await db.execute(
        update(Campaign)
        .where(Campaign.owner_user_id == user.id)
        .values(is_archived=True)
    )
    await db.execute(delete(DashboardLayout).where(DashboardLayout.owner_user_id == user.id))
    await db.execute(delete(Note).where(Note.owner_user_id == user.id))
    await db.execute(delete(Character).where(Character.owner_user_id == user.id))
    await db.execute(delete(CampaignMember).where(CampaignMember.user_id == user.id))
    await db.execute(delete(Session).where(Session.user_id == user.id))
    await db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
    suffix = uuid.uuid4().hex
    user.email = f"deleted-{suffix}@invalid.local"
    user.display_name = "Conta excluída"
    user.password_hash = hash_password(uuid.uuid4().hex + uuid.uuid4().hex)
    user.is_active = False
    user.auth_version += 1
    await db.flush()
    return media_keys


def export_timestamp() -> datetime:
    return datetime.now(UTC)
