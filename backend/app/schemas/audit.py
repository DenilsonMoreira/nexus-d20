import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    campaign_id: uuid.UUID
    actor_user_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID | None
    action: str
    before_data: dict[str, object] | None
    after_data: dict[str, object] | None
    reason: str | None
    is_reversible: bool
    reversed_at: datetime | None
    reversed_by_user_id: uuid.UUID | None
    reversal_reason: str | None
    reversal_of_id: uuid.UUID | None
    created_at: datetime


class AuditListResponse(BaseModel):
    items: list[AuditResponse]
    next_cursor: None = None


class AuditReverseRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=500)
