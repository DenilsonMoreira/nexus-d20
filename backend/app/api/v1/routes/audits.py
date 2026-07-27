import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.errors import AppError
from app.models import AuditLog, Campaign, CampaignMember, Character, ItemInstance
from app.schemas.audit import AuditResponse, AuditReverseRequest
from app.services.audit import mark_reversed
from app.services.characters import (
    apply_character_snapshot,
    character_snapshot,
    normalize_character_snapshot,
)
from app.services.rest_state import apply_rest_snapshot, load_rest_character, rest_snapshot

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
    if audit.action == "campaign.archived" and audit.entity_id == audit.campaign_id:
        campaign = await db.get(Campaign, audit.campaign_id)
        if campaign is None:
            raise AppError(409, "audit_state_changed", "O estado atual impede a reversão.")
        expected_state = (audit.after_data or {}).get("is_archived")
        if campaign.is_archived != expected_state:
            raise AppError(409, "audit_state_changed", "O estado atual impede a reversão.")
        campaign.is_archived = bool((audit.before_data or {}).get("is_archived", False))
    elif audit.action == "character.updated" and audit.entity_id is not None:
        character = await db.get(Character, audit.entity_id)
        if (
            character is None
            or character.campaign_id != audit.campaign_id
            or audit.before_data is None
            or audit.after_data is None
            or character_snapshot(character)
            != normalize_character_snapshot(audit.after_data)
        ):
            raise AppError(409, "audit_state_changed", "O estado atual impede a reversão.")
        await apply_character_snapshot(db, character, audit.before_data)
    elif audit.action == "item.durability_changed" and audit.entity_id is not None:
        item = await db.get(ItemInstance, audit.entity_id)
        current = {
            "current_durability": item.current_durability if item else None,
            "equipped": item.equipped if item else None,
            "is_active_weapon": item.is_active_weapon if item else None,
        }
        if (
            item is None
            or item.campaign_id != audit.campaign_id
            or audit.before_data is None
            or audit.after_data is None
            or current != audit.after_data
        ):
            raise AppError(409, "audit_state_changed", "O estado atual impede a reversÃ£o.")
        item.current_durability = int(audit.before_data["current_durability"])
        item.equipped = bool(audit.before_data["equipped"])
        item.is_active_weapon = bool(audit.before_data["is_active_weapon"])
    elif audit.action == "long_rest.applied" and audit.entity_id is not None:
        character = await load_rest_character(db, audit.entity_id)
        if (
            character is None
            or character.campaign_id != audit.campaign_id
            or audit.before_data is None
            or audit.after_data is None
            or await rest_snapshot(db, character) != audit.after_data
        ):
            raise AppError(409, "audit_state_changed", "O estado atual impede a reversÃ£o.")
        await apply_rest_snapshot(db, character, audit.before_data)
    else:
        raise AppError(409, "audit_not_reversible", "Esta alteração não pode ser revertida.")
    reversal = mark_reversed(
        db,
        original=audit,
        actor_user_id=current_user.id,
        reason=payload.reason,
    )
    await db.commit()
    await db.refresh(reversal)
    return reversal
