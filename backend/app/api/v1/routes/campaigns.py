import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.dependencies import (
    CampaignAccessDependency,
    CampaignMaster,
    CurrentUser,
    DatabaseSession,
)
from app.core.errors import AppError
from app.models import AuditLog, Campaign, CampaignMember, Invite, User
from app.schemas.campaigns import (
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignMemberListResponse,
    CampaignMemberResponse,
    CampaignResponse,
    CampaignUpdateRequest,
    InviteCreateRequest,
    InviteResponse,
    MemberRoleUpdateRequest,
    MembershipResponse,
)
from app.services.auth import token_digest
from app.services.campaigns import create_invite, record_audit

router = APIRouter()
invite_router = APIRouter()


def campaign_response(campaign: Campaign, role: str) -> CampaignResponse:
    return CampaignResponse(
        id=campaign.id,
        name=campaign.name,
        ruleset_code=campaign.ruleset_code,
        role=role,
        created_at=campaign.created_at,
    )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreateRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CampaignResponse:
    campaign = Campaign(
        name=payload.name.strip(),
        owner_user_id=current_user.id,
        ruleset_code="dnd5e-2014",
        is_archived=False,
    )
    db.add(campaign)
    await db.flush()
    db.add(CampaignMember(campaign_id=campaign.id, user_id=current_user.id, role="master"))
    record_audit(
        db,
        campaign=campaign,
        actor=current_user,
        action="campaign.created",
        entity_type="campaign",
        after_data={"name": campaign.name, "ruleset_code": campaign.ruleset_code},
    )
    await db.commit()
    await db.refresh(campaign)
    return campaign_response(campaign, "master")


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CampaignListResponse:
    rows = (
        await db.execute(
            select(Campaign, CampaignMember.role)
            .join(CampaignMember, CampaignMember.campaign_id == Campaign.id)
            .where(
                CampaignMember.user_id == current_user.id,
                Campaign.is_archived.is_(False),
            )
            .order_by(Campaign.created_at, Campaign.id)
        )
    ).all()
    return CampaignListResponse(
        items=[campaign_response(campaign, role) for campaign, role in rows]
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(access: CampaignAccessDependency) -> CampaignResponse:
    return campaign_response(access.campaign, access.member.role)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    payload: CampaignUpdateRequest,
    access: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CampaignResponse:
    old_name = access.campaign.name
    access.campaign.name = payload.name.strip()
    record_audit(
        db,
        campaign=access.campaign,
        actor=current_user,
        action="campaign.updated",
        entity_type="campaign",
        before_data={"name": old_name},
        after_data={"name": access.campaign.name},
    )
    await db.commit()
    await db.refresh(access.campaign)
    return campaign_response(access.campaign, access.member.role)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_campaign(
    access: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> None:
    access.campaign.is_archived = True
    record_audit(
        db,
        campaign=access.campaign,
        actor=current_user,
        action="campaign.archived",
        entity_type="campaign",
        before_data={"is_archived": False},
        after_data={"is_archived": True},
    )
    await db.commit()


@router.post(
    "/{campaign_id}/invites",
    response_model=InviteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    payload: InviteCreateRequest,
    access: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> InviteResponse:
    invite, token = create_invite(
        db,
        campaign=access.campaign,
        actor=current_user,
        email=payload.email,
        role=payload.role,
    )
    await db.flush()
    db.add(
        AuditLog(
            campaign_id=access.campaign.id,
            actor_user_id=current_user.id,
            entity_type="invite",
            entity_id=invite.id,
            action="invite.created",
            before_data=None,
            after_data={"email": invite.email, "role": invite.role},
            reason=None,
        )
    )
    await db.commit()
    await db.refresh(invite)
    return InviteResponse(
        id=invite.id,
        campaign_id=invite.campaign_id,
        email=invite.email,
        role=payload.role,
        expires_at=invite.expires_at,
        token=token,
    )


@router.get("/{campaign_id}/members", response_model=CampaignMemberListResponse)
async def list_members(
    access: CampaignMaster,
    db: DatabaseSession,
) -> CampaignMemberListResponse:
    rows = (
        await db.execute(
            select(CampaignMember, User)
            .join(User, User.id == CampaignMember.user_id)
            .where(CampaignMember.campaign_id == access.campaign.id)
            .order_by(CampaignMember.created_at, CampaignMember.id)
        )
    ).all()
    return CampaignMemberListResponse(
        items=[
            CampaignMemberResponse(
                user_id=user.id,
                email=user.email,
                display_name=user.display_name,
                role=member.role,
            )
            for member, user in rows
        ]
    )


@router.patch(
    "/{campaign_id}/members/{member_user_id}", response_model=CampaignMemberResponse
)
async def update_member_role(
    member_user_id: uuid.UUID,
    payload: MemberRoleUpdateRequest,
    access: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CampaignMemberResponse:
    if member_user_id == access.campaign.owner_user_id:
        raise AppError(409, "campaign_owner_protected", "O papel do proprietário é protegido.")
    row = (
        await db.execute(
            select(CampaignMember, User)
            .join(User, User.id == CampaignMember.user_id)
            .where(
                CampaignMember.campaign_id == access.campaign.id,
                CampaignMember.user_id == member_user_id,
            )
        )
    ).one_or_none()
    if row is None:
        raise AppError(404, "campaign_member_not_found", "Participante não encontrado.")
    member, user = row
    old_role = member.role
    member.role = payload.role
    db.add(
        AuditLog(
            campaign_id=access.campaign.id,
            actor_user_id=current_user.id,
            entity_type="campaign_member",
            entity_id=member.id,
            action="campaign_member.role_updated",
            before_data={"role": old_role},
            after_data={"role": member.role},
            reason=None,
        )
    )
    await db.commit()
    return CampaignMemberResponse(
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=member.role,
    )


@router.delete("/{campaign_id}/members/{member_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_user_id: uuid.UUID,
    access: CampaignMaster,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> None:
    if member_user_id == access.campaign.owner_user_id:
        raise AppError(409, "campaign_owner_protected", "O proprietário não pode ser removido.")
    member = await db.scalar(
        select(CampaignMember).where(
            CampaignMember.campaign_id == access.campaign.id,
            CampaignMember.user_id == member_user_id,
        )
    )
    if member is None:
        raise AppError(404, "campaign_member_not_found", "Participante não encontrado.")
    db.add(
        AuditLog(
            campaign_id=access.campaign.id,
            actor_user_id=current_user.id,
            entity_type="campaign_member",
            entity_id=member.id,
            action="campaign_member.removed",
            before_data={"user_id": str(member.user_id), "role": member.role},
            after_data=None,
            reason=None,
        )
    )
    await db.delete(member)
    await db.commit()


@invite_router.post("/{token}/accept", response_model=MembershipResponse)
async def accept_invite(
    token: str,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> MembershipResponse:
    invite = await db.scalar(select(Invite).where(Invite.token_hash == token_digest(token)))
    now = datetime.now(UTC)
    if (
        invite is None
        or invite.accepted_at is not None
        or invite.expires_at <= now
        or invite.email != current_user.email
    ):
        raise AppError(404, "invite_not_found", "Convite inválido ou expirado.")
    campaign = await db.get(Campaign, invite.campaign_id)
    if campaign is None or campaign.is_archived:
        raise AppError(404, "invite_not_found", "Convite inválido ou expirado.")
    existing = await db.scalar(
        select(CampaignMember.id).where(
            CampaignMember.campaign_id == campaign.id,
            CampaignMember.user_id == current_user.id,
        )
    )
    if existing is not None:
        raise AppError(409, "already_campaign_member", "Usuário já participa da campanha.")
    invite.accepted_at = now
    member = CampaignMember(
        campaign_id=campaign.id,
        user_id=current_user.id,
        role=invite.role,
    )
    db.add(member)
    db.add(
        AuditLog(
            campaign_id=campaign.id,
            actor_user_id=current_user.id,
            entity_type="invite",
            entity_id=invite.id,
            action="invite.accepted",
            before_data=None,
            after_data={"role": invite.role},
            reason=None,
        )
    )
    await db.commit()
    await db.refresh(campaign)
    return MembershipResponse(campaign=campaign_response(campaign, invite.role))
