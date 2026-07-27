import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.main import app
from app.models import (
    AuditLog,
    Campaign,
    CampaignMember,
    Character,
    Invite,
    Session,
    User,
)
from app.models.world import (
    Creature,
    DashboardLayout,
    Encounter,
    KnowledgeEdge,
    KnowledgeNode,
    LibraryEntry,
    Shop,
    ShopStock,
    TravelPlan,
)


@pytest.mark.asyncio
async def test_phases_seven_to_ten_acceptance_flow() -> None:
    suffix = uuid.uuid4()
    email = f"mestre-mundo-{suffix}@example.com"
    member_email = f"observador-mundo-{suffix}@example.com"
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    member = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    campaign_id: uuid.UUID | None = None
    try:
        registered = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "display_name": "Mestre do Mundo",
                "password": "segredo-com-12-caracteres",
            },
        )
        assert registered.status_code == 201
        campaign = await client.post(
            "/api/v1/campaigns", json={"name": "Marchas de Brumaverde"}
        )
        assert campaign.status_code == 201
        campaign_id = uuid.UUID(campaign.json()["id"])
        assert (
            await member.post(
                "/api/v1/auth/register",
                json={
                    "email": member_email,
                    "display_name": "Observador",
                    "password": "segredo-com-12-caracteres",
                },
            )
        ).status_code == 201
        invitation = await client.post(
            f"/api/v1/campaigns/{campaign_id}/invites",
            json={"email": member_email, "role": "observer"},
        )
        assert invitation.status_code == 201
        assert (
            await member.post(
                f"/api/v1/campaign-invites/{invitation.json()['token']}/accept"
            )
        ).status_code == 200

        original = await client.post(
            f"/api/v1/campaigns/{campaign_id}/library",
            json={
                "kind": "spell",
                "name": "Névoa Arcana",
                "description": "Uma névoa cobre o vale.",
                "data": {"damage": "1d6"},
            },
        )
        assert original.status_code == 201
        duplicate = await client.post(
            f"/api/v1/campaigns/{campaign_id}/library/"
            f"{original.json()['id']}/duplicate"
        )
        changed = await client.patch(
            f"/api/v1/campaigns/{campaign_id}/library/{duplicate.json()['id']}",
            json={"name": "Névoa Voraz", "data": {"damage": "1d8"}},
        )
        assert changed.status_code == 200
        library = (
            await client.get(f"/api/v1/campaigns/{campaign_id}/library")
        ).json()
        original_after = next(entry for entry in library if entry["id"] == original.json()["id"])
        copy_after = next(entry for entry in library if entry["id"] == duplicate.json()["id"])
        assert original_after["data"]["damage"] == "1d6"
        assert copy_after["data"]["damage"] == "1d8"
        assert copy_after["source_entry_id"] == original.json()["id"]

        shop = await client.post(
            f"/api/v1/campaigns/{campaign_id}/shops",
            json={"name": "Empório do Corvo", "owner_name": "Maela"},
        )
        stock = await client.put(
            f"/api/v1/campaigns/{campaign_id}/shops/{shop.json()['id']}/stock",
            json={
                "library_entry_id": copy_after["id"],
                "quantity": 3,
                "price_gp": "75.00",
            },
        )
        assert stock.status_code == 200
        secret_entry = await client.post(
            f"/api/v1/campaigns/{campaign_id}/library",
            json={
                "kind": "item",
                "name": "Adaga do Traidor",
                "is_secret": True,
            },
        )
        assert (
            await client.put(
                f"/api/v1/campaigns/{campaign_id}/shops/{shop.json()['id']}/stock",
                json={
                    "library_entry_id": secret_entry.json()["id"],
                    "quantity": 1,
                    "price_gp": "1.00",
                    "is_hidden": False,
                },
            )
        ).status_code == 200

        creature = await client.post(
            f"/api/v1/campaigns/{campaign_id}/creatures",
            json={
                "name": "Lobo de Névoa",
                "armor_class": 13,
                "hit_points": 18,
                "challenge_rating": "1",
                "encounter_weight": 5,
                "biomes": ["floresta"],
                "treasure": [{"name": "Presa opalescente"}],
                "data": {"visible": "pegadas", "gm_notes": "ataca ao anoitecer"},
            },
        )
        assert creature.status_code == 201
        creature_copy = await client.post(
            f"/api/v1/campaigns/{campaign_id}/creatures/"
            f"{creature.json()['id']}/duplicate"
        )
        assert (
            await client.patch(
                f"/api/v1/campaigns/{campaign_id}/creatures/"
                f"{creature_copy.json()['id']}",
                json={"name": "Lobo Alfa", "hit_points": 36},
            )
        ).status_code == 200
        encounter = await client.post(
            f"/api/v1/campaigns/{campaign_id}/encounters/generate",
            json={"biome": "floresta", "danger": 2, "seed": 19},
        )
        assert encounter.status_code == 201
        assert encounter.json()["difficulty_is_estimate"] is True
        adjusted = await client.patch(
            f"/api/v1/campaigns/{campaign_id}/encounters/{encounter.json()['id']}",
            json={
                "estimated_difficulty": "hard",
                "status": "active",
                "history_entry": {"event": "combat_started"},
            },
        )
        assert adjusted.json()["status"] == "active"
        assert adjusted.json()["estimated_difficulty"] == "hard"

        character = await client.post(
            f"/api/v1/campaigns/{campaign_id}/characters",
            json={
                "name": "Ariane",
                "speed_meters": 9,
                "abilities": {"strength": 10},
            },
        )
        assert character.status_code == 201
        travel = await client.post(
            f"/api/v1/campaigns/{campaign_id}/travel-plans",
            json={
                "name": "Travessia das Ruínas",
                "origin": "Brumaverde",
                "destination": "Ruínas Élficas",
                "distance_km": "80",
                "pace": "fast",
                "difficult_terrain": True,
                "severe_weather": True,
                "hidden_fatigue_enabled": True,
                "traveler_ids": [character.json()["id"]],
                "travel_hours_per_day": 9,
            },
        )
        assert travel.status_code == 201
        assert travel.json()["distance_km"] == "80.0"
        assert travel.json()["forced_march_checks"][0]["constitution_save_dc"] == 11
        assert travel.json()["hidden_fatigue_dc"] == 14
        assert travel.json()["loads"][character.json()["id"]]["state"] == "comfortable"

        public_node = await client.post(
            f"/api/v1/campaigns/{campaign_id}/knowledge/nodes",
            json={
                "node_type": "clue",
                "title": "Símbolos antigos",
                "occurred_at": "2026-07-27T18:00:00Z",
            },
        )
        secret_node = await client.post(
            f"/api/v1/campaigns/{campaign_id}/knowledge/nodes",
            json={
                "node_type": "secret",
                "title": "O regente é o traidor",
                "is_secret": True,
                "data": {"secret": "identidade"},
            },
        )
        assert public_node.status_code == secret_node.status_code == 201

        dashboard = await client.post(
            f"/api/v1/campaigns/{campaign_id}/dashboards",
            json={
                "name": "Exploração pública",
                "template_code": "exploration",
                "visibility": "presentation",
                "cards": [
                    {"title": "Pista", "content": "Pegadas na lama"},
                    {
                        "title": "Segredo do mestre",
                        "is_secret": True,
                        "secret": "O traidor acompanha o grupo",
                    },
                ],
            },
        )
        assert dashboard.status_code == 201
        member_library = (
            await member.get(f"/api/v1/campaigns/{campaign_id}/library")
        ).json()
        assert "Adaga do Traidor" not in str(member_library)
        member_shops = (
            await member.get(f"/api/v1/campaigns/{campaign_id}/shops")
        ).json()
        assert "Adaga do Traidor" not in str(member_shops)
        member_creatures = (
            await member.get(f"/api/v1/campaigns/{campaign_id}/creatures")
        ).json()
        assert member_creatures[0]["data"] == {"visible": "pegadas"}
        member_dashboards = (
            await member.get(f"/api/v1/campaigns/{campaign_id}/dashboards")
        ).json()
        assert "Segredo do mestre" not in str(member_dashboards)
        public_client = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        )
        try:
            presentation = await public_client.get(
                f"/api/v1/presentations/{dashboard.json()['id']}"
            )
        finally:
            await public_client.aclose()
        assert presentation.status_code == 200
        serialized = str(presentation.json())
        assert "Pista" in serialized
        assert "Segredo do mestre" not in serialized
        assert "traidor acompanha" not in serialized
    finally:
        await client.aclose()
        await member.aclose()
        async with SessionLocal() as db:
            users = list(
                (
                    await db.scalars(
                        select(User).where(User.email.in_([email, member_email]))
                    )
                ).all()
            )
            if campaign_id is not None:
                await db.execute(
                    delete(ShopStock).where(
                        ShopStock.shop_id.in_(
                            select(Shop.id).where(Shop.campaign_id == campaign_id)
                        )
                    )
                )
                for model in (
                    KnowledgeEdge,
                    KnowledgeNode,
                    Shop,
                    LibraryEntry,
                    Encounter,
                    Creature,
                    TravelPlan,
                    DashboardLayout,
                    AuditLog,
                    Character,
                    Invite,
                    CampaignMember,
                ):
                    await db.execute(delete(model).where(model.campaign_id == campaign_id))
                await db.execute(delete(Campaign).where(Campaign.id == campaign_id))
            user_ids = [user.id for user in users]
            if user_ids:
                await db.execute(delete(Session).where(Session.user_id.in_(user_ids)))
                await db.execute(delete(User).where(User.id.in_(user_ids)))
            await db.commit()
