import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.rules.ability_score_progression import AbilityName
from app.domain.rules.class_progression import ClassId, HitPointMethod
from app.domain.rules.subclass_progression import SubclassId


class SpellChoice(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    spell_level: int = Field(ge=0, le=9)
    is_known: bool = False
    is_prepared: bool = False
    in_spellbook: bool = False
    source_class_id: ClassId

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()


class LevelUpRequest(BaseModel):
    target_class_id: ClassId
    base_class_id: ClassId | None = None
    experience_points: int | None = Field(default=None, ge=0)
    hit_point_method: HitPointMethod | None = None
    hit_die_roll: int | None = None
    selected_subclass_id: SubclassId | None = None
    ability_increases: dict[AbilityName, Literal[1, 2]] | None = None
    spells: list[SpellChoice] | None = Field(default=None, max_length=200)
    reason: str | None = Field(default=None, max_length=500)


class ClassLevelResponse(BaseModel):
    class_id: ClassId
    level: int
    subclass_id: str | None


class SpellcastingProfileResponse(BaseModel):
    mode: Literal["none", "known", "prepared", "spellbook", "pact"]
    ability: Literal["intelligence", "wisdom", "charisma"] | None
    cantrips_known: int
    spells_known: int | None
    prepared_limit: int | None
    spellbook_minimum: int | None
    slots: dict[int, int]
    pact_slot_level: int | None


class LevelUpSimulationResponse(BaseModel):
    character_id: uuid.UUID
    current_level: int
    resulting_level: int
    target_class_id: ClassId
    target_class_level: int
    hit_point_gain: int | None
    hit_points_max_after: int | None
    proficiency_bonus_after: int
    class_levels_after: list[ClassLevelResponse]
    spellcasting: SpellcastingProfileResponse
    multiclass_allowed: bool
    unmet_multiclass_requirements: list[str]
    required_choices: list[str]
    warnings: list[str]
    ready_to_apply: bool


class LevelUpResultResponse(LevelUpSimulationResponse):
    event_id: uuid.UUID
    applied_at: datetime


class ProgressionStateResponse(BaseModel):
    character_id: uuid.UUID
    total_level: int
    class_levels: list[ClassLevelResponse]
    spells: list[SpellChoice]
    spell_slots: dict[int, int]
