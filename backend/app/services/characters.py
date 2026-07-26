import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.domain.rules.abilities import ability_modifier
from app.models import (
    Campaign,
    CampaignMember,
    Character,
    CharacterProficiency,
    CharacterResource,
)
from app.schemas.characters import (
    AbilityResponse,
    CharacterProficiencyInput,
    CharacterProficiencyResponse,
    CharacterResourceInput,
    CharacterResourceResponse,
    CharacterResponse,
)

ABILITY_FIELDS = (
    ("strength", "FORÇA"),
    ("dexterity", "DESTREZA"),
    ("constitution", "CONSTITUIÇÃO"),
    ("intelligence", "INTELIGÊNCIA"),
    ("wisdom", "SABEDORIA"),
    ("charisma", "CARISMA"),
)


def character_snapshot(character: Character) -> dict[str, object]:
    return {
        "name": character.name,
        "race_name": character.race_name,
        "class_name": character.class_name,
        "subclass_name": character.subclass_name,
        "level": character.level,
        "background": character.background,
        "alignment": character.alignment,
        "hit_points_current": character.hit_points_current,
        "hit_points_max": character.hit_points_max,
        "temporary_hit_points": character.temporary_hit_points,
        "armor_class": character.armor_class,
        "initiative": character.initiative,
        "speed_meters": character.speed_meters,
        "abilities": {field: getattr(character, field) for field, _ in ABILITY_FIELDS},
        "proficiencies": [
            {"category": item.category, "name": item.name}
            for item in sorted(
                character.proficiencies,
                key=lambda value: (value.category, value.name.casefold()),
            )
        ],
        "resources": [
            {
                "name": item.name,
                "current_value": item.current_value,
                "maximum_value": item.maximum_value,
                "recovery": item.recovery,
            }
            for item in sorted(
                character.resources,
                key=lambda value: value.name.casefold(),
            )
        ],
    }


def normalize_character_snapshot(snapshot: dict[str, object]) -> dict[str, object]:
    return {
        **snapshot,
        "proficiencies": snapshot.get("proficiencies", []),
        "resources": snapshot.get("resources", []),
    }


async def apply_character_snapshot(
    db: AsyncSession,
    character: Character,
    snapshot: dict[str, object],
) -> None:
    snapshot = normalize_character_snapshot(snapshot)
    for field in (
        "name",
        "race_name",
        "class_name",
        "subclass_name",
        "level",
        "background",
        "alignment",
        "hit_points_current",
        "hit_points_max",
        "temporary_hit_points",
        "armor_class",
        "initiative",
        "speed_meters",
    ):
        setattr(character, field, snapshot[field])
    abilities = snapshot["abilities"]
    if not isinstance(abilities, dict):
        raise AppError(409, "audit_state_invalid", "O histórico da ficha está inválido.")
    for field, _ in ABILITY_FIELDS:
        setattr(character, field, abilities[field])
    proficiencies = snapshot["proficiencies"]
    resources = snapshot["resources"]
    if not isinstance(proficiencies, list) or not isinstance(resources, list):
        raise AppError(409, "audit_state_invalid", "O histórico da ficha está inválido.")
    try:
        proficiency_items = [
            CharacterProficiencyInput.model_validate(item) for item in proficiencies
        ]
        resource_items = [CharacterResourceInput.model_validate(item) for item in resources]
    except (TypeError, ValueError) as error:
        raise AppError(
            409,
            "audit_state_invalid",
            "O histórico da ficha está inválido.",
        ) from error
    character.proficiencies.clear()
    character.resources.clear()
    await db.flush()
    character.proficiencies.extend(
        CharacterProficiency(
            category=item.category,
            name=item.name,
        )
        for item in proficiency_items
    )
    character.resources.extend(
        CharacterResource(
            name=item.name,
            current_value=item.current_value,
            maximum_value=item.maximum_value,
            recovery=item.recovery,
        )
        for item in resource_items
    )


def character_response(character: Character) -> CharacterResponse:
    return CharacterResponse(
        id=character.id,
        campaign_id=character.campaign_id,
        owner_user_id=character.owner_user_id,
        name=character.name,
        race_name=character.race_name,
        class_name=character.class_name,
        subclass_name=character.subclass_name,
        level=character.level,
        background=character.background,
        alignment=character.alignment,
        hit_points_current=character.hit_points_current,
        hit_points_max=character.hit_points_max,
        temporary_hit_points=character.temporary_hit_points,
        armor_class=character.armor_class,
        initiative=character.initiative,
        speed_meters=character.speed_meters,
        abilities=[
            AbilityResponse(
                code=field,
                label=label,
                score=getattr(character, field),
                modifier=ability_modifier(getattr(character, field)),
            )
            for field, label in ABILITY_FIELDS
        ],
        proficiencies=[
            CharacterProficiencyResponse(category=item.category, name=item.name)
            for item in character.proficiencies
        ],
        resources=[
            CharacterResourceResponse(
                name=item.name,
                current_value=item.current_value,
                maximum_value=item.maximum_value,
                recovery=item.recovery,
            )
            for item in character.resources
        ],
        created_at=character.created_at,
        updated_at=character.updated_at,
    )


async def get_visible_character(
    db: AsyncSession,
    *,
    character_id: uuid.UUID,
    user_id: uuid.UUID,
) -> tuple[Character, str]:
    row = (
        await db.execute(
            select(Character, CampaignMember.role)
            .join(
                CampaignMember,
                (CampaignMember.campaign_id == Character.campaign_id)
                & (CampaignMember.user_id == user_id),
            )
            .join(Campaign, Campaign.id == Character.campaign_id)
            .where(Character.id == character_id, Campaign.is_archived.is_(False))
        )
    ).one_or_none()
    if row is None:
        raise AppError(404, "character_not_found", "Personagem não encontrado.")
    character, role = row
    if role == "observer" or (role != "master" and character.owner_user_id != user_id):
        raise AppError(404, "character_not_found", "Personagem não encontrado.")
    return character, role
