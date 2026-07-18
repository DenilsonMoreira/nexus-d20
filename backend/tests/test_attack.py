from app.domain.rules.attack import resolve_attack


def test_normal_hit_wears_by_margin() -> None:
    result = resolve_attack({"natural_roll": 12, "attack_modifier": 5, "target_ac": 15})
    assert result["outcome"] == "hit"
    assert result["margin"] == 2
    assert result["attacker_weapon_wear"] == 2


def test_normal_miss_wears_by_margin() -> None:
    result = resolve_attack({"natural_roll": 6, "attack_modifier": 5, "target_ac": 15})
    assert result["outcome"] == "miss"
    assert result["attacker_weapon_wear"] == 4


def test_critical_miss_doubles_wear() -> None:
    result = resolve_attack({"natural_roll": 1, "attack_modifier": 5, "target_ac": 15})
    assert result["outcome"] == "critical_miss"
    assert result["margin"] == 9
    assert result["attacker_weapon_wear"] == 18


def test_critical_hit_does_not_wear_attacker() -> None:
    result = resolve_attack({"natural_roll": 20, "attack_modifier": 5, "target_ac": 16})
    assert result["outcome"] == "critical_hit"
    assert result["attacker_weapon_wear"] == 0
    assert result["suggested_target_equipment_wear"] == 18


def test_exact_ac_has_zero_wear() -> None:
    result = resolve_attack({"natural_roll": 10, "attack_modifier": 5, "target_ac": 15})
    assert result["outcome"] == "hit"
    assert result["margin"] == 0
