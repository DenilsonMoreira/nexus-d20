import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_class_progression_endpoint_simulates_without_mutation() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/rules/progression/classes/simulate",
            json={
                "class_id": "rogue",
                "current_class_level": 9,
                "constitution_modifier": 2,
                "hit_point_method": "rolled",
                "hit_die_roll": 6,
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "class_id": "rogue",
        "class_label": "Ladino",
        "current_class_level": 9,
        "next_class_level": 10,
        "hit_die_sides": 8,
        "fixed_hit_point_value": 5,
        "hit_point_method": "rolled",
        "hit_die_roll": 6,
        "constitution_modifier": 2,
        "hit_point_gain": 8,
        "ability_score_improvement_required": True,
        "required_choices": ["ability_score_improvement"],
        "class_level_cap": False,
    }


@pytest.mark.asyncio
async def test_class_progression_endpoint_rejects_roll_above_hit_die() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/rules/progression/classes/simulate",
            json={
                "class_id": "wizard",
                "current_class_level": 4,
                "constitution_modifier": 1,
                "hit_point_method": "rolled",
                "hit_die_roll": 7,
            },
        )

    assert response.status_code == 422
