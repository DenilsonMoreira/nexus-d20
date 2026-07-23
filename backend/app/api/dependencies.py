import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.errors import AppError
from app.models import Campaign, CampaignMember, User
from app.services.auth import decode_access_token

DatabaseSession = Annotated[AsyncSession, Depends(get_session)]
AccessCookie = Annotated[str | None, Cookie()]


async def get_current_user(
    db: DatabaseSession,
    access_token: AccessCookie = None,
) -> User:
    if access_token is None:
        raise AppError(401, "authentication_required", "Autenticação necessária.")
    user_id, auth_version = decode_access_token(access_token)
    user = await db.get(User, user_id)
    if user is None or not user.is_active or user.auth_version != auth_version:
        raise AppError(401, "authentication_required", "Autenticação necessária.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@dataclass(frozen=True)
class CampaignAccess:
    campaign: Campaign
    member: CampaignMember


async def get_campaign_access(
    campaign_id: uuid.UUID,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CampaignAccess:
    row = (
        await db.execute(
            select(Campaign, CampaignMember)
            .join(CampaignMember, CampaignMember.campaign_id == Campaign.id)
            .where(
                Campaign.id == campaign_id,
                CampaignMember.user_id == current_user.id,
                Campaign.is_archived.is_(False),
            )
        )
    ).one_or_none()
    if row is None:
        raise AppError(404, "campaign_not_found", "Campanha não encontrada.")
    return CampaignAccess(campaign=row[0], member=row[1])


CampaignAccessDependency = Annotated[CampaignAccess, Depends(get_campaign_access)]


async def require_campaign_master(
    access: CampaignAccessDependency,
) -> CampaignAccess:
    if access.member.role != "master":
        raise AppError(403, "master_role_required", "Apenas o mestre pode realizar esta ação.")
    return access


CampaignMaster = Annotated[CampaignAccess, Depends(require_campaign_master)]
