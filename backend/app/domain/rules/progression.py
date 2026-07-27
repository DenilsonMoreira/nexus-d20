from bisect import bisect_right
from typing import Literal, TypedDict

XP_THRESHOLDS = (
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

Qualification = Literal[
    "eligible",
    "insufficient_experience",
    "not_evaluated",
    "level_cap",
]


class ProgressionSnapshot(TypedDict):
    level: int
    experience_threshold: int
    proficiency_bonus: int


class LevelUpSimulation(TypedDict):
    current: ProgressionSnapshot
    next: ProgressionSnapshot | None
    experience_points: int | None
    highest_level_by_experience: int | None
    experience_remaining: int | None
    qualification: Qualification


def validate_level(level: int) -> None:
    if level < 1 or level > 20:
        raise ValueError("O nível deve estar entre 1 e 20.")


def proficiency_bonus(level: int) -> int:
    validate_level(level)
    return 2 + (level - 1) // 4


def progression_snapshot(level: int) -> ProgressionSnapshot:
    validate_level(level)
    return {
        "level": level,
        "experience_threshold": XP_THRESHOLDS[level - 1],
        "proficiency_bonus": proficiency_bonus(level),
    }


def level_for_experience(experience_points: int) -> int:
    if experience_points < 0:
        raise ValueError("Os pontos de experiência não podem ser negativos.")
    return min(bisect_right(XP_THRESHOLDS, experience_points), 20)


def simulate_next_level(
    *,
    current_level: int,
    experience_points: int | None = None,
) -> LevelUpSimulation:
    current = progression_snapshot(current_level)
    if experience_points is not None and experience_points < 0:
        raise ValueError("Os pontos de experiência não podem ser negativos.")
    if current_level == 20:
        return {
            "current": current,
            "next": None,
            "experience_points": experience_points,
            "highest_level_by_experience": (
                level_for_experience(experience_points)
                if experience_points is not None
                else None
            ),
            "experience_remaining": None,
            "qualification": "level_cap",
        }

    next_snapshot = progression_snapshot(current_level + 1)
    if experience_points is None:
        return {
            "current": current,
            "next": next_snapshot,
            "experience_points": None,
            "highest_level_by_experience": None,
            "experience_remaining": None,
            "qualification": "not_evaluated",
        }

    experience_remaining = max(
        next_snapshot["experience_threshold"] - experience_points,
        0,
    )
    return {
        "current": current,
        "next": next_snapshot,
        "experience_points": experience_points,
        "highest_level_by_experience": level_for_experience(experience_points),
        "experience_remaining": experience_remaining,
        "qualification": (
            "eligible" if experience_remaining == 0 else "insufficient_experience"
        ),
    }
