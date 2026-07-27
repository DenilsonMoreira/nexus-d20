from app.domain.rules.progression import (
    XP_THRESHOLDS,
    level_for_experience,
    proficiency_bonus,
    simulate_next_level,
)


def test_progression_table_matches_srd_5_1() -> None:
    assert XP_THRESHOLDS == (
        0,
        300,
        900,
        2_700,
        6_500,
        14_000,
        23_000,
        34_000,
        48_000,
        64_000,
        85_000,
        100_000,
        120_000,
        140_000,
        165_000,
        195_000,
        225_000,
        265_000,
        305_000,
        355_000,
    )
    assert [proficiency_bonus(level) for level in range(1, 21)] == [
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        4,
        4,
        4,
        4,
        5,
        5,
        5,
        5,
        6,
        6,
        6,
        6,
    ]


def test_level_for_experience_uses_exact_boundaries() -> None:
    assert level_for_experience(299) == 1
    assert level_for_experience(300) == 2
    assert level_for_experience(6_499) == 4
    assert level_for_experience(6_500) == 5
    assert level_for_experience(999_999) == 20


def test_level_up_simulation_reports_before_after_without_mutation() -> None:
    result = simulate_next_level(current_level=4, experience_points=6_400)

    assert result["current"] == {
        "level": 4,
        "experience_threshold": 2_700,
        "proficiency_bonus": 2,
    }
    assert result["next"] == {
        "level": 5,
        "experience_threshold": 6_500,
        "proficiency_bonus": 3,
    }
    assert result["qualification"] == "insufficient_experience"
    assert result["experience_remaining"] == 100
    assert result["highest_level_by_experience"] == 4


def test_level_cap_has_no_next_snapshot() -> None:
    result = simulate_next_level(current_level=20, experience_points=355_000)

    assert result["next"] is None
    assert result["qualification"] == "level_cap"
    assert result["experience_remaining"] is None


def test_level_up_without_experience_preserves_milestone_policy() -> None:
    result = simulate_next_level(current_level=3)

    assert result["next"] == {
        "level": 4,
        "experience_threshold": 2_700,
        "proficiency_bonus": 2,
    }
    assert result["experience_points"] is None
    assert result["highest_level_by_experience"] is None
    assert result["experience_remaining"] is None
    assert result["qualification"] == "not_evaluated"
