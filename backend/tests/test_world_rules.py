from decimal import Decimal

from app.domain.rules.world import (
    fatigue_dc,
    generate_weighted_encounter,
    plan_travel,
    sanitize_public_payload,
)


def test_weighted_encounter_is_deterministic_and_estimated() -> None:
    creatures = [
        {
            "id": "wolf",
            "name": "Lobo",
            "challenge_rating": Decimal("0.25"),
            "weight": 5,
        },
        {
            "id": "owlbear",
            "name": "Urso-coruja",
            "challenge_rating": Decimal("3"),
            "weight": 1,
        },
    ]
    first = generate_weighted_encounter(creatures=creatures, danger=3, seed=42)
    second = generate_weighted_encounter(creatures=creatures, danger=3, seed=42)
    assert first == second
    assert first["difficulty_is_estimate"] is True
    assert first["estimated_difficulty"] in {"easy", "moderate", "hard", "deadly"}


def test_travel_uses_slowest_character_and_official_forced_march_dc() -> None:
    result = plan_travel(
        distance_km=Decimal("60"),
        pace="normal",
        difficult_terrain=True,
        travel_hours_per_day=10,
        travelers=[
            {"character_id": "fast", "speed_m": Decimal("9")},
            {"character_id": "slow", "speed_m": Decimal("6")},
        ],
    )
    assert result["limiting_character_id"] == "slow"
    assert result["daily_distance_km"] == Decimal("16.7")
    assert result["forced_march_checks"] == [
        {"hour_beyond_eight": 1, "constitution_save_dc": 11},
        {"hour_beyond_eight": 2, "constitution_save_dc": 12},
    ]


def test_hidden_fatigue_is_separate_and_optional() -> None:
    assert fatigue_dc(factors=["fast_pace", "severe_weather"]) == 12
    assert fatigue_dc(factors=["slow_pace", "adequate_mount"]) == 5


def test_public_payload_removes_secrets_before_serialization() -> None:
    payload = [
        {"title": "Pista pública", "content": "Pegadas"},
        {"title": "Traidor", "is_secret": True, "secret": "É o regente"},
        {
            "title": "Mapa",
            "private_data": {"coordinates": "cofre"},
            "children": [{"title": "Armadilha", "is_secret": True}],
        },
    ]
    assert sanitize_public_payload(payload) == [
        {"title": "Pista pública", "content": "Pegadas"},
        {"title": "Mapa", "children": []},
    ]
