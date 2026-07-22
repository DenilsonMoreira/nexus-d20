import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import AuditLog


def record_audit(
    db: AsyncSession,
    *,
    campaign_id: uuid.UUID,
    actor_user_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID | None,
    action: str,
    before_data: dict[str, object] | None = None,
    after_data: dict[str, object] | None = None,
    reason: str | None = None,
    is_reversible: bool = False,
    reversal_of_id: uuid.UUID | None = None,
) -> AuditLog:
    audit = AuditLog(
        campaign_id=campaign_id,
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        before_data=before_data,
        after_data=after_data,
        reason=reason,
        is_reversible=is_reversible,
        reversal_of_id=reversal_of_id,
    )
    db.add(audit)
    return audit


def mark_reversed(
    db: AsyncSession,
    *,
    original: AuditLog,
    actor_user_id: uuid.UUID,
    reason: str,
) -> AuditLog:
    normalized_reason = reason.strip()
    if not original.is_reversible:
        raise AppError(409, "audit_not_reversible", "Esta alteração não pode ser revertida.")
    if original.reversed_at is not None:
        raise AppError(409, "audit_already_reversed", "Esta alteração já foi revertida.")
    if len(normalized_reason) < 5:
        raise AppError(422, "reversal_reason_required", "Informe o motivo da reversão.")
    original.reversed_at = datetime.now(UTC)
    original.reversed_by_user_id = actor_user_id
    original.reversal_reason = normalized_reason
    return record_audit(
        db,
        campaign_id=original.campaign_id,
        actor_user_id=actor_user_id,
        entity_type=original.entity_type,
        entity_id=original.entity_id,
        action=f"{original.action}.reversed",
        before_data=original.after_data,
        after_data=original.before_data,
        reason=normalized_reason,
        reversal_of_id=original.id,
    )
