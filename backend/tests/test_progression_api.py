import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_progression_endpoint_is_a_pure_simulation() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/rules/progression/simulate",
            json={"current_level": 8, "experience_points": 48_000},
        )

    assert response.status_code == 200
    assert response.json() == {
        "current": {
            "level": 8,
            "experience_threshold": 34_000,
            "proficiency_bonus": 3,
        },
        "next": {
            "level": 9,
            "experience_threshold": 48_000,
            "proficiency_bonus": 4,
        },
        "experience_points": 48_000,
        "highest_level_by_experience": 9,
        "experience_remaining": 0,
        "qualification": "eligible",
    }
