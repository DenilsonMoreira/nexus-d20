import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.errors import AppError
from app.models import AuditLog, Campaign, CampaignMember
from app.schemas.audit import AuditResponse, AuditReverseRequest
from app.services.audit import mark_reversed

router = APIRouter()


@router.post("/{audit_id}/reverse", response_model=AuditResponse)
async def reverse_audit(
    audit_id: uuid.UUID,
    payload: AuditReverseRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> AuditLog:
    audit = await db.get(AuditLog, audit_id)
    if audit is None:
        raise AppError(404, "audit_not_found", "Registro de auditoria não encontrado.")
    member = await db.scalar(
        select(CampaignMember).where(
            CampaignMember.campaign_id == audit.campaign_id,
            CampaignMember.user_id == current_user.id,
        )
    )
    if member is None:
        raise AppError(404, "audit_not_found", "Registro de auditoria não encontrado.")
    if member.role != "master":
        raise AppError(403, "master_role_required", "Apenas o mestre pode realizar esta ação.")
    if audit.reversed_at is not None:
        raise AppError(409, "audit_already_reversed", "Esta alteração já foi revertida.")
    if not audit.is_reversible:
        raise AppError(409, "audit_not_reversible", "Esta alteração não pode ser revertida.")
    if audit.action != "campaign.archived" or audit.entity_id != audit.campaign_id:
        raise AppError(409, "audit_not_reversible", "Esta alteração não pode ser revertida.")
    campaign = await db.get(Campaign, audit.campaign_id)
    if campaign is None:
        raise AppError(409, "audit_state_changed", "O estado atual impede a reversão.")
    expected_state = (audit.after_data or {}).get("is_archived")
    if campaign.is_archived != expected_state:
        raise AppError(409, "audit_state_changed", "O estado atual impede a reversão.")
    campaign.is_archived = bool((audit.before_data or {}).get("is_archived", False))
    reversal = mark_reversed(
        db,
        original=audit,
        actor_user_id=current_user.id,
        reason=payload.reason,
    )
    await db.commit()
    await db.refresh(reversal)
    return reversal
