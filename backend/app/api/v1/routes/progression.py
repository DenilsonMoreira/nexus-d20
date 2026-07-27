import uuid
from typing import Annotated

from fastapi import APIRouter, Header

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.errors import AppError
from app.schemas.progression import (
    LevelUpRequest,
    LevelUpResultResponse,
    LevelUpSimulationResponse,
    ProgressionStateResponse,
)
from app.services.audit import record_audit
from app.services.characters import get_visible_character
from app.services.progression import (
    apply_character_level_up,
    simulate_character_level_up,
)

router = APIRouter()
IdempotencyKey = Annotated[str | None, Header(alias="Idempotency-Key")]


@router.get("/{character_id}/progression", response_model=ProgressionStateResponse)
async def progression_state(
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ProgressionStateResponse:
    character, _ = await get_visible_character(
        db, character_id=character_id, user_id=current_user.id
    )
    return ProgressionStateResponse.model_validate(
        {
            "character_id": character.id,
            "total_level": character.level,
            "class_levels": [
                {
                    "class_id": item.class_id,
                    "level": item.level,
                    "subclass_id": item.subclass_id,
                }
                for item in character.class_levels
            ],
            "spells": [
                {
                    "name": item.name,
                    "spell_level": item.spell_level,
                    "is_known": item.is_known,
                    "is_prepared": item.is_prepared,
                    "in_spellbook": item.in_spellbook,
                    "source_class_id": item.source_class_id,
                }
                for item in character.spells
            ],
            "spell_slots": {
                item.level: item.maximum_value for item in character.spell_slots
            },
        }
    )


@router.post(
    "/{character_id}/level-up/simulate",
    response_model=LevelUpSimulationResponse,
)
async def simulate_level_up(
    character_id: uuid.UUID,
    payload: LevelUpRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> LevelUpSimulationResponse:
    character, _ = await get_visible_character(
        db, character_id=character_id, user_id=current_user.id
    )
    return LevelUpSimulationResponse.model_validate(
        simulate_character_level_up(character, payload)
    )


@router.post(
    "/{character_id}/level-up/apply",
    response_model=LevelUpResultResponse,
)
async def apply_level_up(
    character_id: uuid.UUID,
    payload: LevelUpRequest,
    idempotency_key: IdempotencyKey,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> LevelUpResultResponse:
    if not idempotency_key or len(idempotency_key) > 120:
        raise AppError(
            422,
            "idempotency_key_required",
            "Informe uma chave de idempotência válida.",
        )
    character, role = await get_visible_character(
        db, character_id=character_id, user_id=current_user.id
    )
    if role == "observer":
        raise AppError(403, "character_write_forbidden", "Observadores não editam fichas.")
    before: dict[str, object] = {
        "level": character.level,
        "hit_points_max": character.hit_points_max,
    }
    event, result = await apply_character_level_up(
        db,
        character=character,
        actor_user_id=current_user.id,
        idempotency_key=idempotency_key,
        payload=payload,
    )
    if event.created_at is None:
        await db.flush()
    if before["level"] != result["resulting_level"]:
        record_audit(
            db,
            campaign_id=character.campaign_id,
            actor_user_id=current_user.id,
            entity_type="character",
            entity_id=character.id,
            action="character.level_up",
            before_data=before,
            after_data={
                "level": result["resulting_level"],
                "hit_points_max": result["hit_points_max_after"],
                "class_levels": result["class_levels_after"],
            },
            reason=payload.reason,
        )
    await db.commit()
    await db.refresh(event)
    return LevelUpResultResponse.model_validate(
        {**result, "event_id": event.id, "applied_at": event.created_at}
    )
