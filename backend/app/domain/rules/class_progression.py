from typing import Literal, TypedDict

ClassId = Literal[
    "barbarian",
    "bard",
    "cleric",
    "druid",
    "fighter",
    "monk",
    "paladin",
    "ranger",
    "rogue",
    "sorcerer",
    "warlock",
    "wizard",
]
HitPointMethod = Literal["fixed", "rolled"]
RequiredChoice = Literal["hit_points", "ability_score_improvement"]

STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS = (4, 8, 12, 16, 19)


class ClassDefinition(TypedDict):
    label: str
    hit_die_sides: int
    fixed_hit_point_value: int
    ability_score_improvement_levels: tuple[int, ...]


class ClassLevelUpSimulation(TypedDict):
    class_id: ClassId
    class_label: str
    current_class_level: int
    next_class_level: int | None
    hit_die_sides: int
    fixed_hit_point_value: int
    hit_point_method: HitPointMethod | None
    hit_die_roll: int | None
    constitution_modifier: int
    hit_point_gain: int | None
    ability_score_improvement_required: bool
    required_choices: list[RequiredChoice]
    class_level_cap: bool


CLASS_DEFINITIONS: dict[ClassId, ClassDefinition] = {
    "barbarian": {
        "label": "Bárbaro",
        "hit_die_sides": 12,
        "fixed_hit_point_value": 7,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "bard": {
        "label": "Bardo",
        "hit_die_sides": 8,
        "fixed_hit_point_value": 5,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "cleric": {
        "label": "Clérigo",
        "hit_die_sides": 8,
        "fixed_hit_point_value": 5,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "druid": {
        "label": "Druida",
        "hit_die_sides": 8,
        "fixed_hit_point_value": 5,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "fighter": {
        "label": "Guerreiro",
        "hit_die_sides": 10,
        "fixed_hit_point_value": 6,
        "ability_score_improvement_levels": (4, 6, 8, 12, 14, 16, 19),
    },
    "monk": {
        "label": "Monge",
        "hit_die_sides": 8,
        "fixed_hit_point_value": 5,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "paladin": {
        "label": "Paladino",
        "hit_die_sides": 10,
        "fixed_hit_point_value": 6,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "ranger": {
        "label": "Patrulheiro",
        "hit_die_sides": 10,
        "fixed_hit_point_value": 6,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "rogue": {
        "label": "Ladino",
        "hit_die_sides": 8,
        "fixed_hit_point_value": 5,
        "ability_score_improvement_levels": (4, 8, 10, 12, 16, 19),
    },
    "sorcerer": {
        "label": "Feiticeiro",
        "hit_die_sides": 6,
        "fixed_hit_point_value": 4,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "warlock": {
        "label": "Bruxo",
        "hit_die_sides": 8,
        "fixed_hit_point_value": 5,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
    "wizard": {
        "label": "Mago",
        "hit_die_sides": 6,
        "fixed_hit_point_value": 4,
        "ability_score_improvement_levels": STANDARD_ABILITY_SCORE_IMPROVEMENT_LEVELS,
    },
}


def validate_hit_point_choice(
    *,
    class_id: ClassId,
    hit_point_method: HitPointMethod | None,
    hit_die_roll: int | None,
) -> None:
    if hit_point_method is None:
        if hit_die_roll is not None:
            raise ValueError("Informe o método de ganho de PV para usar uma rolagem.")
        return
    if hit_point_method == "fixed":
        if hit_die_roll is not None:
            raise ValueError("O valor fixo de PV não aceita uma rolagem.")
        return
    if hit_die_roll is None:
        raise ValueError("Informe o resultado do dado de vida.")
    hit_die_sides = CLASS_DEFINITIONS[class_id]["hit_die_sides"]
    if hit_die_roll < 1 or hit_die_roll > hit_die_sides:
        raise ValueError(f"A rolagem do dado de vida deve estar entre 1 e {hit_die_sides}.")


def simulate_class_level_up(
    *,
    class_id: ClassId,
    current_class_level: int,
    constitution_modifier: int,
    hit_point_method: HitPointMethod | None = None,
    hit_die_roll: int | None = None,
) -> ClassLevelUpSimulation:
    if current_class_level < 1 or current_class_level > 20:
        raise ValueError("O nível da classe deve estar entre 1 e 20.")
    validate_hit_point_choice(
        class_id=class_id,
        hit_point_method=hit_point_method,
        hit_die_roll=hit_die_roll,
    )

    definition = CLASS_DEFINITIONS[class_id]
    if current_class_level == 20:
        return {
            "class_id": class_id,
            "class_label": definition["label"],
            "current_class_level": current_class_level,
            "next_class_level": None,
            "hit_die_sides": definition["hit_die_sides"],
            "fixed_hit_point_value": definition["fixed_hit_point_value"],
            "hit_point_method": hit_point_method,
            "hit_die_roll": hit_die_roll,
            "constitution_modifier": constitution_modifier,
            "hit_point_gain": None,
            "ability_score_improvement_required": False,
            "required_choices": [],
            "class_level_cap": True,
        }

    next_class_level = current_class_level + 1
    required_choices: list[RequiredChoice] = []
    hit_point_gain: int | None = None
    if hit_point_method is None:
        required_choices.append("hit_points")
    elif hit_point_method == "fixed":
        hit_point_gain = max(
            1,
            definition["fixed_hit_point_value"] + constitution_modifier,
        )
    else:
        if hit_die_roll is None:
            raise AssertionError("A rolagem foi validada e deveria estar presente.")
        hit_point_gain = max(1, hit_die_roll + constitution_modifier)

    ability_score_improvement_required = (
        next_class_level in definition["ability_score_improvement_levels"]
    )
    if ability_score_improvement_required:
        required_choices.append("ability_score_improvement")

    return {
        "class_id": class_id,
        "class_label": definition["label"],
        "current_class_level": current_class_level,
        "next_class_level": next_class_level,
        "hit_die_sides": definition["hit_die_sides"],
        "fixed_hit_point_value": definition["fixed_hit_point_value"],
        "hit_point_method": hit_point_method,
        "hit_die_roll": hit_die_roll,
        "constitution_modifier": constitution_modifier,
        "hit_point_gain": hit_point_gain,
        "ability_score_improvement_required": ability_score_improvement_required,
        "required_choices": required_choices,
        "class_level_cap": False,
    }
