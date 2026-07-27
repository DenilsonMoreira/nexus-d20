import uuid
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Material(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "materials"

    code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(80))
    base_points: Mapped[int] = mapped_column(Integer)
    craft_domain: Mapped[str] = mapped_column(String(40))


class QualityLevel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quality_levels"

    code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(80))
    multiplier: Mapped[Decimal] = mapped_column(Numeric(8, 4))


class ItemTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "item_templates"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(40))
    craft_domain: Mapped[str] = mapped_column(String(40))
    base_damage_die: Mapped[str] = mapped_column(String(12), default="d6")
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    price_gp: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class ItemTemplateVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "item_template_versions"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("item_templates.id", ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("materials.id"))
    quality_level_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quality_levels.id")
    )
    structure_multiplier: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=1)
    magic_multiplier: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=1)
    is_magical: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_repair_percent: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0)
    template: Mapped[ItemTemplate] = relationship(lazy="joined")
    material: Mapped[Material] = relationship(lazy="joined")
    quality_level: Mapped[QualityLevel] = relationship(lazy="joined")


class CharacterProfession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "character_professions"

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    domain: Mapped[str] = mapped_column(String(40))


class ItemInstance(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "item_instances"
    __table_args__ = (
        CheckConstraint("quantity >= 1", name="quantity_positive"),
        CheckConstraint(
            "current_durability >= 0 AND current_durability <= maximum_durability",
            name="durability_range",
        ),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    template_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("item_template_versions.id"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(160))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    current_durability: Mapped[int] = mapped_column(Integer)
    maximum_durability: Mapped[int] = mapped_column(Integer)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active_weapon: Mapped[bool] = mapped_column(Boolean, default=False)
    template_version: Mapped[ItemTemplateVersion] = relationship(lazy="joined")


class DurabilityEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "durability_events"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    item_instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("item_instances.id", ondelete="CASCADE"), index=True
    )
    actor_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(30))
    points: Mapped[int] = mapped_column(Integer)
    before_points: Mapped[int] = mapped_column(Integer)
    after_points: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
