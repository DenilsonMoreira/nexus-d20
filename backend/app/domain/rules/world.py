import random
from collections.abc import Iterable, Mapping, Sequence
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, TypedDict

PACE_KM_PER_DAY = {
    "slow": Decimal("30"),
    "normal": Decimal("40"),
    "fast": Decimal("48"),
}

FATIGUE_FACTORS = {
    "slow_pace": -2,
    "fast_pace": 2,
    "encumbered": 2,
    "heavily_encumbered": 4,
    "difficult_terrain": 2,
    "severe_weather": 2,
    "extreme_temperature": 2,
    "insufficient_food": 2,
    "insufficient_water": 3,
    "interrupted_rest": 2,
    "adequate_mount": -2,
    "experienced_guide": -1,
    "proper_equipment": -1,
}


class EncounterResult(TypedDict):
    creatures: list[dict[str, str]]
    estimated_difficulty: str
    difficulty_is_estimate: bool
    challenge_total: str
    seed: int


def rounded(value: Decimal, places: str = "0.1") -> Decimal:
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def plan_travel(
    *,
    distance_km: Decimal,
    pace: str,
    difficult_terrain: bool,
    travelers: Sequence[Mapping[str, Any]],
    travel_hours_per_day: int = 8,
) -> dict[str, object]:
    if distance_km <= 0:
        raise ValueError("A distância deve ser positiva.")
    if pace not in PACE_KM_PER_DAY:
        raise ValueError("Ritmo de viagem inválido.")
    if not travelers:
        raise ValueError("Informe ao menos um viajante.")
    if travel_hours_per_day < 1:
        raise ValueError("As horas de viagem devem ser positivas.")

    limiting = min(travelers, key=lambda traveler: Decimal(str(traveler["speed_m"])))
    speed_ratio = min(Decimal("1"), Decimal(str(limiting["speed_m"])) / Decimal("9"))
    terrain_ratio = Decimal("0.5") if difficult_terrain else Decimal("1")
    daily_distance = (
        PACE_KM_PER_DAY[pace]
        * Decimal(travel_hours_per_day)
        / Decimal("8")
        * speed_ratio
        * terrain_ratio
    )
    days = distance_km / daily_distance
    forced_hours = max(0, travel_hours_per_day - 8)
    return {
        "distance_km": rounded(distance_km),
        "daily_distance_km": rounded(daily_distance),
        "estimated_days": rounded(days, "0.01"),
        "limiting_character_id": str(limiting["character_id"]),
        "forced_march_checks": [
            {"hour_beyond_eight": hour, "constitution_save_dc": 10 + hour}
            for hour in range(1, forced_hours + 1)
        ],
        "food_rations_per_traveler": max(1, int(days.to_integral_value(rounding=ROUND_HALF_UP))),
        "water_liters_per_traveler": rounded(days * Decimal("3.8")),
    }


def fatigue_dc(*, factors: Iterable[str], exhaustion_level: int = 0) -> int:
    return max(
        5,
        8 + exhaustion_level + sum(FATIGUE_FACTORS.get(factor, 0) for factor in factors),
    )


def generate_weighted_encounter(
    *,
    creatures: Sequence[Mapping[str, Any]],
    danger: int,
    seed: int,
    maximum_creatures: int = 6,
) -> EncounterResult:
    if not creatures:
        raise ValueError("Não há criaturas compatíveis com o ambiente.")
    if not 1 <= danger <= 5:
        raise ValueError("Perigo deve estar entre 1 e 5.")
    rng = random.Random(seed)
    population = list(creatures)
    weights = [max(1, int(creature.get("weight", 1))) for creature in population]
    count = min(maximum_creatures, max(1, danger + rng.randint(-1, 1)))
    selected = rng.choices(population, weights=weights, k=count)
    challenge_total = sum(
        Decimal(str(creature.get("challenge_rating", 0))) for creature in selected
    )
    bands = (
        (Decimal("2"), "easy"),
        (Decimal("5"), "moderate"),
        (Decimal("10"), "hard"),
    )
    difficulty = next((label for ceiling, label in bands if challenge_total <= ceiling), "deadly")
    return {
        "creatures": [
            {"id": str(creature["id"]), "name": creature["name"]}
            for creature in selected
        ],
        "estimated_difficulty": difficulty,
        "difficulty_is_estimate": True,
        "challenge_total": str(challenge_total),
        "seed": seed,
    }


def sanitize_public_payload(value: Any) -> Any:
    if isinstance(value, list):
        return [
            sanitized
            for item in value
            if not (isinstance(item, Mapping) and item.get("is_secret") is True)
            for sanitized in [sanitize_public_payload(item)]
        ]
    if isinstance(value, Mapping):
        return {
            key: sanitize_public_payload(item)
            for key, item in value.items()
            if key not in {"secret", "private_data", "gm_notes"} and key != "is_secret"
        }
    return value
