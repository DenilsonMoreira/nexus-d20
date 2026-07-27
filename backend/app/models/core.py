import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    auth_version: Mapped[int] = mapped_column(default=1)


class Session(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PasswordResetToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "password_reset_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Campaign(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(160))
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    ruleset_code: Mapped[str] = mapped_column(String(40), default="dnd5e-2014")
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)


class CampaignMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "campaign_members"
    __table_args__ = (UniqueConstraint("campaign_id", "user_id"),)

    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(String(30))


class Character(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "characters"
    __table_args__ = (
        CheckConstraint("level BETWEEN 1 AND 20", name="level_range"),
        CheckConstraint(
            "hit_points_current >= 0 AND hit_points_current <= hit_points_max",
            name="hit_points_range",
        ),
        CheckConstraint("hit_points_max >= 1", name="hit_points_max_positive"),
        CheckConstraint("temporary_hit_points >= 0", name="temporary_hit_points_positive"),
        CheckConstraint("armor_class BETWEEN 0 AND 99", name="armor_class_range"),
        CheckConstraint("initiative BETWEEN -20 AND 30", name="initiative_range"),
        CheckConstraint("speed_meters BETWEEN 0 AND 999", name="speed_meters_range"),
        CheckConstraint(
            "strength BETWEEN 1 AND 30 AND dexterity BETWEEN 1 AND 30 "
            "AND constitution BETWEEN 1 AND 30 AND intelligence BETWEEN 1 AND 30 "
            "AND wisdom BETWEEN 1 AND 30 AND charisma BETWEEN 1 AND 30",
            name="ability_scores_range",
        ),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), index=True
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    race_name: Mapped[str] = mapped_column(String(120), default="")
    class_name: Mapped[str] = mapped_column(String(120), default="")
    subclass_name: Mapped[str] = mapped_column(String(120), default="")
    level: Mapped[int] = mapped_column(Integer, default=1)
    background: Mapped[str] = mapped_column(String(160), default="")
    alignment: Mapped[str] = mapped_column(String(80), default="")
    hit_points_current: Mapped[int] = mapped_column(Integer, default=1)
    hit_points_max: Mapped[int] = mapped_column(Integer, default=1)
    temporary_hit_points: Mapped[int] = mapped_column(Integer, default=0)
    armor_class: Mapped[int] = mapped_column(Integer, default=10)
    initiative: Mapped[int] = mapped_column(Integer, default=0)
    speed_meters: Mapped[int] = mapped_column(Integer, default=9)
    strength: Mapped[int] = mapped_column(Integer, default=10)
    dexterity: Mapped[int] = mapped_column(Integer, default=10)
    constitution: Mapped[int] = mapped_column(Integer, default=10)
    intelligence: Mapped[int] = mapped_column(Integer, default=10)
    wisdom: Mapped[int] = mapped_column(Integer, default=10)
    charisma: Mapped[int] = mapped_column(Integer, default=10)
    is_active_group: Mapped[bool] = mapped_column(Boolean, default=False)
    hit_dice_current: Mapped[int] = mapped_column(Integer, default=1)
    hit_dice_max: Mapped[int] = mapped_column(Integer, default=1)
    exhaustion_level: Mapped[int] = mapped_column(Integer, default=0)
    hidden_fatigue: Mapped[int] = mapped_column(Integer, default=0)
    proficiencies: Mapped[list["CharacterProficiency"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CharacterProficiency.category, CharacterProficiency.name",
    )
    resources: Mapped[list["CharacterResource"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CharacterResource.name",
    )
    spell_slots: Mapped[list["CharacterSpellSlot"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CharacterSpellSlot.level",
    )
    conditions: Mapped[list["CharacterCondition"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CharacterCondition.name",
    )


class CharacterProficiency(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "character_proficiencies"
    __table_args__ = (
        UniqueConstraint("character_id", "category", "name"),
        CheckConstraint(
            "category IN ('saving_throw', 'skill', 'language', 'tool', "
            "'weapon', 'armor', 'other')",
            name="category_allowed",
        ),
    )

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(160))
    character: Mapped[Character] = relationship(back_populates="proficiencies")


class CharacterResource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "character_resources"
    __table_args__ = (
        UniqueConstraint("character_id", "name"),
        CheckConstraint(
            "current_value >= 0 AND current_value <= maximum_value",
            name="current_value_range",
        ),
        CheckConstraint("maximum_value >= 1", name="maximum_value_positive"),
        CheckConstraint(
            "recovery IN ('short_rest', 'long_rest', 'manual')",
            name="recovery_allowed",
        ),
    )

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    current_value: Mapped[int] = mapped_column(Integer)
    maximum_value: Mapped[int] = mapped_column(Integer)
    recovery: Mapped[str] = mapped_column(String(30))
    character: Mapped[Character] = relationship(back_populates="resources")


class CharacterSpellSlot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "character_spell_slots"
    __table_args__ = (
        UniqueConstraint("character_id", "level"),
        CheckConstraint("level BETWEEN 1 AND 9", name="level_range"),
        CheckConstraint(
            "current_value >= 0 AND current_value <= maximum_value",
            name="current_value_range",
        ),
    )

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    level: Mapped[int] = mapped_column(Integer)
    current_value: Mapped[int] = mapped_column(Integer)
    maximum_value: Mapped[int] = mapped_column(Integer)
    character: Mapped[Character] = relationship(back_populates="spell_slots")


class CharacterCondition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "character_conditions"

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    expires_on_long_rest: Mapped[bool] = mapped_column(Boolean, default=False)
    character: Mapped[Character] = relationship(back_populates="conditions")


class LongRestEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "long_rest_events"
    __table_args__ = (UniqueConstraint("campaign_id", "idempotency_key"),)

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    idempotency_key: Mapped[str] = mapped_column(String(120))
    request_hash: Mapped[str] = mapped_column(String(64))
    result_data: Mapped[dict[str, Any]] = mapped_column(JSON)


class Invite(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "invites"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), index=True
    )
    invited_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    email: Mapped[str] = mapped_column(String(320), index=True)
    role: Mapped[str] = mapped_column(String(30))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Note(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notes"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), index=True
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="")
    visibility: Mapped[str] = mapped_column(String(30), default="private")


class NoteLink(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "note_links"
    __table_args__ = (UniqueConstraint("note_id", "entity_type", "entity_id"),)

    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), index=True
    )
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))


class MediaAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "media_assets"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), index=True
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    object_key: Mapped[str] = mapped_column(String(500), unique=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"))
    actor_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    before_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    after_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_reversible: Mapped[bool] = mapped_column(Boolean, default=False)
    reversed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reversed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reversal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reversal_of_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audit_logs.id"), nullable=True, index=True
    )
