import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AbilityScores(BaseModel):
    strength: int = Field(default=10, ge=1, le=30)
    dexterity: int = Field(default=10, ge=1, le=30)
    constitution: int = Field(default=10, ge=1, le=30)
    intelligence: int = Field(default=10, ge=1, le=30)
    wisdom: int = Field(default=10, ge=1, le=30)
    charisma: int = Field(default=10, ge=1, le=30)


class AbilityScoresUpdate(BaseModel):
    strength: int | None = Field(default=None, ge=1, le=30)
    dexterity: int | None = Field(default=None, ge=1, le=30)
    constitution: int | None = Field(default=None, ge=1, le=30)
    intelligence: int | None = Field(default=None, ge=1, le=30)
    wisdom: int | None = Field(default=None, ge=1, le=30)
    charisma: int | None = Field(default=None, ge=1, le=30)


class CharacterCreateRequest(BaseModel):
    owner_user_id: uuid.UUID | None = None
    name: str = Field(min_length=2, max_length=160)
    race_name: str = Field(default="", max_length=120)
    class_name: str = Field(default="", max_length=120)
    subclass_name: str = Field(default="", max_length=120)
    level: int = Field(default=1, ge=1, le=20)
    background: str = Field(default="", max_length=160)
    alignment: str = Field(default="", max_length=80)
    hit_points_current: int = Field(default=1, ge=0, le=9999)
    hit_points_max: int = Field(default=1, ge=1, le=9999)
    temporary_hit_points: int = Field(default=0, ge=0, le=9999)
    armor_class: int = Field(default=10, ge=0, le=99)
    initiative: int = Field(default=0, ge=-20, le=30)
    speed_meters: int = Field(default=9, ge=0, le=999)
    abilities: AbilityScores = Field(default_factory=AbilityScores)

    @model_validator(mode="after")
    def validate_hit_points(self) -> "CharacterCreateRequest":
        if self.hit_points_current > self.hit_points_max:
            raise ValueError("PV atuais não podem superar os PV máximos.")
        return self


class CharacterUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    race_name: str | None = Field(default=None, max_length=120)
    class_name: str | None = Field(default=None, max_length=120)
    subclass_name: str | None = Field(default=None, max_length=120)
    level: int | None = Field(default=None, ge=1, le=20)
    background: str | None = Field(default=None, max_length=160)
    alignment: str | None = Field(default=None, max_length=80)
    hit_points_current: int | None = Field(default=None, ge=0, le=9999)
    hit_points_max: int | None = Field(default=None, ge=1, le=9999)
    temporary_hit_points: int | None = Field(default=None, ge=0, le=9999)
    armor_class: int | None = Field(default=None, ge=0, le=99)
    initiative: int | None = Field(default=None, ge=-20, le=30)
    speed_meters: int | None = Field(default=None, ge=0, le=999)
    abilities: AbilityScoresUpdate | None = None
    reason: str | None = Field(default=None, max_length=500)


class AbilityResponse(BaseModel):
    code: str
    label: str
    score: int
    modifier: int


class CharacterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    campaign_id: uuid.UUID
    owner_user_id: uuid.UUID
    name: str
    race_name: str
    class_name: str
    subclass_name: str
    level: int
    background: str
    alignment: str
    hit_points_current: int
    hit_points_max: int
    temporary_hit_points: int
    armor_class: int
    initiative: int
    speed_meters: int
    abilities: list[AbilityResponse]
    created_at: datetime
    updated_at: datetime


class CharacterListResponse(BaseModel):
    items: list[CharacterResponse]
    next_cursor: None = None
