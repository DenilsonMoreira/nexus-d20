import hashlib
import json
import uuid
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.domain.rules.abilities import ability_modifier
from app.domain.rules.ability_score_progression import (
    AbilityScoreMap,
    simulate_ability_score_improvement,
)
from app.domain.rules.class_progression import ClassId, simulate_class_level_up
from app.domain.rules.multiclass import validate_multiclass
from app.domain.rules.progression import proficiency_bonus, simulate_next_level
from app.domain.rules.spellcasting import spellcasting_profile
from app.domain.rules.subclass_progression import simulate_subclass_choice
from app.models import (
    Character,
    CharacterClassLevel,
    CharacterSpell,
    CharacterSpellSlot,
    LevelUpEvent,
)
from app.schemas.progression import LevelUpRequest


def _scores(character: Character) -> AbilityScoreMap:
    return cast(
        AbilityScoreMap,
        {
            ability: getattr(character, ability)
            for ability in (
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            )
        },
    )


def _class_map(
    character: Character, base_class_id: ClassId | None
) -> dict[ClassId, dict[str, Any]]:
    if character.class_levels:
        return {
            cast(ClassId, item.class_id): {
                "level": item.level,
                "subclass_id": item.subclass_id,
            }
            for item in character.class_levels
        }
    if base_class_id is None:
        raise AppError(
            422,
            "base_class_required",
            "Informe a classe-base para migrar esta ficha ao assistente de progressão.",
        )
    return {base_class_id: {"level": character.level, "subclass_id": None}}


def simulate_character_level_up(character: Character, payload: LevelUpRequest) -> dict[str, Any]:
    if character.level >= 20:
        raise AppError(409, "character_level_cap", "O personagem já alcançou o nível 20.")
    class_map = _class_map(character, payload.base_class_id)
    current_target_level = int(class_map.get(payload.target_class_id, {"level": 0})["level"])
    scores = _scores(character)
    multiclass = validate_multiclass(
        current_classes=list(class_map),
        target_class=payload.target_class_id,
        ability_scores=scores,
    )
    if current_target_level == 0:
        hp_definition = simulate_class_level_up(
            class_id=payload.target_class_id,
            current_class_level=1,
            constitution_modifier=ability_modifier(character.constitution),
            hit_point_method=payload.hit_point_method,
            hit_die_roll=payload.hit_die_roll,
        )
        target_level = 1
        hit_point_gain = hp_definition["hit_point_gain"]
        required_choices: list[str] = [
            choice for choice in hp_definition["required_choices"] if choice == "hit_points"
        ]
    else:
        hp_definition = simulate_class_level_up(
            class_id=payload.target_class_id,
            current_class_level=current_target_level,
            constitution_modifier=ability_modifier(character.constitution),
            hit_point_method=payload.hit_point_method,
            hit_die_roll=payload.hit_die_roll,
        )
        target_level = current_target_level + 1
        hit_point_gain = hp_definition["hit_point_gain"]
        required_choices = list(hp_definition["required_choices"])

    subclass = simulate_subclass_choice(
        class_id=payload.target_class_id,
        target_class_level=target_level,
        selected_subclass_id=payload.selected_subclass_id,
    )
    existing_subclass = class_map.get(payload.target_class_id, {}).get("subclass_id")
    if subclass["selection_required"] and not existing_subclass:
        required_choices.append("subclass")

    resulting_level = character.level + 1
    hp_adjustment = 0
    resulting_scores = scores
    if "ability_score_improvement" in required_choices and payload.ability_increases:
        asi = simulate_ability_score_improvement(
            current_scores=scores,
            increases=cast(dict[Any, int], payload.ability_increases),
            resulting_character_level=resulting_level,
        )
        hp_adjustment = asi["hit_point_maximum_adjustment"]
        resulting_scores = asi["after"]
        required_choices.remove("ability_score_improvement")

    if payload.hit_point_method is not None and "hit_points" in required_choices:
        required_choices.remove("hit_points")
    if payload.selected_subclass_id and "subclass" in required_choices:
        required_choices.remove("subclass")

    ability_name = spellcasting_profile(
        class_id=payload.target_class_id,
        class_level=target_level,
        ability_modifier=0,
    )["ability"]
    profile = spellcasting_profile(
        class_id=payload.target_class_id,
        class_level=target_level,
        ability_modifier=ability_modifier(resulting_scores[ability_name]) if ability_name else 0,
    )
    warnings: list[str] = []
    if profile["mode"] != "none" and payload.spells is None:
        warnings.append("A lista de magias atual será preservada.")
    if not multiclass["allowed"]:
        warnings.append("Os pré-requisitos de multiclasse não foram atendidos.")

    class_map[payload.target_class_id] = {
        "level": target_level,
        "subclass_id": payload.selected_subclass_id or existing_subclass,
    }
    level_check = simulate_next_level(
        current_level=character.level,
        experience_points=payload.experience_points,
    )
    if level_check["qualification"] == "insufficient_experience":
        warnings.append("A experiência informada ainda não alcança o próximo nível.")

    return {
        "character_id": character.id,
        "current_level": character.level,
        "resulting_level": resulting_level,
        "target_class_id": payload.target_class_id,
        "target_class_level": target_level,
        "hit_point_gain": hit_point_gain,
        "hit_points_max_after": (
            character.hit_points_max + hit_point_gain + hp_adjustment
            if hit_point_gain is not None
            else None
        ),
        "proficiency_bonus_after": proficiency_bonus(resulting_level),
        "class_levels_after": [
            {"class_id": class_id, **values}
            for class_id, values in sorted(class_map.items())
        ],
        "spellcasting": profile,
        "multiclass_allowed": multiclass["allowed"],
        "unmet_multiclass_requirements": multiclass["unmet_requirements"],
        "required_choices": sorted(set(required_choices)),
        "warnings": warnings,
        "ready_to_apply": not required_choices and multiclass["allowed"],
        "_scores_after": resulting_scores,
    }


async def apply_character_level_up(
    db: AsyncSession,
    *,
    character: Character,
    actor_user_id: uuid.UUID,
    idempotency_key: str,
    payload: LevelUpRequest,
) -> tuple[LevelUpEvent, dict[str, Any]]:
    request_data = payload.model_dump(mode="json")
    request_hash = hashlib.sha256(
        json.dumps(request_data, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    existing = await db.scalar(
        select(LevelUpEvent).where(
            LevelUpEvent.character_id == character.id,
            LevelUpEvent.idempotency_key == idempotency_key,
        )
    )
    if existing:
        if existing.request_hash != request_hash:
            raise AppError(
                409,
                "idempotency_key_reused",
                "A chave de idempotência já foi usada com outro conteúdo.",
            )
        return existing, existing.result_data

    result = simulate_character_level_up(character, payload)
    if not result["ready_to_apply"]:
        raise AppError(
            422,
            "level_up_not_ready",
            "Conclua as escolhas obrigatórias antes de aplicar.",
            {"required_choices": result["required_choices"], "warnings": result["warnings"]},
        )
    character.level = int(result["resulting_level"])
    hit_points_max_after = result["hit_points_max_after"]
    if hit_points_max_after is None:
        raise AppError(422, "hit_points_required", "Defina o ganho de pontos de vida.")
    hp_gain = int(hit_points_max_after) - character.hit_points_max
    character.hit_points_max = int(hit_points_max_after)
    character.hit_points_current = min(
        character.hit_points_current + max(0, hp_gain),
        character.hit_points_max,
    )
    for ability, score in result.pop("_scores_after").items():
        setattr(character, ability, score)

    class_rows = {item.class_id: item for item in character.class_levels}
    for item in result["class_levels_after"]:
        class_row = class_rows.get(item["class_id"])
        if class_row is None:
            character.class_levels.append(
                CharacterClassLevel(
                    class_id=item["class_id"],
                    level=item["level"],
                    subclass_id=item["subclass_id"],
                )
            )
        else:
            class_row.level = item["level"]
            class_row.subclass_id = item["subclass_id"]

    if payload.spells is not None:
        character.spells.clear()
        await db.flush()
        character.spells.extend(CharacterSpell(**spell.model_dump()) for spell in payload.spells)

    slot_rows = {item.level: item for item in character.spell_slots}
    for level, maximum in result["spellcasting"]["slots"].items():
        slot_row = slot_rows.get(int(level))
        if slot_row is None:
            character.spell_slots.append(
                CharacterSpellSlot(level=int(level), current_value=maximum, maximum_value=maximum)
            )
        else:
            gained = maximum - slot_row.maximum_value
            slot_row.maximum_value = maximum
            slot_row.current_value = min(
                maximum, slot_row.current_value + max(0, gained)
            )

    persisted_result = json.loads(json.dumps(result, default=str))
    event = LevelUpEvent(
        character_id=character.id,
        actor_user_id=actor_user_id,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        result_data=persisted_result,
    )
    db.add(event)
    await db.flush()
    return event, persisted_result
