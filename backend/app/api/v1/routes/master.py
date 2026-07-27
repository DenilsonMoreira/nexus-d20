import hashlib
import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Header
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.api.dependencies import CampaignMaster, CurrentUser, DatabaseSession
from app.core.errors import AppError
from app.domain.rules.rest import simulate_long_rest
from app.models import (
    Character,
    CharacterCondition,
    CharacterSpellSlot,
    ItemInstance,
    LongRestEvent,
)
from app.schemas.master import (
    ConditionCreate,
    LongRestRequest,
    LongRestResponse,
    MasterStateUpdate,
    SpellSlotInput,
)
from app.services.audit import record_audit
from app.services.inventory import get_character_access
from app.services.rest_state import (
    apply_rest_result,
    load_rest_character,
    rest_payload,
    rest_snapshot,
)

campaign_router = APIRouter()
character_router = APIRouter()


async def master_character(
    db: DatabaseSession, character_id: uuid.UUID, current_user: CurrentUser
) -> Character:
    character, member = await get_character_access(db, character_id, current_user)
    if member.role != "master":
        raise AppError(403, "master_role_required", "Apenas o mestre pode realizar esta ação.")
    loaded = await load_rest_character(db, character.id)
    if loaded is None:
        raise AppError(404, "character_not_found", "Personagem não encontrado.")
    return loaded


@campaign_router.get("/{campaign_id}/master-dashboard")
async def master_dashboard(
    master: CampaignMaster, db: DatabaseSession
) -> dict[str, object]:
    characters = (
        await db.scalars(
            select(Character)
            .options(
                selectinload(Character.resources),
                selectinload(Character.conditions),
            )
            .where(
                Character.campaign_id == master.campaign.id,
                Character.is_active_group.is_(True),
            )
            .order_by(Character.name)
        )
    ).all()
    result: list[dict[str, object]] = []
    for character in characters:
        items = (
            await db.scalars(
                select(ItemInstance).where(
                    ItemInstance.character_id == character.id,
                    (ItemInstance.equipped.is_(True))
                    | (ItemInstance.is_active_weapon.is_(True)),
                )
            )
        ).all()
        result.append(
            {
                "id": character.id,
                "name": character.name,
                "hit_points": {
                    "current": character.hit_points_current,
                    "maximum": character.hit_points_max,
                },
                "exhaustion_level": character.exhaustion_level,
                "hidden_fatigue": character.hidden_fatigue,
                "resources": [
                    {
                        "id": resource.id,
                        "name": resource.name,
                        "current": resource.current_value,
                        "maximum": resource.maximum_value,
                        "recovery": resource.recovery,
                    }
                    for resource in character.resources
                ],
                "conditions": [
                    {
                        "id": condition.id,
                        "name": condition.name,
                        "expires_on_long_rest": condition.expires_on_long_rest,
                    }
                    for condition in character.conditions
                ],
                "active_items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "current_durability": item.current_durability,
                        "maximum_durability": item.maximum_durability,
                    }
                    for item in items
                ],
            }
        )
    return {"campaign_id": master.campaign.id, "characters": result}


@character_router.patch("/{character_id}/master-state")
async def update_master_state(
    character_id: uuid.UUID,
    payload: MasterStateUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    character = await master_character(db, character_id, current_user)
    values = payload.model_dump(exclude_unset=True)
    next_maximum = int(values.get("hit_dice_max", character.hit_dice_max))
    next_current = int(values.get("hit_dice_current", character.hit_dice_current))
    if next_current > next_maximum:
        raise AppError(422, "hit_dice_invalid", "Dados de vida atuais superam o máximo.")
    before = {key: getattr(character, key) for key in values}
    for key, value in values.items():
        setattr(character, key, value)
    record_audit(
        db,
        campaign_id=character.campaign_id,
        actor_user_id=current_user.id,
        entity_type="character",
        entity_id=character.id,
        action="character.master_state_updated",
        before_data=before,
        after_data=values,
    )
    await db.commit()
    return {"character_id": character.id, **values}


@character_router.put("/{character_id}/spell-slots")
async def replace_spell_slots(
    character_id: uuid.UUID,
    payload: list[SpellSlotInput],
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    character = await master_character(db, character_id, current_user)
    levels = [slot.level for slot in payload]
    if len(levels) != len(set(levels)):
        raise AppError(422, "spell_slot_duplicate", "Não repita níveis de magia.")
    await db.execute(
        delete(CharacterSpellSlot).where(
            CharacterSpellSlot.character_id == character.id
        )
    )
    db.add_all(
        [
            CharacterSpellSlot(character_id=character.id, **slot.model_dump())
            for slot in payload
        ]
    )
    await db.commit()
    return {"character_id": character.id, "spell_slots": [slot.model_dump() for slot in payload]}


@character_router.post("/{character_id}/conditions")
async def add_condition(
    character_id: uuid.UUID,
    payload: ConditionCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    character = await master_character(db, character_id, current_user)
    condition = CharacterCondition(
        character_id=character.id,
        name=payload.name.strip(),
        description=payload.description,
        expires_on_long_rest=payload.expires_on_long_rest,
    )
    db.add(condition)
    await db.commit()
    await db.refresh(condition)
    return {"id": condition.id, **payload.model_dump()}


async def build_rest(
    character_id: uuid.UUID,
    payload: LongRestRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> tuple[Character, dict[str, object], list[str]]:
    character = await master_character(db, character_id, current_user)
    rules_payload = await rest_payload(db, character, payload.model_dump())
    result = dict(simulate_long_rest(rules_payload))
    expired = (
        [
            condition.name
            for condition in character.conditions
            if condition.expires_on_long_rest
        ]
        if payload.rest_completed
        else []
    )
    return character, result, expired


@character_router.post(
    "/{character_id}/long-rest/simulate", response_model=LongRestResponse
)
async def simulate_rest(
    character_id: uuid.UUID,
    payload: LongRestRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    character, result, expired = await build_rest(
        character_id, payload, current_user, db
    )
    return {
        "character_id": character.id,
        "applied": False,
        "result": result,
        "expired_conditions": expired,
    }


@character_router.post(
    "/{character_id}/long-rest/apply", response_model=LongRestResponse
)
async def apply_rest(
    character_id: uuid.UUID,
    payload: LongRestRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=120)],
) -> dict[str, object]:
    character, result, expired = await build_rest(
        character_id, payload, current_user, db
    )
    request_hash = hashlib.sha256(
        json.dumps(
            {"character_id": str(character_id), **payload.model_dump()},
            sort_keys=True,
        ).encode()
    ).hexdigest()
    existing = await db.scalar(
        select(LongRestEvent).where(
            LongRestEvent.campaign_id == character.campaign_id,
            LongRestEvent.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        if existing.request_hash != request_hash:
            raise AppError(
                409,
                "idempotency_conflict",
                "A chave de idempotência já foi usada com outra solicitação.",
            )
        return {**existing.result_data, "idempotent_replay": True}
    before = await rest_snapshot(db, character)
    if payload.rest_completed:
        expired = await apply_rest_result(db, character, result)
    await db.flush()
    after = await rest_snapshot(db, character)
    response: dict[str, object] = {
        "character_id": str(character.id),
        "applied": True,
        "idempotent_replay": False,
        "result": result,
        "expired_conditions": expired,
    }
    db.add(
        LongRestEvent(
            campaign_id=character.campaign_id,
            character_id=character.id,
            actor_user_id=current_user.id,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            result_data=response,
        )
    )
    record_audit(
        db,
        campaign_id=character.campaign_id,
        actor_user_id=current_user.id,
        entity_type="long_rest",
        entity_id=character.id,
        action="long_rest.applied",
        before_data=before,
        after_data=after,
        reason="Descanso longo aplicado pelo painel do mestre.",
        is_reversible=True,
    )
    await db.commit()
    return response
