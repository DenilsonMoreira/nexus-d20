from app.domain.rules.rest import simulate_long_rest


def test_long_rest_restores_resources_and_magic_item() -> None:
    result = simulate_long_rest(
        {
            "hit_points_current": 8,
            "hit_points_maximum": 17,
            "spell_slots_current": {"1": 1},
            "spell_slots_maximum": {"1": 4},
            "resources_current": {"ki": 0},
            "resources_maximum": {"ki": 2},
            "long_rest_resource_keys": ["ki"],
            "hit_dice_current": 0,
            "hit_dice_maximum": 2,
            "exhaustion_level": 1,
            "hidden_fatigue": 2,
            "magic_items": [
                {
                    "name": "Espada Arcana",
                    "current_points": 700,
                    "maximum_points": 1000,
                    "auto_repair_percent": 5,
                }
            ],
        }
    )
    assert result["hit_points_after"] == 17
    assert result["spell_slots_after"] == {"1": 4}
    assert result["resources_after"]["ki"] == 2
    assert result["hit_dice_after"] == 1
    assert result["exhaustion_after"] == 0
    assert result["hidden_fatigue_after"] == 0
    assert result["magic_items"][0]["current_points_after"] == 750


def test_antimagic_blocks_auto_repair() -> None:
    result = simulate_long_rest(
        {
            "hit_points_current": 10,
            "hit_points_maximum": 10,
            "antimagic_zone": True,
            "magic_items": [
                {
                    "name": "Espada Arcana",
                    "current_points": 700,
                    "maximum_points": 1000,
                    "auto_repair_percent": 5,
                }
            ],
        }
    )
    assert result["magic_items"][0]["current_points_after"] == 700
