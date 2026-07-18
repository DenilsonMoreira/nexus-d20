from typing import Any, Literal, TypedDict


class AttackResult(TypedDict):
    natural_roll: int
    attack_modifier: int
    total: int
    target_ac: int
    margin: int
    outcome: Literal["critical_miss", "miss", "hit", "critical_hit"]
    attacker_weapon_wear: int
    suggested_target_equipment_wear: int


def resolve_attack(payload: dict[str, Any]) -> AttackResult:
    natural_roll = int(payload["natural_roll"])
    attack_modifier = int(payload["attack_modifier"])
    target_ac = int(payload["target_ac"])

    if not 1 <= natural_roll <= 20:
        raise ValueError("O resultado natural deve estar entre 1 e 20.")
    if target_ac < 0:
        raise ValueError("A CA não pode ser negativa.")

    total = natural_roll + attack_modifier
    margin = abs(total - target_ac)

    if natural_roll == 1:
        outcome: Literal["critical_miss", "miss", "hit", "critical_hit"] = "critical_miss"
        attacker_wear = margin * 2
        target_wear = 0
    elif natural_roll == 20:
        outcome = "critical_hit"
        attacker_wear = 0
        target_wear = margin * 2
    elif total >= target_ac:
        outcome = "hit"
        attacker_wear = margin
        target_wear = 0
    else:
        outcome = "miss"
        attacker_wear = margin
        target_wear = 0

    return {
        "natural_roll": natural_roll,
        "attack_modifier": attack_modifier,
        "total": total,
        "target_ac": target_ac,
        "margin": margin,
        "outcome": outcome,
        "attacker_weapon_wear": attacker_wear,
        "suggested_target_equipment_wear": target_wear,
    }
