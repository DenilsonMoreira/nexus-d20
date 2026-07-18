from decimal import Decimal

from app.domain.rules.encumbrance import calculate_encumbrance


def test_strength_twelve_limits_in_kg() -> None:
    result = calculate_encumbrance(
        strength=12, current_weight_kg=Decimal("33.1"), base_speed_m=Decimal("9")
    )
    assert result["comfortable_limit_kg"] == Decimal("27.2")
    assert result["maximum_capacity_kg"] == Decimal("81.6")
    assert result["state"] == "encumbered"
    assert result["current_speed_m"] == Decimal("6.0")


def test_heavy_encumbrance_reduces_six_meters() -> None:
    result = calculate_encumbrance(
        strength=10, current_weight_kg=Decimal("50"), base_speed_m=Decimal("9")
    )
    assert result["state"] == "heavily_encumbered"
    assert result["current_speed_m"] == Decimal("3.0")
