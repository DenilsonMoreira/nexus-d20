import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CatalogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    code: str
    name: str
    base_points: int | None = None
    craft_domain: str | None = None
    multiplier: Decimal | None = None


class ItemTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=40)
    craft_domain: str = Field(min_length=1, max_length=40)
    base_damage_die: str = Field(
        default="d6",
        pattern=r"^(1|d4|d6|d8|d10|d12|1d4|1d6|1d8|1d10|1d12)$",
    )
    weight_kg: Decimal = Field(ge=0, max_digits=10, decimal_places=3)
    price_gp: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    material_code: str
    quality_code: str = "standard"
    structure_multiplier: Decimal = Field(default=Decimal("1"), gt=0)
    magic_multiplier: Decimal = Field(default=Decimal("1"), gt=0)
    is_magical: bool = False
    auto_repair_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class ItemTemplateResponse(BaseModel):
    id: uuid.UUID
    version_id: uuid.UUID
    name: str
    category: str
    craft_domain: str
    base_damage_die: str
    weight_kg: Decimal
    price_gp: Decimal
    material_code: str
    quality_code: str
    maximum_durability: int
    is_magical: bool
    auto_repair_percent: Decimal


class ItemCreate(BaseModel):
    template_version_id: uuid.UUID
    name: str | None = Field(default=None, max_length=160)
    quantity: int = Field(default=1, ge=1, le=999)


class ProfessionUpdate(BaseModel):
    domains: list[str] = Field(max_length=20)

    @field_validator("domains")
    @classmethod
    def normalize_domains(cls, value: list[str]) -> list[str]:
        result = [domain.strip().lower() for domain in value if domain.strip()]
        if len(result) != len(set(result)):
            raise ValueError("Não repita a mesma profissão.")
        return result


class DurabilityView(BaseModel):
    state: str
    percentage: Decimal | None
    current_points: int | None
    maximum_points: int | None
    effective_damage_die: str
    break_risk: bool
    usable: bool


class ItemResponse(BaseModel):
    id: uuid.UUID
    character_id: uuid.UUID
    name: str
    category: str
    quantity: int
    weight_kg: Decimal
    price_gp: Decimal
    equipped: bool
    is_active_weapon: bool
    is_magical: bool
    durability: DurabilityView


class ItemStateUpdate(BaseModel):
    equipped: bool | None = None
    is_active_weapon: bool | None = None


class AttackInput(BaseModel):
    natural_roll: int = Field(ge=1, le=20)
    attack_modifier: int = Field(ge=-30, le=50)
    target_ac: int = Field(ge=0, le=99)
    allow_below_magic_floor: bool = False
    reason: str | None = Field(default=None, max_length=500)


class RepairInput(BaseModel):
    points: int = Field(gt=0, le=100000)
    reason: str = Field(min_length=5, max_length=500)


class DurabilityChangeResponse(BaseModel):
    item: ItemResponse
    event_type: Literal["attack", "repair"]
    points: int
    before_points: int
    after_points: int
    attack: dict[str, int | str] | None = None


class DurabilityEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    event_type: str
    points: int
    before_points: int
    after_points: int
    reason: str | None
    created_at: datetime
