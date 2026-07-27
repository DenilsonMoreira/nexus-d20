import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models import AuditLog, Campaign, CampaignMember, Character, Session, User


@pytest.mark.asyncio
async def test_level_up_is_simulated_persisted_and_idempotent() -> None:
    suffix = uuid.uuid4()
    user_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    character_id: uuid.UUID | None = None
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        registered = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"progressao-{suffix}@example.com",
                "display_name": "Progressão",
                "password": "segredo-com-12-caracteres",
            },
        )
        assert registered.status_code == 201
        user_id = uuid.UUID(registered.json()["user"]["id"])
        campaign = await client.post(
            "/api/v1/campaigns", json={"name": "Progressão persistente"}
        )
        campaign_id = uuid.UUID(campaign.json()["id"])
        character = await client.post(
            f"/api/v1/campaigns/{campaign_id}/characters",
            json={
                "name": "Iria",
                "class_name": "Monge",
                "level": 1,
                "hit_points_current": 10,
                "hit_points_max": 10,
                "abilities": {
                    "strength": 10,
                    "dexterity": 16,
                    "constitution": 14,
                    "intelligence": 10,
                    "wisdom": 16,
                    "charisma": 10,
                },
            },
        )
        character_id = uuid.UUID(character.json()["id"])
        payload = {
            "target_class_id": "monk",
            "base_class_id": "monk",
            "hit_point_method": "fixed",
        }
        preview = await client.post(
            f"/api/v1/characters/{character_id}/level-up/simulate",
            json=payload,
        )
        assert preview.status_code == 200
        assert preview.json()["ready_to_apply"] is True
        assert preview.json()["resulting_level"] == 2

        headers = {"Idempotency-Key": str(uuid.uuid4())}
        applied = await client.post(
            f"/api/v1/characters/{character_id}/level-up/apply",
            json=payload,
            headers=headers,
        )
        repeated = await client.post(
            f"/api/v1/characters/{character_id}/level-up/apply",
            json=payload,
            headers=headers,
        )
        assert applied.status_code == repeated.status_code == 200
        assert applied.json()["event_id"] == repeated.json()["event_id"]
        state = await client.get(f"/api/v1/characters/{character_id}/progression")
        assert state.json()["total_level"] == 2
        assert state.json()["class_levels"] == [
            {"class_id": "monk", "level": 2, "subclass_id": None}
        ]

    async with SessionLocal() as db:
        if campaign_id:
            await db.execute(delete(AuditLog).where(AuditLog.campaign_id == campaign_id))
        if character_id:
            await db.execute(delete(Character).where(Character.id == character_id))
        if campaign_id:
            await db.execute(
                delete(CampaignMember).where(CampaignMember.campaign_id == campaign_id)
            )
            await db.execute(delete(Campaign).where(Campaign.id == campaign_id))
        if user_id:
            await db.execute(delete(Session).where(Session.user_id == user_id))
            await db.execute(delete(User).where(User.id == user_id))
        await db.commit()


@pytest.mark.asyncio
async def test_operational_headers_metrics_export_and_account_deletion() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        health = await client.get("/health")
        assert health.headers["x-request-id"]
        assert health.headers["x-content-type-options"] == "nosniff"
        metrics = await client.get("/metrics")
        assert metrics.status_code == 200
        assert "nexus_http_requests_total" in metrics.text

        registered = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"privacidade-{uuid.uuid4()}@example.com",
                "display_name": "Privacidade",
                "password": "segredo-com-12-caracteres",
            },
        )
        assert registered.status_code == 201
        exported = await client.get("/api/v1/account/export")
        assert exported.status_code == 200
        assert exported.json()["data"]["profile"]["display_name"] == "Privacidade"
        deleted = await client.request(
            "DELETE",
            "/api/v1/account",
            json={"confirmation": "EXCLUIR"},
        )
        assert deleted.status_code == 200
        assert (await client.get("/api/v1/account/export")).status_code == 401
