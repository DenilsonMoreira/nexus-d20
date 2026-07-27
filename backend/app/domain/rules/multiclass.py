from typing import TypedDict, cast

from app.domain.rules.ability_score_progression import AbilityScoreMap
from app.domain.rules.class_progression import ClassId


class MulticlassValidation(TypedDict):
    allowed: bool
    unmet_requirements: list[str]


REQUIREMENTS: dict[ClassId, tuple[tuple[str, ...], ...]] = {
    "barbarian": (("strength",),),
    "bard": (("charisma",),),
    "cleric": (("wisdom",),),
    "druid": (("wisdom",),),
    "fighter": (("strength", "dexterity"),),
    "monk": (("dexterity",), ("wisdom",)),
    "paladin": (("strength",), ("charisma",)),
    "ranger": (("dexterity",), ("wisdom",)),
    "rogue": (("dexterity",),),
    "sorcerer": (("charisma",),),
    "warlock": (("charisma",),),
    "wizard": (("intelligence",),),
}


def validate_multiclass(
    *,
    current_classes: list[ClassId],
    target_class: ClassId,
    ability_scores: AbilityScoreMap,
) -> MulticlassValidation:
    if not current_classes or target_class in current_classes:
        return {"allowed": True, "unmet_requirements": []}

    unmet: list[str] = []
    scores = cast(dict[str, int], dict(ability_scores))
    for class_id in [*current_classes, target_class]:
        for alternatives in REQUIREMENTS[class_id]:
            if max(scores[ability] for ability in alternatives) < 13:
                unmet.append(f"{class_id}: {' ou '.join(alternatives)} 13")
    return {"allowed": not unmet, "unmet_requirements": unmet}
