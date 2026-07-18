from decimal import ROUND_HALF_UP, Decimal
from typing import Literal, TypedDict

DurabilityState = Literal["Ótimo", "Bom", "Regular", "Ruim", "Inutilizável"]


class DurabilitySnapshot(TypedDict):
    current_points: int
    maximum_points: int
    percentage: Decimal
    state: DurabilityState
    effective_damage_die: str
    break_risk: bool
    usable: bool


def percentage(current_points: int, maximum_points: int) -> Decimal:
    if maximum_points <= 0:
        raise ValueError("A durabilidade máxima deve ser maior que zero.")
    current = max(0, min(current_points, maximum_points))
    value = Decimal(current) / Decimal(maximum_points) * Decimal(100)
    return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def state_for(percent: Decimal) -> DurabilityState:
    if percent > Decimal(75):
        return "Ótimo"
    if percent > Decimal(50):
        return "Bom"
    if percent > Decimal(25):
        return "Regular"
    if percent > Decimal(10):
        return "Ruim"
    return "Inutilizável"


def reduce_damage_die(die: str) -> str:
    progression = {"d12": "d10", "d10": "d8", "d8": "d6", "d6": "d4", "d4": "1"}
    normalized = die.lower().replace("1", "", 1) if die.lower().startswith("1d") else die.lower()
    return progression.get(normalized, die)


def apply_wear(
    *,
    current_points: int,
    maximum_points: int,
    wear_points: int,
    is_magical: bool = False,
    allow_below_magic_floor: bool = False,
) -> int:
    if wear_points < 0:
        raise ValueError("O desgaste não pode ser negativo.")
    proposed = max(0, current_points - wear_points)
    if is_magical and not allow_below_magic_floor:
        floor = (maximum_points + 1) // 2
        return max(floor, proposed)
    return proposed


def auto_repair(
    *, current_points: int, maximum_points: int, repair_percent: Decimal
) -> int:
    if repair_percent < 0:
        raise ValueError("O percentual de reparo não pode ser negativo.")
    recovered = int((Decimal(maximum_points) * repair_percent / Decimal(100)).to_integral_value())
    return min(maximum_points, current_points + recovered)


def durability_snapshot(
    *, current_points: int, maximum_points: int, base_damage_die: str
) -> DurabilitySnapshot:
    percent = percentage(current_points, maximum_points)
    state = state_for(percent)
    damaged = percent < Decimal(50)
    return {
        "current_points": max(0, min(current_points, maximum_points)),
        "maximum_points": maximum_points,
        "percentage": percent,
        "state": state,
        "effective_damage_die": reduce_damage_die(base_damage_die) if damaged else base_damage_die,
        "break_risk": percent <= Decimal(25),
        "usable": percent > Decimal(10),
    }
