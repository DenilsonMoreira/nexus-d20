import pytest

from app.domain.rules.ability_score_progression import (
    simulate_ability_score_improvement,
)

BASE_SCORES = {
    "strength": 15,
    "dexterity": 14,
    "constitution": 17,
    "intelligence": 10,
    "wisdom": 12,
    "charisma": 8,
}


def test_single_ability_can_increase_by_two() -> None:
    result = simulate_ability_score_improvement(
        current_scores=BASE_SCORES,
        increases={"strength": 2},
        resulting_character_level=4,
    )

    assert result["after"]["strength"] == 17
    assert result["after"]["dexterity"] == 14
    assert result["modifiers_before"]["strength"] == 2
    assert result["modifiers_after"]["strength"] == 3
    assert result["hit_point_maximum_adjustment"] == 0


def test_two_different_abilities_can_increase_by_one() -> None:
    result = simulate_ability_score_improvement(
        current_scores=BASE_SCORES,
        increases={"dexterity": 1, "wisdom": 1},
        resulting_character_level=8,
    )

    assert result["after"]["dexterity"] == 15
    assert result["after"]["wisdom"] == 13
    assert result["modifiers_before"] == result["modifiers_after"]


def test_constitution_modifier_change_adjusts_all_attained_levels() -> None:
    result = simulate_ability_score_improvement(
        current_scores=BASE_SCORES,
        increases={"constitution": 1, "charisma": 1},
        resulting_character_level=8,
    )

    assert result["after"]["constitution"] == 18
    assert result["constitution_modifier_change"] == 1
    assert result["hit_point_maximum_adjustment"] == 8


def test_score_cannot_be_increased_above_twenty() -> None:
    scores = BASE_SCORES | {"strength": 19}

    with pytest.raises(
        ValueError,
        match=r"O aumento de atributo desta característica não pode superar 20\.",
    ):
        simulate_ability_score_improvement(
            current_scores=scores,
            increases={"strength": 2},
            resulting_character_level=4,
        )


@pytest.mark.parametrize(
    "increases",
    [
        {"strength": 1},
        {"strength": 2, "dexterity": 1},
        {"strength": 1, "dexterity": 1, "wisdom": 0},
    ],
)
def test_choice_must_spend_exactly_two_points(
    increases: dict[str, int],
) -> None:
    with pytest.raises(
        ValueError,
        match=r"Aumente um atributo em 2 ou dois atributos diferentes em 1\.",
    ):
        simulate_ability_score_improvement(
            current_scores=BASE_SCORES,
            increases=increases,  # type: ignore[arg-type]
            resulting_character_level=4,
        )


def test_input_maps_are_not_mutated() -> None:
    scores = BASE_SCORES.copy()
    increases = {"intelligence": 2}

    simulate_ability_score_improvement(
        current_scores=scores,
        increases=increases,
        resulting_character_level=12,
    )

    assert scores == BASE_SCORES
    assert increases == {"intelligence": 2}
