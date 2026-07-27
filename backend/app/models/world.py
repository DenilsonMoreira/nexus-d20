import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LibraryEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "library_entries"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('item', 'spell', 'condition', 'service')",
            name="kind_allowed",
        ),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    source_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("library_entries.id"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)
    is_identified: Mapped[bool] = mapped_column(Boolean, default=True)


class Shop(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shops"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    owner_name: Mapped[str] = mapped_column(String(160), default="")
    region: Mapped[str] = mapped_column(String(120), default="")
    opening_hours: Mapped[str] = mapped_column(String(160), default="")
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)


class ShopStock(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shop_stock"
    __table_args__ = (
        UniqueConstraint("shop_id", "library_entry_id"),
        CheckConstraint("quantity >= 0", name="quantity_nonnegative"),
        CheckConstraint("price_gp >= 0", name="price_nonnegative"),
    )

    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), index=True
    )
    library_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("library_entries.id"), index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    price_gp: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)


class Creature(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "creatures"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    source_creature_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("creatures.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(160))
    armor_class: Mapped[int] = mapped_column(Integer, default=10)
    hit_points: Mapped[int] = mapped_column(Integer, default=1)
    challenge_rating: Mapped[Decimal] = mapped_column(Numeric(8, 3), default=0)
    encounter_weight: Mapped[int] = mapped_column(Integer, default=1)
    biomes: Mapped[list[str]] = mapped_column(JSON, default=list)
    equipment: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    treasure: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)


class Encounter(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "encounters"
    __table_args__ = (
        CheckConstraint("danger BETWEEN 1 AND 5", name="danger_range"),
        CheckConstraint(
            "status IN ('planned', 'active', 'completed')",
            name="status_allowed",
        ),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    biome: Mapped[str] = mapped_column(String(100))
    weather: Mapped[str] = mapped_column(String(100), default="")
    time_of_day: Mapped[str] = mapped_column(String(40), default="")
    danger: Mapped[int] = mapped_column(Integer)
    estimated_difficulty: Mapped[str] = mapped_column(String(30))
    difficulty_is_estimate: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(30), default="planned")
    seed: Mapped[int] = mapped_column(Integer)
    creatures: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    history: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)


class TravelPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "travel_plans"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    origin: Mapped[str] = mapped_column(String(160))
    destination: Mapped[str] = mapped_column(String(160))
    distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    pace: Mapped[str] = mapped_column(String(30))
    difficult_terrain: Mapped[bool] = mapped_column(Boolean, default=False)
    severe_weather: Mapped[bool] = mapped_column(Boolean, default=False)
    hidden_fatigue_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    traveler_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    result: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class KnowledgeNode(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_nodes"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    node_type: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class KnowledgeEdge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_edges"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), index=True
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), index=True
    )
    relation_type: Mapped[str] = mapped_column(String(80))
    directed: Mapped[bool] = mapped_column(Boolean, default=True)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[int] = mapped_column(Integer, default=100)


class DashboardLayout(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dashboard_layouts"
    __table_args__ = (
        CheckConstraint(
            "visibility IN ('private', 'shared', 'presentation')",
            name="visibility_allowed",
        ),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    template_code: Mapped[str] = mapped_column(String(40), default="custom")
    visibility: Mapped[str] = mapped_column(String(30), default="private")
    cards: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
