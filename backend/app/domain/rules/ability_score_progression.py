from typing import Literal, TypedDict

from app.domain.rules.abilities import ability_modifier

AbilityName = Literal[
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]

ABILITY_NAMES: tuple[AbilityName, ...] = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)


class AbilityScoreMap(TypedDict):
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


class AbilityScoreImprovementSimulation(TypedDict):
    resulting_character_level: int
    before: AbilityScoreMap
    after: AbilityScoreMap
    increases: dict[AbilityName, int]
    modifiers_before: AbilityScoreMap
    modifiers_after: AbilityScoreMap
    constitution_modifier_change: int
    hit_point_maximum_adjustment: int


def validate_ability_score_improvement(
    *,
    current_scores: AbilityScoreMap,
    increases: dict[AbilityName, int],
) -> None:
    if len(increases) not in (1, 2) or sum(increases.values()) != 2:
        raise ValueError(
            "Aumente um atributo em 2 ou dois atributos diferentes em 1."
        )
    if any(increase not in (1, 2) for increase in increases.values()):
        raise ValueError("Cada aumento de atributo deve ser 1 ou 2.")
    if len(increases) == 2 and any(increase != 1 for increase in increases.values()):
        raise ValueError("Ao escolher dois atributos, aumente cada um em 1.")

    for ability in ABILITY_NAMES:
        score = current_scores[ability]
        if score < 1 or score > 30:
            raise ValueError("As pontuações de atributo devem estar entre 1 e 30.")
        if ability in increases and score + increases[ability] > 20:
            raise ValueError(
                "O aumento de atributo desta característica não pode superar 20."
            )


def _modifiers(scores: AbilityScoreMap) -> AbilityScoreMap:
    return {
        "strength": ability_modifier(scores["strength"]),
        "dexterity": ability_modifier(scores["dexterity"]),
        "constitution": ability_modifier(scores["constitution"]),
        "intelligence": ability_modifier(scores["intelligence"]),
        "wisdom": ability_modifier(scores["wisdom"]),
        "charisma": ability_modifier(scores["charisma"]),
    }


def simulate_ability_score_improvement(
    *,
    current_scores: AbilityScoreMap,
    increases: dict[AbilityName, int],
    resulting_character_level: int,
) -> AbilityScoreImprovementSimulation:
    if resulting_character_level < 1 or resulting_character_level > 20:
        raise ValueError("O nível total resultante deve estar entre 1 e 20.")
    validate_ability_score_improvement(
        current_scores=current_scores,
        increases=increases,
    )

    after = current_scores.copy()
    for ability, increase in increases.items():
        after[ability] += increase

    modifiers_before = _modifiers(current_scores)
    modifiers_after = _modifiers(after)
    constitution_modifier_change = (
        modifiers_after["constitution"] - modifiers_before["constitution"]
    )

    return {
        "resulting_character_level": resulting_character_level,
        "before": current_scores.copy(),
        "after": after,
        "increases": increases.copy(),
        "modifiers_before": modifiers_before,
        "modifiers_after": modifiers_after,
        "constitution_modifier_change": constitution_modifier_change,
        "hit_point_maximum_adjustment": (
            constitution_modifier_change * resulting_character_level
        ),
    }
