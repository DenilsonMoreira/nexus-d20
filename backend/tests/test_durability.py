from decimal import Decimal

from app.domain.rules.durability import (
    apply_wear,
    auto_repair,
    durability_snapshot,
    state_for,
)


def test_material_points_produce_different_percentages() -> None:
    iron = durability_snapshot(current_points=90, maximum_points=100, base_damage_die="d10")
    steel = durability_snapshot(current_points=990, maximum_points=1000, base_damage_die="d10")
    assert iron["percentage"] == Decimal("90.0")
    assert steel["percentage"] == Decimal("99.0")


def test_damage_die_reduces_below_fifty_percent() -> None:
    at_fifty = durability_snapshot(current_points=500, maximum_points=1000, base_damage_die="d10")
    below = durability_snapshot(current_points=499, maximum_points=1000, base_damage_die="d10")
    assert at_fifty["effective_damage_die"] == "d10"
    assert below["effective_damage_die"] == "d8"


def test_magic_item_floor() -> None:
    result = apply_wear(
        current_points=550,
        maximum_points=1000,
        wear_points=100,
        is_magical=True,
    )
    assert result == 500


def test_master_can_override_magic_floor() -> None:
    result = apply_wear(
        current_points=550,
        maximum_points=1000,
        wear_points=100,
        is_magical=True,
        allow_below_magic_floor=True,
    )
    assert result == 450


def test_auto_repair() -> None:
    assert auto_repair(current_points=700, maximum_points=1000, repair_percent=Decimal("5")) == 750


def test_state_thresholds() -> None:
    assert state_for(Decimal("100")) == "Ótimo"
    assert state_for(Decimal("75")) == "Bom"
    assert state_for(Decimal("50")) == "Regular"
    assert state_for(Decimal("25")) == "Ruim"
    assert state_for(Decimal("10")) == "Inutilizável"
