import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.main import app
from app.models import AuditLog, Campaign, CampaignMember, Invite, Session, User


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


@pytest.mark.asyncio
async def test_campaign_membership_enforces_tenant_isolation() -> None:
    suffix = uuid.uuid4()
    master_email = f"mestre-{suffix}@example.com"
    player_email = f"jogador-{suffix}@example.com"
    outsider_email = f"intruso-{suffix}@example.com"
    clients: list[AsyncClient] = []
    campaign_id: uuid.UUID | None = None

    try:
        master = await register_client(master_email, "Mestre")
        player = await register_client(player_email, "Jogador")
        outsider = await register_client(outsider_email, "Intruso")
        clients.extend([master, player, outsider])

        created = await master.post("/api/v1/campaigns", json={"name": "Sombras de Esterien"})
        assert created.status_code == 201
        campaign_id = uuid.UUID(created.json()["id"])
        assert created.json()["role"] == "master"

        hidden = await outsider.get(f"/api/v1/campaigns/{campaign_id}")
        assert hidden.status_code == 404
        assert hidden.json()["error"]["code"] == "campaign_not_found"

        outsider_list = await outsider.get("/api/v1/campaigns")
        assert outsider_list.status_code == 200
        assert outsider_list.json()["items"] == []

        invitation = await master.post(
            f"/api/v1/campaigns/{campaign_id}/invites",
            json={"email": player_email, "role": "player"},
        )
        assert invitation.status_code == 201
        token = invitation.json()["token"]

        wrong_recipient = await outsider.post(f"/api/v1/campaign-invites/{token}/accept")
        assert wrong_recipient.status_code == 404
        assert wrong_recipient.json()["error"]["code"] == "invite_not_found"

        accepted = await player.post(f"/api/v1/campaign-invites/{token}/accept")
        assert accepted.status_code == 200
        assert accepted.json()["campaign"]["role"] == "player"

        visible = await player.get(f"/api/v1/campaigns/{campaign_id}")
        assert visible.status_code == 200
        assert visible.json()["name"] == "Sombras de Esterien"

        forbidden = await player.post(
            f"/api/v1/campaigns/{campaign_id}/invites",
            json={"email": outsider_email, "role": "observer"},
        )
        assert forbidden.status_code == 403
        assert forbidden.json()["error"]["code"] == "master_role_required"

        members = await master.get(f"/api/v1/campaigns/{campaign_id}/members")
        assert members.status_code == 200
        player_member = next(
            item for item in members.json()["items"] if item["email"] == player_email
        )
        player_id = player_member["user_id"]

        changed_role = await master.patch(
            f"/api/v1/campaigns/{campaign_id}/members/{player_id}",
            json={"role": "observer"},
        )
        assert changed_role.status_code == 200
        assert changed_role.json()["role"] == "observer"
        assert (await player.get(f"/api/v1/campaigns/{campaign_id}")).json()["role"] == "observer"

        audit_list = await master.get(f"/api/v1/campaigns/{campaign_id}/audit")
        assert audit_list.status_code == 200
        assert audit_list.json()["items"]
        assert (await player.get(f"/api/v1/campaigns/{campaign_id}/audit")).status_code == 403

        creation_audit = next(
            item for item in audit_list.json()["items"] if item["action"] == "campaign.created"
        )
        unsafe_reversal = await master.post(
            f"/api/v1/campaign-audits/{creation_audit['id']}/reverse",
            json={"reason": "Operação sem inversão segura"},
        )
        assert unsafe_reversal.status_code == 409
        assert unsafe_reversal.json()["error"]["code"] == "audit_not_reversible"

        removed = await master.delete(
            f"/api/v1/campaigns/{campaign_id}/members/{player_id}"
        )
        assert removed.status_code == 204
        assert (await player.get(f"/api/v1/campaigns/{campaign_id}")).status_code == 404

        archived = await master.delete(f"/api/v1/campaigns/{campaign_id}")
        assert archived.status_code == 204
        assert (await master.get(f"/api/v1/campaigns/{campaign_id}")).status_code == 404
        assert (await player.get(f"/api/v1/campaigns/{campaign_id}")).status_code == 404

        async with SessionLocal() as db:
            archived_audit_id = await db.scalar(
                select(AuditLog.id).where(
                    AuditLog.campaign_id == campaign_id,
                    AuditLog.action == "campaign.archived",
                )
            )
        assert archived_audit_id is not None

        hidden_audit = await outsider.post(
            f"/api/v1/campaign-audits/{archived_audit_id}/reverse",
            json={"reason": "Tentativa externa"},
        )
        assert hidden_audit.status_code == 404

        reversed_audit = await master.post(
            f"/api/v1/campaign-audits/{archived_audit_id}/reverse",
            json={"reason": "Campanha arquivada por engano"},
        )
        assert reversed_audit.status_code == 200
        assert reversed_audit.json()["reversal_of_id"] == str(archived_audit_id)
        assert reversed_audit.json()["reason"] == "Campanha arquivada por engano"
        assert (await master.get(f"/api/v1/campaigns/{campaign_id}")).status_code == 200

        duplicate_reversal = await master.post(
            f"/api/v1/campaign-audits/{archived_audit_id}/reverse",
            json={"reason": "Segunda tentativa de reversão"},
        )
        assert duplicate_reversal.status_code == 409
        assert duplicate_reversal.json()["error"]["code"] == "audit_already_reversed"

        async with SessionLocal() as db:
            actions = set(
                (
                    await db.scalars(
                        select(AuditLog.action).where(AuditLog.campaign_id == campaign_id)
                    )
                ).all()
            )
        assert {
            "campaign.created",
            "invite.created",
            "invite.accepted",
            "campaign_member.role_updated",
            "campaign_member.removed",
            "campaign.archived",
            "campaign.archived.reversed",
        }.issubset(actions)
    finally:
        for client in clients:
            await client.aclose()
        async with SessionLocal() as db:
            user_ids = list(
                (
                    await db.scalars(
                        select(User.id).where(
                            User.email.in_([master_email, player_email, outsider_email])
                        )
                    )
                ).all()
            )
            if campaign_id is not None:
                await db.execute(delete(AuditLog).where(AuditLog.campaign_id == campaign_id))
                await db.execute(delete(Invite).where(Invite.campaign_id == campaign_id))
                await db.execute(
                    delete(CampaignMember).where(CampaignMember.campaign_id == campaign_id)
                )
                await db.execute(delete(Campaign).where(Campaign.id == campaign_id))
            if user_ids:
                await db.execute(delete(Session).where(Session.user_id.in_(user_ids)))
                await db.execute(delete(User).where(User.id.in_(user_ids)))
            await db.commit()


@pytest.mark.asyncio
async def test_campaigns_require_authentication() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/campaigns")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"
