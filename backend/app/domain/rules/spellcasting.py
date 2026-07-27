from typing import Literal, TypedDict

from app.domain.rules.class_progression import ClassId

SpellcastingMode = Literal["none", "known", "prepared", "spellbook", "pact"]
SpellcastingAbility = Literal["intelligence", "wisdom", "charisma"]

FULL_CASTER_SLOTS: tuple[tuple[int, ...], ...] = (
    (),
    (2,),
    (3,),
    (4, 2),
    (4, 3),
    (4, 3, 2),
    (4, 3, 3),
    (4, 3, 3, 1),
    (4, 3, 3, 2),
    (4, 3, 3, 3, 1),
    (4, 3, 3, 3, 2),
    (4, 3, 3, 3, 2, 1),
    (4, 3, 3, 3, 2, 1),
    (4, 3, 3, 3, 2, 1, 1),
    (4, 3, 3, 3, 2, 1, 1),
    (4, 3, 3, 3, 2, 1, 1, 1),
    (4, 3, 3, 3, 2, 1, 1, 1),
    (4, 3, 3, 3, 2, 1, 1, 1, 1),
    (4, 3, 3, 3, 3, 1, 1, 1, 1),
    (4, 3, 3, 3, 3, 2, 1, 1, 1),
    (4, 3, 3, 3, 3, 2, 2, 1, 1),
)

HALF_CASTER_SLOTS: tuple[tuple[int, ...], ...] = (
    (),
    (),
    (2,),
    (3,),
    (3,),
    (4, 2),
    (4, 2),
    (4, 3),
    (4, 3),
    (4, 3, 2),
    (4, 3, 2),
    (4, 3, 3),
    (4, 3, 3),
    (4, 3, 3, 1),
    (4, 3, 3, 1),
    (4, 3, 3, 2),
    (4, 3, 3, 2),
    (4, 3, 3, 3, 1),
    (4, 3, 3, 3, 1),
    (4, 3, 3, 3, 2),
    (4, 3, 3, 3, 2),
)

CANTRIPS: dict[ClassId, tuple[int, ...]] = {
    "bard": (2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4),
    "cleric": (3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5),
    "druid": (2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4),
    "sorcerer": (4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6),
    "warlock": (2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4),
    "wizard": (3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5),
}

KNOWN_SPELLS: dict[ClassId, tuple[int, ...]] = {
    "bard": (4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 15, 16, 18, 19, 19, 20, 22, 22, 22),
    "ranger": (0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11),
    "sorcerer": (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15),
    "warlock": (2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15),
}


class SpellcastingProfile(TypedDict):
    mode: SpellcastingMode
    ability: SpellcastingAbility | None
    cantrips_known: int
    spells_known: int | None
    prepared_limit: int | None
    spellbook_minimum: int | None
    slots: dict[int, int]
    pact_slot_level: int | None


SPELLCASTING: dict[ClassId, tuple[SpellcastingMode, SpellcastingAbility | None]] = {
    "barbarian": ("none", None),
    "bard": ("known", "charisma"),
    "cleric": ("prepared", "wisdom"),
    "druid": ("prepared", "wisdom"),
    "fighter": ("none", None),
    "monk": ("none", None),
    "paladin": ("prepared", "charisma"),
    "ranger": ("known", "wisdom"),
    "rogue": ("none", None),
    "sorcerer": ("known", "charisma"),
    "warlock": ("pact", "charisma"),
    "wizard": ("spellbook", "intelligence"),
}


def _slots(values: tuple[int, ...]) -> dict[int, int]:
    return {level: count for level, count in enumerate(values, start=1) if count}


def _pact_slots(level: int) -> tuple[int, int]:
    slot_count = 1 if level == 1 else 2 if level <= 10 else 3 if level <= 16 else 4
    slot_level = min(5, (level + 1) // 2)
    return slot_count, slot_level


def spellcasting_profile(
    *,
    class_id: ClassId,
    class_level: int,
    ability_modifier: int,
) -> SpellcastingProfile:
    if class_level < 1 or class_level > 20:
        raise ValueError("O nível da classe deve estar entre 1 e 20.")
    mode, ability = SPELLCASTING[class_id]
    cantrips = CANTRIPS.get(class_id, (0,) * 20)[class_level - 1]
    known = KNOWN_SPELLS.get(class_id)
    prepared: int | None = None
    spellbook_minimum: int | None = None
    slots: dict[int, int] = {}
    pact_slot_level: int | None = None

    if class_id in {"bard", "cleric", "druid", "sorcerer", "wizard"}:
        slots = _slots(FULL_CASTER_SLOTS[class_level])
    elif class_id in {"paladin", "ranger"}:
        slots = _slots(HALF_CASTER_SLOTS[class_level])
    elif class_id == "warlock":
        count, pact_slot_level = _pact_slots(class_level)
        slots = {pact_slot_level: count}

    if mode == "prepared":
        prepared = 0 if class_id == "paladin" and class_level == 1 else max(
            1, ability_modifier + (class_level // 2 if class_id == "paladin" else class_level)
        )
    elif mode == "spellbook":
        prepared = max(1, ability_modifier + class_level)
        spellbook_minimum = 6 + max(0, class_level - 1) * 2

    return {
        "mode": mode,
        "ability": ability,
        "cantrips_known": cantrips,
        "spells_known": known[class_level - 1] if known else None,
        "prepared_limit": prepared,
        "spellbook_minimum": spellbook_minimum,
        "slots": slots,
        "pact_slot_level": pact_slot_level,
    }
