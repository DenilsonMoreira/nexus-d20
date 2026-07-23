import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.domain.rules.abilities import ability_modifier
from app.models import Campaign, CampaignMember, Character
from app.schemas.characters import AbilityResponse, CharacterResponse

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
    }


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
