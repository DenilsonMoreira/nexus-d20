import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class LibraryEntryCreate(BaseModel):
    kind: Literal["item", "spell", "condition", "service"]
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=10_000)
    data: dict[str, Any] = Field(default_factory=dict)
    is_secret: bool = False
    is_identified: bool = True


class LibraryEntryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=10_000)
    data: dict[str, Any] | None = None
    is_secret: bool | None = None
    is_identified: bool | None = None


class ShopCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    owner_name: str = Field(default="", max_length=160)
    region: str = Field(default="", max_length=120)
    opening_hours: str = Field(default="", max_length=160)
    is_secret: bool = False


class StockUpdate(BaseModel):
    library_entry_id: uuid.UUID
    quantity: int = Field(ge=0, le=1_000_000)
    price_gp: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    is_hidden: bool = False


class CreatureCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    armor_class: int = Field(default=10, ge=0, le=99)
    hit_points: int = Field(default=1, ge=1, le=1_000_000)
    challenge_rating: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    encounter_weight: int = Field(default=1, ge=1, le=1000)
    biomes: list[str] = Field(default_factory=list, max_length=30)
    equipment: list[dict[str, Any]] = Field(default_factory=list)
    treasure: list[dict[str, Any]] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    is_secret: bool = False


class CreatureUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    armor_class: int | None = Field(default=None, ge=0, le=99)
    hit_points: int | None = Field(default=None, ge=1, le=1_000_000)
    challenge_rating: Decimal | None = Field(default=None, ge=0, le=100)
    encounter_weight: int | None = Field(default=None, ge=1, le=1000)
    biomes: list[str] | None = Field(default=None, max_length=30)
    equipment: list[dict[str, Any]] | None = None
    treasure: list[dict[str, Any]] | None = None
    data: dict[str, Any] | None = None
    is_secret: bool | None = None


class EncounterGenerate(BaseModel):
    biome: str = Field(min_length=1, max_length=100)
    weather: str = Field(default="", max_length=100)
    time_of_day: str = Field(default="", max_length=40)
    danger: int = Field(ge=1, le=5)
    seed: int = Field(default=1, ge=0, le=2_147_483_647)
    maximum_creatures: int = Field(default=6, ge=1, le=20)


class EncounterAdjust(BaseModel):
    estimated_difficulty: Literal["easy", "moderate", "hard", "deadly"] | None = None
    status: Literal["planned", "active", "completed"] | None = None
    creatures: list[dict[str, Any]] | None = None
    history_entry: dict[str, Any] | None = None


class TravelPlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    origin: str = Field(min_length=1, max_length=160)
    destination: str = Field(min_length=1, max_length=160)
    distance_km: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    pace: Literal["slow", "normal", "fast"] = "normal"
    difficult_terrain: bool = False
    severe_weather: bool = False
    hidden_fatigue_enabled: bool = False
    traveler_ids: list[uuid.UUID] = Field(min_length=1, max_length=30)
    travel_hours_per_day: int = Field(default=8, ge=1, le=16)


class KnowledgeNodeCreate(BaseModel):
    node_type: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(default="", max_length=10_000)
    data: dict[str, Any] = Field(default_factory=dict)
    is_secret: bool = False
    occurred_at: datetime | None = None


class KnowledgeEdgeCreate(BaseModel):
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    relation_type: str = Field(min_length=1, max_length=80)
    directed: bool = True
    is_secret: bool = False
    confidence: int = Field(default=100, ge=0, le=100)

    @model_validator(mode="after")
    def distinct_nodes(self) -> "KnowledgeEdgeCreate":
        if self.source_node_id == self.target_node_id:
            raise ValueError("Uma conexão deve ligar nós diferentes.")
        return self


class DashboardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    template_code: Literal[
        "custom", "combat", "city", "shop", "exploration", "rest"
    ] = "custom"
    visibility: Literal["private", "shared", "presentation"] = "private"
    cards: list[dict[str, Any]] = Field(default_factory=list, max_length=50)
