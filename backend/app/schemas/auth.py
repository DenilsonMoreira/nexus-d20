import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_email_value(value: str) -> str:
    normalized = value.strip().lower()
    if any(character.isspace() for character in normalized) or normalized.count("@") != 1:
        raise ValueError("E-mail inválido.")
    local_part, domain = normalized.split("@")
    if not local_part or not domain:
        raise ValueError("E-mail inválido.")
    return normalized


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    display_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return normalize_email_value(value)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return normalize_email_value(value)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    display_name: str
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserResponse
    access_expires_in_seconds: int


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return normalize_email_value(value)


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    new_password: str = Field(min_length=12, max_length=128)


class MessageResponse(BaseModel):
    message: str
