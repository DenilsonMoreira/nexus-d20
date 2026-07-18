from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class AttackRequest(BaseModel):
    natural_roll: int = Field(ge=1, le=20)
    attack_modifier: int
    target_ac: int = Field(ge=0)


class AttackResponse(BaseModel):
    natural_roll: int
    attack_modifier: int
    total: int
    target_ac: int
    margin: int
    outcome: Literal["critical_miss", "miss", "hit", "critical_hit"]
    attacker_weapon_wear: int
    suggested_target_equipment_wear: int


class DurabilityPreviewRequest(BaseModel):
    current_points: int = Field(ge=0)
    maximum_points: int = Field(gt=0)
    base_damage_die: str = "d8"


class DurabilitySnapshotResponse(BaseModel):
    current_points: int
    maximum_points: int
    percentage: Decimal
    state: Literal["Ótimo", "Bom", "Regular", "Ruim", "Inutilizável"]
    effective_damage_die: str
    break_risk: bool
    usable: bool


class EncumbranceRequest(BaseModel):
    strength: int = Field(gt=0)
    current_weight_kg: Decimal = Field(ge=0)
    base_speed_m: Decimal = Field(ge=0)


class EncumbranceResponse(BaseModel):
    strength: int
    current_weight_kg: Decimal
    comfortable_limit_kg: Decimal
    heavily_encumbered_limit_kg: Decimal
    maximum_capacity_kg: Decimal
    push_drag_lift_kg: Decimal
    state: Literal["comfortable", "encumbered", "heavily_encumbered", "over_capacity"]
    speed_penalty_m: Decimal
    current_speed_m: Decimal


class MagicItemRestInput(BaseModel):
    name: str
    current_points: int = Field(ge=0)
    maximum_points: int = Field(gt=0)
    auto_repair_percent: Decimal = Field(ge=0)


class LongRestRequest(BaseModel):
    hit_points_current: int = Field(ge=0)
    hit_points_maximum: int = Field(gt=0)
    spell_slots_current: dict[str, int] = Field(default_factory=dict)
    spell_slots_maximum: dict[str, int] = Field(default_factory=dict)
    resources_current: dict[str, int] = Field(default_factory=dict)
    resources_maximum: dict[str, int] = Field(default_factory=dict)
    long_rest_resource_keys: list[str] = Field(default_factory=list)
    hit_dice_current: int = Field(default=0, ge=0)
    hit_dice_maximum: int = Field(default=0, ge=0)
    exhaustion_level: int = Field(default=0, ge=0, le=6)
    hidden_fatigue: int = Field(default=0, ge=0)
    has_sufficient_food: bool = True
    has_sufficient_water: bool = True
    rest_completed: bool = True
    antimagic_zone: bool = False
    magic_items: list[MagicItemRestInput] = Field(default_factory=list)


class LongRestResponse(BaseModel):
    hit_points_before: int
    hit_points_after: int
    spell_slots_before: dict[str, int]
    spell_slots_after: dict[str, int]
    resources_before: dict[str, int]
    resources_after: dict[str, int]
    hit_dice_before: int
    hit_dice_after: int
    exhaustion_before: int
    exhaustion_after: int
    hidden_fatigue_before: int
    hidden_fatigue_after: int
    magic_items: list[dict[str, object]]
    warnings: list[str]
