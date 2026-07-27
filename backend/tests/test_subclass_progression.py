import pytest

from app.domain.rules.subclass_progression import (
    SRD_SUBCLASSES,
    simulate_subclass_choice,
)


def test_all_srd_subclasses_have_the_expected_choice_level() -> None:
    assert {
        class_id: (definition["id"], definition["choice_level"])
        for class_id, definition in SRD_SUBCLASSES.items()
    } == {
        "barbarian": ("path_of_the_berserker", 3),
        "bard": ("college_of_lore", 3),
        "cleric": ("life_domain", 1),
        "druid": ("circle_of_the_land", 2),
        "fighter": ("champion", 3),
        "monk": ("way_of_the_open_hand", 3),
        "paladin": ("oath_of_devotion", 3),
        "ranger": ("hunter", 3),
        "rogue": ("thief", 3),
        "sorcerer": ("draconic_bloodline", 1),
        "warlock": ("the_fiend", 1),
        "wizard": ("school_of_evocation", 2),
    }


def test_choice_is_not_available_before_the_class_level() -> None:
    result = simulate_subclass_choice(
        class_id="fighter",
        target_class_level=2,
    )

    assert result["choice_available"] is False
    assert result["selection_required"] is False
    assert result["selected_subclass_id"] is None


def test_choice_is_required_when_checkpoint_is_reached() -> None:
    result = simulate_subclass_choice(
        class_id="wizard",
        target_class_level=2,
    )

    assert result["choice_available"] is True
    assert result["selection_required"] is True
    assert result["available_subclasses"] == [
        {
            "id": "school_of_evocation",
            "label": "Escola de Evocação",
            "source": "srd_5_1",
        }
    ]


def test_level_one_subclass_is_required_immediately() -> None:
    result = simulate_subclass_choice(
        class_id="cleric",
        target_class_level=1,
    )

    assert result["choice_level"] == 1
    assert result["selection_required"] is True


def test_valid_selection_is_reflected_without_mutation() -> None:
    result = simulate_subclass_choice(
        class_id="rogue",
        target_class_level=3,
        selected_subclass_id="thief",
    )

    assert result["selection_required"] is False
    assert result["selected_subclass_id"] == "thief"
    assert result["selected_subclass_label"] == "Ladrão"


def test_subclass_from_another_class_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=r"A subclasse selecionada não pertence à classe informada\.",
    ):
        simulate_subclass_choice(
            class_id="fighter",
            target_class_level=3,
            selected_subclass_id="thief",
        )


def test_subclass_cannot_be_selected_early() -> None:
    with pytest.raises(
        ValueError,
        match=r"A subclasse não pode ser escolhida antes do nível previsto\.",
    ):
        simulate_subclass_choice(
            class_id="barbarian",
            target_class_level=2,
            selected_subclass_id="path_of_the_berserker",
        )
