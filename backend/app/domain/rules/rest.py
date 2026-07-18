from decimal import Decimal
from typing import Any, TypedDict

from app.domain.rules.durability import auto_repair


class RestResult(TypedDict):
    hit_points_before: int
    hit_points_after: int
    spell_slots_before: dict[str, int]
    spell_slots_after: dict[str, int]
    resources_before: dict[str, int]
    resources_after: dict[str, int]
    hit_dice_before: int
    hit_dice_after: int
    exhaustion_before: int
    exhaustion_after: int
    hidden_fatigue_before: int
    hidden_fatigue_after: int
    magic_items: list[dict[str, Any]]
    warnings: list[str]


def simulate_long_rest(payload: dict[str, Any]) -> RestResult:
    hp_current = int(payload["hit_points_current"])
    hp_maximum = int(payload["hit_points_maximum"])
    slots_current = {str(k): int(v) for k, v in payload.get("spell_slots_current", {}).items()}
    slots_maximum = {str(k): int(v) for k, v in payload.get("spell_slots_maximum", {}).items()}
    resources_current = {str(k): int(v) for k, v in payload.get("resources_current", {}).items()}
    resources_maximum = {str(k): int(v) for k, v in payload.get("resources_maximum", {}).items()}
    long_rest_resources = set(payload.get("long_rest_resource_keys", resources_maximum.keys()))
    hit_dice_current = int(payload.get("hit_dice_current", 0))
    hit_dice_maximum = int(payload.get("hit_dice_maximum", 0))
    exhaustion = int(payload.get("exhaustion_level", 0))
    fatigue = int(payload.get("hidden_fatigue", 0))
    has_food = bool(payload.get("has_sufficient_food", True))
    has_water = bool(payload.get("has_sufficient_water", True))
    rest_completed = bool(payload.get("rest_completed", True))
    antimagia = bool(payload.get("antimagic_zone", False))

    warnings: list[str] = []
    if not rest_completed:
        warnings.append("O descanso não foi concluído; nenhuma recuperação foi aplicada.")
        return {
            "hit_points_before": hp_current,
            "hit_points_after": hp_current,
            "spell_slots_before": slots_current,
            "spell_slots_after": slots_current,
            "resources_before": resources_current,
            "resources_after": resources_current,
            "hit_dice_before": hit_dice_current,
            "hit_dice_after": hit_dice_current,
            "exhaustion_before": exhaustion,
            "exhaustion_after": exhaustion,
            "hidden_fatigue_before": fatigue,
            "hidden_fatigue_after": fatigue,
            "magic_items": payload.get("magic_items", []),
            "warnings": warnings,
        }

    resources_after = resources_current.copy()
    for key in long_rest_resources:
        if key in resources_maximum:
            resources_after[key] = resources_maximum[key]

    recovered_hit_dice = max(1, hit_dice_maximum // 2) if hit_dice_maximum > 0 else 0
    hit_dice_after = min(hit_dice_maximum, hit_dice_current + recovered_hit_dice)

    can_reduce_exhaustion = has_food and has_water
    exhaustion_after = max(0, exhaustion - 1) if can_reduce_exhaustion else exhaustion
    if exhaustion and not can_reduce_exhaustion:
        warnings.append("Exaustão não reduzida por falta de alimento ou água suficientes.")

    fatigue_recovery = 2 if has_food and has_water else 1
    fatigue_after = max(0, fatigue - fatigue_recovery)

    item_results: list[dict[str, Any]] = []
    for item in payload.get("magic_items", []):
        result = dict(item)
        if antimagia:
            result["current_points_after"] = int(item["current_points"])
            result["recovered_points"] = 0
            result["warning"] = "Autorreparo bloqueado por antimagia."
        else:
            after = auto_repair(
                current_points=int(item["current_points"]),
                maximum_points=int(item["maximum_points"]),
                repair_percent=Decimal(str(item.get("auto_repair_percent", 0))),
            )
            result["current_points_after"] = after
            result["recovered_points"] = after - int(item["current_points"])
        item_results.append(result)

    return {
        "hit_points_before": hp_current,
        "hit_points_after": hp_maximum,
        "spell_slots_before": slots_current,
        "spell_slots_after": slots_maximum,
        "resources_before": resources_current,
        "resources_after": resources_after,
        "hit_dice_before": hit_dice_current,
        "hit_dice_after": hit_dice_after,
        "exhaustion_before": exhaustion,
        "exhaustion_after": exhaustion_after,
        "hidden_fatigue_before": fatigue,
        "hidden_fatigue_after": fatigue_after,
        "magic_items": item_results,
        "warnings": warnings,
    }
