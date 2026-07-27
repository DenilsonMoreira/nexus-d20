import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Character,
    CharacterCondition,
    CharacterResource,
    CharacterSpellSlot,
    ItemInstance,
    ItemTemplateVersion,
)


async def load_rest_character(
    db: AsyncSession, character_id: uuid.UUID
) -> Character | None:
    character: Character | None = await db.scalar(
        select(Character)
        .options(
            selectinload(Character.resources),
            selectinload(Character.spell_slots),
            selectinload(Character.conditions),
        )
        .where(Character.id == character_id)
    )
    return character


async def rest_payload(
    db: AsyncSession, character: Character, requirements: dict[str, bool]
) -> dict[str, Any]:
    magic_items = (
        await db.scalars(
            select(ItemInstance)
            .join(ItemTemplateVersion)
            .where(
                ItemInstance.character_id == character.id,
                ItemTemplateVersion.is_magical.is_(True),
            )
        )
    ).all()
    return {
        "hit_points_current": character.hit_points_current,
        "hit_points_maximum": character.hit_points_max,
        "spell_slots_current": {
            str(slot.level): slot.current_value for slot in character.spell_slots
        },
        "spell_slots_maximum": {
            str(slot.level): slot.maximum_value for slot in character.spell_slots
        },
        "resources_current": {
            str(resource.id): resource.current_value for resource in character.resources
        },
        "resources_maximum": {
            str(resource.id): resource.maximum_value for resource in character.resources
        },
        "long_rest_resource_keys": [
            str(resource.id)
            for resource in character.resources
            if resource.recovery == "long_rest"
        ],
        "hit_dice_current": character.hit_dice_current,
        "hit_dice_maximum": character.hit_dice_max,
        "exhaustion_level": character.exhaustion_level,
        "hidden_fatigue": character.hidden_fatigue,
        "magic_items": [
            {
                "id": str(item.id),
                "current_points": item.current_durability,
                "maximum_points": item.maximum_durability,
                "auto_repair_percent": str(
                    item.template_version.auto_repair_percent
                ),
            }
            for item in magic_items
        ],
        **requirements,
    }


async def rest_snapshot(db: AsyncSession, character: Character) -> dict[str, Any]:
    items = (
        await db.scalars(
            select(ItemInstance).where(ItemInstance.character_id == character.id)
        )
    ).all()
    conditions = (
        await db.scalars(
            select(CharacterCondition).where(
                CharacterCondition.character_id == character.id
            )
        )
    ).all()
    return {
        "character": {
            "hit_points_current": character.hit_points_current,
            "hit_dice_current": character.hit_dice_current,
            "exhaustion_level": character.exhaustion_level,
            "hidden_fatigue": character.hidden_fatigue,
        },
        "resources": {
            str(resource.id): resource.current_value for resource in character.resources
        },
        "spell_slots": {
            str(slot.id): slot.current_value for slot in character.spell_slots
        },
        "items": {str(item.id): item.current_durability for item in items},
        "conditions": [
            {
                "id": str(condition.id),
                "name": condition.name,
                "description": condition.description,
                "expires_on_long_rest": condition.expires_on_long_rest,
            }
            for condition in conditions
        ],
    }


async def apply_rest_result(
    db: AsyncSession, character: Character, result: dict[str, Any]
) -> list[str]:
    character.hit_points_current = int(result["hit_points_after"])
    character.hit_dice_current = int(result["hit_dice_after"])
    character.exhaustion_level = int(result["exhaustion_after"])
    character.hidden_fatigue = int(result["hidden_fatigue_after"])
    for resource in character.resources:
        resource.current_value = int(result["resources_after"][str(resource.id)])
    for slot in character.spell_slots:
        slot.current_value = int(result["spell_slots_after"][str(slot.level)])
    for item_data in result["magic_items"]:
        item = await db.get(ItemInstance, uuid.UUID(item_data["id"]))
        if item is not None:
            item.current_durability = int(item_data["current_points_after"])
    expired = [
        condition for condition in character.conditions if condition.expires_on_long_rest
    ]
    names = [condition.name for condition in expired]
    if expired:
        await db.execute(
            delete(CharacterCondition).where(
                CharacterCondition.id.in_([condition.id for condition in expired])
            )
        )
    return names


async def apply_rest_snapshot(
    db: AsyncSession, character: Character, snapshot: dict[str, Any]
) -> None:
    for key, value in snapshot["character"].items():
        setattr(character, key, int(value))
    for resource_id, value in snapshot["resources"].items():
        resource = await db.get(CharacterResource, uuid.UUID(resource_id))
        if resource is not None:
            resource.current_value = int(value)
    for slot_id, value in snapshot["spell_slots"].items():
        slot = await db.get(CharacterSpellSlot, uuid.UUID(slot_id))
        if slot is not None:
            slot.current_value = int(value)
    for item_id, value in snapshot["items"].items():
        item = await db.get(ItemInstance, uuid.UUID(item_id))
        if item is not None:
            item.current_durability = int(value)
    existing_ids = set(
        (
            await db.scalars(
                select(CharacterCondition.id).where(
                    CharacterCondition.character_id == character.id
                )
            )
        ).all()
    )
    for data in snapshot["conditions"]:
        condition_id = uuid.UUID(data["id"])
        if condition_id not in existing_ids:
            db.add(
                CharacterCondition(
                    id=condition_id,
                    character_id=character.id,
                    name=data["name"],
                    description=data["description"],
                    expires_on_long_rest=data["expires_on_long_rest"],
                )
            )
