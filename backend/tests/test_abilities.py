from app.domain.rules.abilities import ability_modifier


def test_ability_modifier_uses_2014_floor_rule() -> None:
    assert ability_modifier(8) == -1
    assert ability_modifier(9) == -1
    assert ability_modifier(10) == 0
    assert ability_modifier(16) == 3
