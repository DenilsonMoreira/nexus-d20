import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CampaignRole = Literal["master", "player", "observer"]
InviteRole = Literal["player", "observer"]


class CampaignCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)


class CampaignUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    ruleset_code: str
    role: CampaignRole
    created_at: datetime


class CampaignListResponse(BaseModel):
    items: list[CampaignResponse]
    next_cursor: None = None


class InviteCreateRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: InviteRole

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("E-mail inválido.")
        return normalized


class InviteResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    email: str
    role: InviteRole
    expires_at: datetime
    token: str


class MembershipResponse(BaseModel):
    campaign: CampaignResponse


class MemberRoleUpdateRequest(BaseModel):
    role: InviteRole


class CampaignMemberResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    display_name: str
    role: CampaignRole


class CampaignMemberListResponse(BaseModel):
    items: list[CampaignMemberResponse]
    next_cursor: None = None
