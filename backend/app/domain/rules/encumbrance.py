from decimal import ROUND_HALF_UP, Decimal
from typing import Literal, TypedDict

EncumbranceState = Literal[
    "comfortable", "encumbered", "heavily_encumbered", "over_capacity"
]


class EncumbranceResult(TypedDict):
    strength: int
    current_weight_kg: Decimal
    comfortable_limit_kg: Decimal
    heavily_encumbered_limit_kg: Decimal
    maximum_capacity_kg: Decimal
    push_drag_lift_kg: Decimal
    state: EncumbranceState
    speed_penalty_m: Decimal
    current_speed_m: Decimal


def rounded(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def calculate_encumbrance(
    *, strength: int, current_weight_kg: Decimal, base_speed_m: Decimal
) -> EncumbranceResult:
    if strength < 1:
        raise ValueError("Força deve ser maior que zero.")
    if current_weight_kg < 0 or base_speed_m < 0:
        raise ValueError("Peso e deslocamento não podem ser negativos.")

    comfortable = Decimal(strength) * Decimal("2.26796")
    heavy = Decimal(strength) * Decimal("4.53592")
    maximum = Decimal(strength) * Decimal("6.80389")
    push_drag_lift = Decimal(strength) * Decimal("13.6078")

    if current_weight_kg > maximum:
        state: EncumbranceState = "over_capacity"
        penalty = base_speed_m
    elif current_weight_kg > heavy:
        state = "heavily_encumbered"
        penalty = Decimal(6)
    elif current_weight_kg > comfortable:
        state = "encumbered"
        penalty = Decimal(3)
    else:
        state = "comfortable"
        penalty = Decimal(0)

    current_speed = max(Decimal(0), base_speed_m - penalty)
    return {
        "strength": strength,
        "current_weight_kg": rounded(current_weight_kg),
        "comfortable_limit_kg": rounded(comfortable),
        "heavily_encumbered_limit_kg": rounded(heavy),
        "maximum_capacity_kg": rounded(maximum),
        "push_drag_lift_kg": rounded(push_drag_lift),
        "state": state,
        "speed_penalty_m": rounded(penalty),
        "current_speed_m": rounded(current_speed),
    }
