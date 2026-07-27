from decimal import Decimal

from app.domain.rules.attack import resolve_attack
from app.domain.rules.durability import apply_wear, maximum_durability


def test_iron_and_steel_have_deterministic_maximum_durability() -> None:
    assert maximum_durability(
        material_points=80,
        structure_multiplier=Decimal("1"),
        quality_multiplier=Decimal("1"),
    ) == 80
    assert maximum_durability(
        material_points=120,
        structure_multiplier=Decimal("1.5"),
        quality_multiplier=Decimal("1.25"),
    ) == 225


def test_critical_results_drive_expected_wear() -> None:
    critical_miss = resolve_attack(
        {"natural_roll": 1, "attack_modifier": 4, "target_ac": 16}
    )
    critical_hit = resolve_attack(
        {"natural_roll": 20, "attack_modifier": 4, "target_ac": 16}
    )
    assert critical_miss["attacker_weapon_wear"] == 22
    assert critical_hit["attacker_weapon_wear"] == 0
    assert critical_hit["suggested_target_equipment_wear"] == 16


def test_magical_floor_requires_explicit_override() -> None:
    assert apply_wear(
        current_points=60,
        maximum_points=100,
        wear_points=40,
        is_magical=True,
    ) == 50
    assert apply_wear(
        current_points=60,
        maximum_points=100,
        wear_points=40,
        is_magical=True,
        allow_below_magic_floor=True,
    ) == 20
