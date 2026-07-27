import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.errors import AppError
from app.domain.rules.durability import durability_snapshot, maximum_durability
from app.models import (
    CampaignMember,
    Character,
    CharacterProfession,
    ItemInstance,
    ItemTemplateVersion,
    User,
)


async def get_character_access(
    db: AsyncSession, character_id: uuid.UUID, user: User
) -> tuple[Character, CampaignMember]:
    row = (
        await db.execute(
            select(Character, CampaignMember)
            .join(
                CampaignMember,
                CampaignMember.campaign_id == Character.campaign_id,
            )
            .where(
                Character.id == character_id,
                CampaignMember.user_id == user.id,
            )
        )
    ).one_or_none()
    if row is None:
        raise AppError(404, "character_not_found", "Personagem não encontrado.")
    character, member = row
    if member.role != "master" and character.owner_user_id != user.id:
        raise AppError(403, "character_access_denied", "Você não pode acessar este personagem.")
    return character, member


async def get_item_access(
    db: AsyncSession, item_id: uuid.UUID, user: User
) -> tuple[ItemInstance, Character, CampaignMember]:
    row = (
        await db.execute(
            select(ItemInstance, Character, CampaignMember)
            .options(
                joinedload(ItemInstance.template_version).joinedload(
                    ItemTemplateVersion.template
                ),
                joinedload(ItemInstance.template_version).joinedload(
                    ItemTemplateVersion.material
                ),
                joinedload(ItemInstance.template_version).joinedload(
                    ItemTemplateVersion.quality_level
                ),
            )
            .join(Character, Character.id == ItemInstance.character_id)
            .join(
                CampaignMember,
                CampaignMember.campaign_id == ItemInstance.campaign_id,
            )
            .where(ItemInstance.id == item_id, CampaignMember.user_id == user.id)
        )
    ).one_or_none()
    if row is None:
        raise AppError(404, "item_not_found", "Item não encontrado.")
    item, character, member = row
    if member.role != "master" and character.owner_user_id != user.id:
        raise AppError(403, "item_access_denied", "Você não pode acessar este item.")
    return item, character, member


async def can_see_exact_durability(
    db: AsyncSession,
    *,
    character: Character,
    member: CampaignMember,
    craft_domain: str,
) -> bool:
    if member.role == "master":
        return True
    profession = await db.scalar(
        select(CharacterProfession).where(
            CharacterProfession.character_id == character.id,
            CharacterProfession.domain == craft_domain,
        )
    )
    return profession is not None


async def item_to_response(
    db: AsyncSession,
    item: ItemInstance,
    character: Character,
    member: CampaignMember,
) -> dict[str, object]:
    version = item.template_version
    template = version.template
    snapshot = durability_snapshot(
        current_points=item.current_durability,
        maximum_points=item.maximum_durability,
        base_damage_die=template.base_damage_die,
    )
    exact = await can_see_exact_durability(
        db,
        character=character,
        member=member,
        craft_domain=template.craft_domain,
    )
    return {
        "id": item.id,
        "character_id": item.character_id,
        "name": item.name,
        "category": template.category,
        "quantity": item.quantity,
        "weight_kg": template.weight_kg,
        "price_gp": template.price_gp,
        "equipped": item.equipped,
        "is_active_weapon": item.is_active_weapon,
        "is_magical": version.is_magical,
        "durability": {
            **snapshot,
            "percentage": snapshot["percentage"] if exact else None,
            "current_points": snapshot["current_points"] if exact else None,
            "maximum_points": snapshot["maximum_points"] if exact else None,
        },
    }


def version_maximum_durability(version: ItemTemplateVersion) -> int:
    return maximum_durability(
        material_points=version.material.base_points,
        structure_multiplier=Decimal(version.structure_multiplier),
        quality_multiplier=Decimal(version.quality_level.multiplier),
        magic_multiplier=Decimal(version.magic_multiplier),
    )


def item_snapshot(item: ItemInstance) -> dict[str, object]:
    return {
        "current_durability": item.current_durability,
        "equipped": item.equipped,
        "is_active_weapon": item.is_active_weapon,
    }
