import pytest

from app.domain.rules.class_progression import CLASS_DEFINITIONS
from app.domain.rules.multiclass import validate_multiclass
from app.domain.rules.spellcasting import spellcasting_profile
from app.models import Character
from app.schemas.progression import LevelUpRequest
from app.services.progression import simulate_character_level_up


@pytest.mark.parametrize("class_id", CLASS_DEFINITIONS)
def test_every_srd_class_has_a_level_up_and_spellcasting_profile(class_id: str) -> None:
    character = Character(
        name="Teste",
        level=1,
        hit_points_current=10,
        hit_points_max=10,
        strength=16,
        dexterity=16,
        constitution=14,
        intelligence=16,
        wisdom=16,
        charisma=16,
    )
    character.class_levels = []
    character.spells = []
    character.spell_slots = []
    result = simulate_character_level_up(
        character,
        LevelUpRequest(
            target_class_id=class_id,  # type: ignore[arg-type]
            base_class_id=class_id,  # type: ignore[arg-type]
            hit_point_method="fixed",
        ),
    )
    assert result["resulting_level"] == 2
    assert result["target_class_level"] == 2
    assert result["hit_point_gain"] >= 1
    assert result["spellcasting"]["mode"] in {
        "none",
        "known",
        "prepared",
        "spellbook",
        "pact",
    }


def test_multiclass_requires_both_current_and_target_class_abilities() -> None:
    result = validate_multiclass(
        current_classes=["paladin"],
        target_class="monk",
        ability_scores={
            "strength": 13,
            "dexterity": 12,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 13,
            "charisma": 12,
        },
    )
    assert result["allowed"] is False
    assert result["unmet_requirements"] == [
        "paladin: charisma 13",
        "monk: dexterity 13",
    ]


def test_spellcasting_covers_known_prepared_spellbook_cantrips_and_slots() -> None:
    bard = spellcasting_profile(class_id="bard", class_level=5, ability_modifier=3)
    cleric = spellcasting_profile(class_id="cleric", class_level=5, ability_modifier=3)
    wizard = spellcasting_profile(class_id="wizard", class_level=5, ability_modifier=4)
    warlock = spellcasting_profile(class_id="warlock", class_level=5, ability_modifier=3)

    assert bard["spells_known"] == 8
    assert bard["cantrips_known"] == 3
    assert cleric["prepared_limit"] == 8
    assert wizard["spellbook_minimum"] == 14
    assert wizard["prepared_limit"] == 9
    assert warlock["slots"] == {3: 2}
    assert warlock["pact_slot_level"] == 3


def test_level_up_requires_simulation_choices_before_apply() -> None:
    character = Character(
        name="Teste",
        level=3,
        hit_points_current=20,
        hit_points_max=20,
        strength=10,
        dexterity=16,
        constitution=14,
        intelligence=10,
        wisdom=16,
        charisma=10,
    )
    character.class_levels = []
    character.spells = []
    character.spell_slots = []
    result = simulate_character_level_up(
        character,
        LevelUpRequest(target_class_id="monk", base_class_id="monk"),
    )
    assert result["ready_to_apply"] is False
    assert result["required_choices"] == [
        "ability_score_improvement",
        "hit_points",
        "subclass",
    ]
