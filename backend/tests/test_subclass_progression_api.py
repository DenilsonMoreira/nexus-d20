import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_subclass_progression_endpoint_reports_required_choice() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/rules/progression/subclasses/simulate",
            json={
                "class_id": "paladin",
                "target_class_level": 3,
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "class_id": "paladin",
        "class_label": "Paladino",
        "target_class_level": 3,
        "choice_level": 3,
        "choice_available": True,
        "selection_required": True,
        "selected_subclass_id": None,
        "selected_subclass_label": None,
        "available_subclasses": [
            {
                "id": "oath_of_devotion",
                "label": "Juramento de Devoção",
                "source": "srd_5_1",
            }
        ],
    }


@pytest.mark.asyncio
async def test_subclass_progression_endpoint_rejects_cross_class_selection() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/rules/progression/subclasses/simulate",
            json={
                "class_id": "druid",
                "target_class_level": 2,
                "selected_subclass_id": "champion",
            },
        )

    assert response.status_code == 422
