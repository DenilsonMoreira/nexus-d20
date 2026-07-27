import pytest

from app.domain.rules.class_progression import (
    CLASS_DEFINITIONS,
    simulate_class_level_up,
)


def test_all_srd_classes_have_the_expected_hit_point_progression() -> None:
    assert {
        class_id: (
            definition["hit_die_sides"],
            definition["fixed_hit_point_value"],
        )
        for class_id, definition in CLASS_DEFINITIONS.items()
    } == {
        "barbarian": (12, 7),
        "bard": (8, 5),
        "cleric": (8, 5),
        "druid": (8, 5),
        "fighter": (10, 6),
        "monk": (8, 5),
        "paladin": (10, 6),
        "ranger": (10, 6),
        "rogue": (8, 5),
        "sorcerer": (6, 4),
        "warlock": (8, 5),
        "wizard": (6, 4),
    }


def test_fixed_hit_points_and_ability_score_choice_are_simulated() -> None:
    result = simulate_class_level_up(
        class_id="fighter",
        current_class_level=5,
        constitution_modifier=3,
        hit_point_method="fixed",
    )

    assert result["next_class_level"] == 6
    assert result["hit_point_gain"] == 9
    assert result["ability_score_improvement_required"] is True
    assert result["required_choices"] == ["ability_score_improvement"]


def test_missing_hit_point_method_is_reported_as_a_required_choice() -> None:
    result = simulate_class_level_up(
        class_id="wizard",
        current_class_level=2,
        constitution_modifier=1,
    )

    assert result["hit_point_gain"] is None
    assert result["required_choices"] == ["hit_points"]


def test_rolled_hit_points_respect_the_minimum_gain_of_one() -> None:
    result = simulate_class_level_up(
        class_id="sorcerer",
        current_class_level=1,
        constitution_modifier=-3,
        hit_point_method="rolled",
        hit_die_roll=1,
    )

    assert result["hit_point_gain"] == 1


def test_roll_cannot_exceed_the_class_hit_die() -> None:
    with pytest.raises(
        ValueError,
        match=r"A rolagem do dado de vida deve estar entre 1 e 8\.",
    ):
        simulate_class_level_up(
            class_id="rogue",
            current_class_level=3,
            constitution_modifier=2,
            hit_point_method="rolled",
            hit_die_roll=9,
        )


def test_fighter_and_rogue_have_their_additional_ability_score_levels() -> None:
    assert CLASS_DEFINITIONS["fighter"]["ability_score_improvement_levels"] == (
        4,
        6,
        8,
        12,
        14,
        16,
        19,
    )
    assert CLASS_DEFINITIONS["rogue"]["ability_score_improvement_levels"] == (
        4,
        8,
        10,
        12,
        16,
        19,
    )


def test_class_level_cap_has_no_next_level_or_choices() -> None:
    result = simulate_class_level_up(
        class_id="barbarian",
        current_class_level=20,
        constitution_modifier=4,
    )

    assert result["next_class_level"] is None
    assert result["hit_point_gain"] is None
    assert result["required_choices"] == []
    assert result["class_level_cap"] is True
