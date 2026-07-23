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


async def register_client(email: str, display_name: str) -> AsyncClient:
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "display_name": display_name,
            "password": "segredo-com-12-caracteres",
        },
    )
    assert response.status_code == 201
    return client


async def invite_and_accept(
    master: AsyncClient,
    member: AsyncClient,
    campaign_id: uuid.UUID,
    email: str,
    role: str,
) -> None:
    invitation = await master.post(
        f"/api/v1/campaigns/{campaign_id}/invites",
        json={"email": email, "role": role},
    )
    assert invitation.status_code == 201
    accepted = await member.post(
        f"/api/v1/campaign-invites/{invitation.json()['token']}/accept"
    )
    assert accepted.status_code == 200


@pytest.mark.asyncio
async def test_character_sheet_is_persisted_audited_and_tenant_safe() -> None:
    suffix = uuid.uuid4()
    emails = {
        "master": f"mestre-ficha-{suffix}@example.com",
        "player": f"jogador-ficha-{suffix}@example.com",
        "observer": f"observador-ficha-{suffix}@example.com",
        "outsider": f"intruso-ficha-{suffix}@example.com",
    }
    clients: list[AsyncClient] = []
    campaign_id: uuid.UUID | None = None

    try:
        master = await register_client(emails["master"], "Mestre")
        player = await register_client(emails["player"], "Jogador")
        observer = await register_client(emails["observer"], "Observador")
        outsider = await register_client(emails["outsider"], "Intruso")
        clients.extend([master, player, observer, outsider])

        created_campaign = await master.post(
            "/api/v1/campaigns", json={"name": "Ecos da Ficha"}
        )
        assert created_campaign.status_code == 201
        campaign_id = uuid.UUID(created_campaign.json()["id"])
        await invite_and_accept(
            master, player, campaign_id, emails["player"], "player"
        )
        await invite_and_accept(
            master, observer, campaign_id, emails["observer"], "observer"
        )

        created = await player.post(
            f"/api/v1/campaigns/{campaign_id}/characters",
            json={
                "name": "Nox Brasalume",
                "race_name": "Humano variante",
                "class_name": "Monge",
                "level": 2,
                "hit_points_current": 17,
                "hit_points_max": 17,
                "armor_class": 16,
                "speed_meters": 9,
                "abilities": {
                    "strength": 12,
                    "dexterity": 16,
                    "constitution": 14,
                    "intelligence": 10,
                    "wisdom": 15,
                    "charisma": 8,
                },
            },
        )
        assert created.status_code == 201
        character_id = uuid.UUID(created.json()["id"])
        modifiers = {
            ability["code"]: ability["modifier"]
            for ability in created.json()["abilities"]
        }
        assert modifiers == {
            "strength": 1,
            "dexterity": 3,
            "constitution": 2,
            "intelligence": 0,
            "wisdom": 2,
            "charisma": -1,
        }

        assert (await master.get(f"/api/v1/characters/{character_id}")).status_code == 200
        assert (await outsider.get(f"/api/v1/characters/{character_id}")).status_code == 404
        assert (await observer.get(f"/api/v1/characters/{character_id}")).status_code == 404
        assert (
            await outsider.get(f"/api/v1/campaigns/{campaign_id}/characters")
        ).status_code == 404
        observer_list = await observer.get(
            f"/api/v1/campaigns/{campaign_id}/characters"
        )
        assert observer_list.status_code == 200
        assert observer_list.json()["items"] == []

        observer_create = await observer.post(
            f"/api/v1/campaigns/{campaign_id}/characters",
            json={"name": "Ficha indevida"},
        )
        assert observer_create.status_code == 403
        assert observer_create.json()["error"]["code"] == "character_write_forbidden"

        partial_ability_update = await player.patch(
            f"/api/v1/characters/{character_id}",
            json={"abilities": {"strength": 13}},
        )
        assert partial_ability_update.status_code == 200
        updated_scores = {
            ability["code"]: ability["score"]
            for ability in partial_ability_update.json()["abilities"]
        }
        assert updated_scores["strength"] == 13
        assert updated_scores["dexterity"] == 16

        updated = await master.patch(
            f"/api/v1/characters/{character_id}",
            json={
                "hit_points_current": 12,
                "reason": "Dano recebido durante a sessão",
            },
        )
        assert updated.status_code == 200
        assert updated.json()["hit_points_current"] == 12

        invalid_hp = await player.patch(
            f"/api/v1/characters/{character_id}",
            json={"hit_points_current": 18},
        )
        assert invalid_hp.status_code == 422
        assert invalid_hp.json()["error"]["code"] == "character_hit_points_invalid"

        async with SessionLocal() as db:
            audits = list(
                (
                    await db.scalars(
                        select(AuditLog)
                        .where(
                            AuditLog.campaign_id == campaign_id,
                            AuditLog.entity_id == character_id,
                        )
                        .order_by(AuditLog.created_at)
                    )
                ).all()
            )
        assert [audit.action for audit in audits] == [
            "character.created",
            "character.updated",
            "character.updated",
        ]
        assert audits[-1].reason == "Dano recebido durante a sessão"
        assert audits[-1].before_data["hit_points_current"] == 17
        assert audits[-1].after_data["hit_points_current"] == 12
    finally:
        for client in clients:
            await client.aclose()
        async with SessionLocal() as db:
            user_ids = list(
                (
                    await db.scalars(select(User.id).where(User.email.in_(emails.values())))
                ).all()
            )
            if campaign_id is not None:
                await db.execute(delete(AuditLog).where(AuditLog.campaign_id == campaign_id))
                await db.execute(delete(Character).where(Character.campaign_id == campaign_id))
                await db.execute(delete(Invite).where(Invite.campaign_id == campaign_id))
                await db.execute(
                    delete(CampaignMember).where(CampaignMember.campaign_id == campaign_id)
                )
                await db.execute(delete(Campaign).where(Campaign.id == campaign_id))
            if user_ids:
                await db.execute(delete(Session).where(Session.user_id.in_(user_ids)))
                await db.execute(delete(User).where(User.id.in_(user_ids)))
            await db.commit()
