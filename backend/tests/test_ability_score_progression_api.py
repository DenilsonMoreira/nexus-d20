import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_ability_score_progression_endpoint_returns_before_and_after() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/rules/progression/ability-scores/simulate",
            json={
                "current_scores": {
                    "strength": 12,
                    "dexterity": 16,
                    "constitution": 17,
                    "intelligence": 10,
                    "wisdom": 14,
                    "charisma": 8,
                },
                "increases": {"constitution": 1, "charisma": 1},
                "resulting_character_level": 8,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["before"]["constitution"] == 17
    assert payload["after"]["constitution"] == 18
    assert payload["after"]["charisma"] == 9
    assert payload["modifiers_before"]["constitution"] == 3
    assert payload["modifiers_after"]["constitution"] == 4
    assert payload["constitution_modifier_change"] == 1
    assert payload["hit_point_maximum_adjustment"] == 8


@pytest.mark.asyncio
async def test_ability_score_progression_endpoint_rejects_invalid_distribution() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/rules/progression/ability-scores/simulate",
            json={
                "current_scores": {
                    "strength": 12,
                    "dexterity": 16,
                    "constitution": 14,
                    "intelligence": 10,
                    "wisdom": 14,
                    "charisma": 8,
                },
                "increases": {"strength": 1},
                "resulting_character_level": 4,
            },
        )

    assert response.status_code == 422
