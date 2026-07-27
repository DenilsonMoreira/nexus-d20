from decimal import Decimal
from typing import Literal, cast

from pydantic import BaseModel, Field, model_validator

from app.domain.rules.ability_score_progression import (
    AbilityName,
    AbilityScoreMap,
    validate_ability_score_improvement,
)
from app.domain.rules.class_progression import (
    ClassId,
    HitPointMethod,
    RequiredChoice,
    validate_hit_point_choice,
)
from app.domain.rules.subclass_progression import (
    SubclassId,
    validate_subclass_selection,
)


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


class ProgressionSimulationRequest(BaseModel):
    current_level: int = Field(ge=1, le=20)
    experience_points: int | None = Field(default=None, ge=0)


class ProgressionSnapshotResponse(BaseModel):
    level: int
    experience_threshold: int
    proficiency_bonus: int


class ProgressionSimulationResponse(BaseModel):
    current: ProgressionSnapshotResponse
    next: ProgressionSnapshotResponse | None
    experience_points: int | None
    highest_level_by_experience: int | None
    experience_remaining: int | None
    qualification: Literal[
        "eligible",
        "insufficient_experience",
        "not_evaluated",
        "level_cap",
    ]


class ClassProgressionSimulationRequest(BaseModel):
    class_id: ClassId
    current_class_level: int = Field(ge=1, le=20)
    constitution_modifier: int = Field(ge=-10, le=10)
    hit_point_method: HitPointMethod | None = None
    hit_die_roll: int | None = None

    def model_post_init(self, __context: object) -> None:
        validate_hit_point_choice(
            class_id=self.class_id,
            hit_point_method=self.hit_point_method,
            hit_die_roll=self.hit_die_roll,
        )


class ClassProgressionSimulationResponse(BaseModel):
    class_id: ClassId
    class_label: str
    current_class_level: int
    next_class_level: int | None
    hit_die_sides: int
    fixed_hit_point_value: int
    hit_point_method: HitPointMethod | None
    hit_die_roll: int | None
    constitution_modifier: int
    hit_point_gain: int | None
    ability_score_improvement_required: bool
    required_choices: list[RequiredChoice]
    class_level_cap: bool


class AbilityScoreValues(BaseModel):
    strength: int = Field(ge=1, le=30)
    dexterity: int = Field(ge=1, le=30)
    constitution: int = Field(ge=1, le=30)
    intelligence: int = Field(ge=1, le=30)
    wisdom: int = Field(ge=1, le=30)
    charisma: int = Field(ge=1, le=30)


class AbilityModifierValues(BaseModel):
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


class AbilityScoreImprovementSimulationRequest(BaseModel):
    current_scores: AbilityScoreValues
    increases: dict[AbilityName, Literal[1, 2]]
    resulting_character_level: int = Field(ge=1, le=20)

    @model_validator(mode="after")
    def validate_increases(self) -> "AbilityScoreImprovementSimulationRequest":
        validate_ability_score_improvement(
            current_scores=cast(
                AbilityScoreMap,
                self.current_scores.model_dump(),
            ),
            increases=cast(dict[AbilityName, int], self.increases),
        )
        return self


class AbilityScoreImprovementSimulationResponse(BaseModel):
    resulting_character_level: int
    before: AbilityScoreValues
    after: AbilityScoreValues
    increases: dict[AbilityName, int]
    modifiers_before: AbilityModifierValues
    modifiers_after: AbilityModifierValues
    constitution_modifier_change: int
    hit_point_maximum_adjustment: int


class SubclassProgressionSimulationRequest(BaseModel):
    class_id: ClassId
    target_class_level: int = Field(ge=1, le=20)
    selected_subclass_id: SubclassId | None = None

    def model_post_init(self, __context: object) -> None:
        validate_subclass_selection(
            class_id=self.class_id,
            target_class_level=self.target_class_level,
            selected_subclass_id=self.selected_subclass_id,
        )


class SubclassOptionResponse(BaseModel):
    id: SubclassId
    label: str
    source: Literal["srd_5_1"]


class SubclassProgressionSimulationResponse(BaseModel):
    class_id: ClassId
    class_label: str
    target_class_level: int
    choice_level: int
    choice_available: bool
    selection_required: bool
    selected_subclass_id: SubclassId | None
    selected_subclass_label: str | None
    available_subclasses: list[SubclassOptionResponse]
