import uuid

from pydantic import BaseModel, Field, model_validator


class MasterStateUpdate(BaseModel):
    is_active_group: bool | None = None
    hit_dice_current: int | None = Field(default=None, ge=0, le=20)
    hit_dice_max: int | None = Field(default=None, ge=1, le=20)
    exhaustion_level: int | None = Field(default=None, ge=0, le=6)
    hidden_fatigue: int | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def validate_hit_dice(self) -> "MasterStateUpdate":
        if (
            self.hit_dice_current is not None
            and self.hit_dice_max is not None
            and self.hit_dice_current > self.hit_dice_max
        ):
            raise ValueError("Dados de vida atuais não podem superar o máximo.")
        return self


class SpellSlotInput(BaseModel):
    level: int = Field(ge=1, le=9)
    current_value: int = Field(ge=0, le=99)
    maximum_value: int = Field(ge=0, le=99)

    @model_validator(mode="after")
    def validate_current(self) -> "SpellSlotInput":
        if self.current_value > self.maximum_value:
            raise ValueError("Espaços atuais não podem superar o máximo.")
        return self


class ConditionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    expires_on_long_rest: bool = False


class LongRestRequest(BaseModel):
    has_sufficient_food: bool = True
    has_sufficient_water: bool = True
    rest_completed: bool = True
    antimagic_zone: bool = False


class LongRestResponse(BaseModel):
    character_id: uuid.UUID
    applied: bool
    idempotent_replay: bool = False
    result: dict[str, object]
    expired_conditions: list[str]
