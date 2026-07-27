import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NoteLinkInput(BaseModel):
    entity_type: Literal["character", "location", "item", "npc", "session", "event"]
    entity_id: uuid.UUID


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(default="", max_length=100000)
    visibility: Literal["private", "shared"] = "private"
    links: list[NoteLinkInput] = Field(default_factory=list, max_length=100)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return value.strip()


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, max_length=100000)
    visibility: Literal["private", "shared"] | None = None
    links: list[NoteLinkInput] | None = Field(default=None, max_length=100)


class NoteLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    entity_type: str
    entity_id: uuid.UUID


class MediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime


class NoteResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    owner_user_id: uuid.UUID
    title: str
    body: str
    visibility: str
    links: list[NoteLinkResponse]
    media: list[MediaResponse]
    created_at: datetime
    updated_at: datetime


class MediaUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: Literal["image/jpeg", "image/png", "image/webp", "image/gif"]
    size_bytes: int = Field(gt=0)


class MediaUploadResponse(MediaResponse):
    upload_url: str
    upload_headers: dict[str, str]


class MediaDownloadResponse(BaseModel):
    download_url: str
    expires_in_seconds: int
