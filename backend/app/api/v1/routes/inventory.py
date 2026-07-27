import uuid

from fastapi import APIRouter, status
from sqlalchemy import delete, select, update
from sqlalchemy.orm import joinedload

from app.api.dependencies import (
    CampaignAccessDependency,
    CampaignMaster,
    CurrentUser,
    DatabaseSession,
)
from app.core.errors import AppError
from app.domain.rules.attack import resolve_attack
from app.domain.rules.durability import apply_wear
from app.models import (
    CharacterProfession,
    DurabilityEvent,
    ItemInstance,
    ItemTemplate,
    ItemTemplateVersion,
    Material,
    QualityLevel,
)
from app.schemas.inventory import (
    AttackInput,
    CatalogEntry,
    DurabilityChangeResponse,
    DurabilityEventResponse,
    ItemCreate,
    ItemResponse,
    ItemStateUpdate,
    ItemTemplateCreate,
    ItemTemplateResponse,
    ProfessionUpdate,
    RepairInput,
)
from app.services.audit import record_audit
from app.services.inventory import (
    get_character_access,
    get_item_access,
    item_snapshot,
    item_to_response,
    version_maximum_durability,
)

campaign_router = APIRouter()
character_router = APIRouter()
router = APIRouter()


def template_response(version: ItemTemplateVersion) -> dict[str, object]:
    template = version.template
    return {
        "id": template.id,
        "version_id": version.id,
        "name": template.name,
        "category": template.category,
        "craft_domain": template.craft_domain,
        "base_damage_die": template.base_damage_die,
        "weight_kg": template.weight_kg,
        "price_gp": template.price_gp,
        "material_code": version.material.code,
        "quality_code": version.quality_level.code,
        "maximum_durability": version_maximum_durability(version),
        "is_magical": version.is_magical,
        "auto_repair_percent": version.auto_repair_percent,
    }


@campaign_router.get("/{campaign_id}/item-catalog", response_model=dict[str, list[CatalogEntry]])
async def catalog(
    access: CampaignAccessDependency, db: DatabaseSession
) -> dict[str, list[object]]:
    materials = list((await db.scalars(select(Material).order_by(Material.name))).all())
    qualities = list(
        (
            await db.scalars(
                select(QualityLevel).order_by(QualityLevel.multiplier)
            )
        ).all()
    )
    return {
        "materials": list[object](materials),
        "quality_levels": list[object](qualities),
    }


@campaign_router.post(
    "/{campaign_id}/item-templates",
    response_model=ItemTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    payload: ItemTemplateCreate,
    master: CampaignMaster,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> dict[str, object]:
    material = await db.scalar(select(Material).where(Material.code == payload.material_code))
    quality = await db.scalar(
        select(QualityLevel).where(QualityLevel.code == payload.quality_code)
    )
    if material is None or quality is None:
        raise AppError(422, "catalog_entry_not_found", "Material ou qualidade inválidos.")
    template = ItemTemplate(
        campaign_id=master.campaign.id,
        name=payload.name.strip(),
        category=payload.category.strip().lower(),
        craft_domain=payload.craft_domain.strip().lower(),
        base_damage_die=payload.base_damage_die.removeprefix("1"),
        weight_kg=payload.weight_kg,
        price_gp=payload.price_gp,
    )
    db.add(template)
    await db.flush()
    version = ItemTemplateVersion(
        template_id=template.id,
        material_id=material.id,
        quality_level_id=quality.id,
        structure_multiplier=payload.structure_multiplier,
        magic_multiplier=payload.magic_multiplier,
        is_magical=payload.is_magical,
        auto_repair_percent=payload.auto_repair_percent,
        template=template,
        material=material,
        quality_level=quality,
    )
    db.add(version)
    record_audit(
        db,
        campaign_id=master.campaign.id,
        actor_user_id=current_user.id,
        entity_type="item_template",
        entity_id=template.id,
        action="item_template.created",
        after_data={"name": template.name},
    )
    await db.commit()
    return template_response(version)


@campaign_router.get(
    "/{campaign_id}/item-templates", response_model=list[ItemTemplateResponse]
)
async def list_templates(
    access: CampaignAccessDependency, db: DatabaseSession
) -> list[dict[str, object]]:
    versions = (
        await db.scalars(
            select(ItemTemplateVersion)
            .options(
                joinedload(ItemTemplateVersion.template),
                joinedload(ItemTemplateVersion.material),
                joinedload(ItemTemplateVersion.quality_level),
            )
            .join(ItemTemplate)
            .where(ItemTemplate.campaign_id == access.campaign.id)
            .order_by(ItemTemplate.name)
        )
    ).all()
    return [template_response(version) for version in versions]


@character_router.put("/{character_id}/professions", response_model=list[str])
async def update_professions(
    character_id: uuid.UUID,
    payload: ProfessionUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[str]:
    character, member = await get_character_access(db, character_id, current_user)
    await db.execute(
        delete(CharacterProfession).where(CharacterProfession.character_id == character.id)
    )
    db.add_all(
        [CharacterProfession(character_id=character.id, domain=value) for value in payload.domains]
    )
    if member.role == "master":
        record_audit(
            db,
            campaign_id=character.campaign_id,
            actor_user_id=current_user.id,
            entity_type="character",
            entity_id=character.id,
            action="character.professions_updated",
            after_data={"domains": payload.domains},
        )
    await db.commit()
    return payload.domains


@character_router.post(
    "/{character_id}/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED
)
async def create_item(
    character_id: uuid.UUID,
    payload: ItemCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    character, member = await get_character_access(db, character_id, current_user)
    if member.role != "master":
        raise AppError(403, "master_role_required", "Apenas o mestre pode criar itens.")
    version = await db.scalar(
        select(ItemTemplateVersion)
        .options(
            joinedload(ItemTemplateVersion.template),
            joinedload(ItemTemplateVersion.material),
            joinedload(ItemTemplateVersion.quality_level),
        )
        .where(ItemTemplateVersion.id == payload.template_version_id)
    )
    if version is None or version.template.campaign_id != character.campaign_id:
        raise AppError(422, "template_not_found", "Modelo de item inválido.")
    maximum = version_maximum_durability(version)
    item = ItemInstance(
        campaign_id=character.campaign_id,
        character_id=character.id,
        template_version_id=version.id,
        name=(payload.name or version.template.name).strip(),
        quantity=payload.quantity,
        current_durability=maximum,
        maximum_durability=maximum,
        template_version=version,
    )
    db.add(item)
    await db.flush()
    record_audit(
        db,
        campaign_id=character.campaign_id,
        actor_user_id=current_user.id,
        entity_type="item",
        entity_id=item.id,
        action="item.created",
        after_data={"name": item.name, "maximum_durability": maximum},
    )
    await db.commit()
    return await item_to_response(db, item, character, member)


@character_router.get("/{character_id}/items", response_model=list[ItemResponse])
async def list_items(
    character_id: uuid.UUID, current_user: CurrentUser, db: DatabaseSession
) -> list[dict[str, object]]:
    character, member = await get_character_access(db, character_id, current_user)
    items = (
        await db.scalars(
            select(ItemInstance)
            .options(
                joinedload(ItemInstance.template_version).joinedload(ItemTemplateVersion.template),
                joinedload(ItemInstance.template_version).joinedload(ItemTemplateVersion.material),
                joinedload(ItemInstance.template_version).joinedload(
                    ItemTemplateVersion.quality_level
                ),
            )
            .where(ItemInstance.character_id == character.id)
            .order_by(ItemInstance.name)
        )
    ).all()
    return [await item_to_response(db, item, character, member) for item in items]


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item_state(
    item_id: uuid.UUID,
    payload: ItemStateUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    item, character, member = await get_item_access(db, item_id, current_user)
    if payload.equipped is not None:
        item.equipped = payload.equipped
    if payload.is_active_weapon is not None:
        if payload.is_active_weapon:
            await db.execute(
                update(ItemInstance)
                .where(
                    ItemInstance.character_id == character.id,
                    ItemInstance.id != item.id,
                )
                .values(is_active_weapon=False)
            )
        item.is_active_weapon = payload.is_active_weapon
    await db.commit()
    return await item_to_response(db, item, character, member)


async def attack_change(
    item_id: uuid.UUID,
    payload: AttackInput,
    current_user: CurrentUser,
    db: DatabaseSession,
    *,
    persist: bool,
) -> dict[str, object]:
    item, character, member = await get_item_access(db, item_id, current_user)
    if payload.allow_below_magic_floor and member.role != "master":
        raise AppError(
            403,
            "master_override_required",
            "Apenas o mestre pode ignorar o piso mágico.",
        )
    attack = resolve_attack(payload.model_dump())
    before = item.current_durability
    after = apply_wear(
        current_points=before,
        maximum_points=item.maximum_durability,
        wear_points=attack["attacker_weapon_wear"],
        is_magical=item.template_version.is_magical,
        allow_below_magic_floor=payload.allow_below_magic_floor,
    )
    if persist:
        item.current_durability = after
        db.add(DurabilityEvent(
            campaign_id=item.campaign_id,
            item_instance_id=item.id,
            actor_user_id=current_user.id,
            event_type="attack",
            points=before - after,
            before_points=before,
            after_points=after,
            reason=payload.reason,
        ))
        if member.role == "master":
            record_audit(
                db,
                campaign_id=item.campaign_id,
                actor_user_id=current_user.id,
                entity_type="item",
                entity_id=item.id,
                action="item.durability_changed",
                before_data={**item_snapshot(item), "current_durability": before},
                after_data=item_snapshot(item),
                reason=payload.reason,
                is_reversible=True,
            )
        await db.commit()
    response = await item_to_response(db, item, character, member)
    if not persist:
        item.current_durability = after
        response = await item_to_response(db, item, character, member)
        item.current_durability = before
    return {
        "item": response,
        "event_type": "attack",
        "points": before - after,
        "before_points": before,
        "after_points": after,
        "attack": attack,
    }


@router.post("/{item_id}/attacks/simulate", response_model=DurabilityChangeResponse)
async def simulate_attack(
    item_id: uuid.UUID,
    payload: AttackInput,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    return await attack_change(item_id, payload, current_user, db, persist=False)


@router.post("/{item_id}/attacks/apply", response_model=DurabilityChangeResponse)
async def apply_attack(
    item_id: uuid.UUID,
    payload: AttackInput,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    return await attack_change(item_id, payload, current_user, db, persist=True)


@router.post("/{item_id}/repairs", response_model=DurabilityChangeResponse)
async def repair_item(
    item_id: uuid.UUID, payload: RepairInput, current_user: CurrentUser, db: DatabaseSession
) -> dict[str, object]:
    item, character, member = await get_item_access(db, item_id, current_user)
    if member.role != "master":
        raise AppError(403, "master_role_required", "Apenas o mestre pode reparar itens.")
    before = item.current_durability
    after = min(item.maximum_durability, before + payload.points)
    item.current_durability = after
    db.add(DurabilityEvent(
        campaign_id=item.campaign_id,
        item_instance_id=item.id,
        actor_user_id=current_user.id,
        event_type="repair",
        points=after - before,
        before_points=before,
        after_points=after,
        reason=payload.reason,
    ))
    record_audit(
        db,
        campaign_id=item.campaign_id,
        actor_user_id=current_user.id,
        entity_type="item",
        entity_id=item.id,
        action="item.durability_changed",
        before_data={**item_snapshot(item), "current_durability": before},
        after_data=item_snapshot(item),
        reason=payload.reason,
        is_reversible=True,
    )
    await db.commit()
    return {
        "item": await item_to_response(db, item, character, member),
        "event_type": "repair",
        "points": after - before,
        "before_points": before,
        "after_points": after,
        "attack": None,
    }


@router.get("/{item_id}/durability-events", response_model=list[DurabilityEventResponse])
async def durability_history(
    item_id: uuid.UUID, current_user: CurrentUser, db: DatabaseSession
) -> list[DurabilityEvent]:
    await get_item_access(db, item_id, current_user)
    return list((await db.scalars(
        select(DurabilityEvent)
        .where(DurabilityEvent.item_instance_id == item_id)
        .order_by(DurabilityEvent.created_at.desc())
    )).all())
