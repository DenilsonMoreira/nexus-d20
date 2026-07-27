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
    Invite,
    MediaAsset,
    Note,
    NoteLink,
    Session,
    User,
)


async def register(email: str, name: str) -> AsyncClient:
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "display_name": name,
            "password": "segredo-com-12-caracteres",
        },
    )
    assert response.status_code == 201
    return client


@pytest.mark.asyncio
async def test_private_and_shared_notes_enforce_owner_boundary() -> None:
    suffix = uuid.uuid4()
    master_email = f"mestre-notas-{suffix}@example.com"
    player_email = f"jogador-notas-{suffix}@example.com"
    clients: list[AsyncClient] = []
    campaign_id: uuid.UUID | None = None
    try:
        master = await register(master_email, "Mestre")
        player = await register(player_email, "Jogador")
        clients.extend([master, player])
        campaign = await master.post(
            "/api/v1/campaigns", json={"name": "Segredos de Brumaverde"}
        )
        campaign_id = uuid.UUID(campaign.json()["id"])
        invitation = await master.post(
            f"/api/v1/campaigns/{campaign_id}/invites",
            json={"email": player_email, "role": "player"},
        )
        accepted = await player.post(
            f"/api/v1/campaign-invites/{invitation.json()['token']}/accept"
        )
        assert accepted.status_code == 200

        private_note = await player.post(
            f"/api/v1/campaigns/{campaign_id}/notes",
            json={"title": "Segredo", "body": "Só meu", "visibility": "private"},
        )
        assert private_note.status_code == 201
        note_id = private_note.json()["id"]
        master_list = await master.get(f"/api/v1/campaigns/{campaign_id}/notes")
        assert master_list.status_code == 200
        assert master_list.json() == []
        assert (await master.get(f"/api/v1/notes/{note_id}")).status_code == 404

        shared = await player.patch(
            f"/api/v1/notes/{note_id}", json={"visibility": "shared"}
        )
        assert shared.status_code == 200
        master_list = await master.get(f"/api/v1/campaigns/{campaign_id}/notes")
        assert [note["id"] for note in master_list.json()] == [note_id]
        forbidden_edit = await master.patch(
            f"/api/v1/notes/{note_id}", json={"body": "Alterado pelo mestre"}
        )
        assert forbidden_edit.status_code == 404
    finally:
        for client in clients:
            await client.aclose()
        async with SessionLocal() as db:
            users = list(
                (
                    await db.scalars(
                        select(User).where(User.email.in_([master_email, player_email]))
                    )
                ).all()
            )
            user_ids = [user.id for user in users]
            if campaign_id is not None:
                note_ids = list(
                    (
                        await db.scalars(
                            select(Note.id).where(Note.campaign_id == campaign_id)
                        )
                    ).all()
                )
                if note_ids:
                    await db.execute(
                        delete(MediaAsset).where(MediaAsset.note_id.in_(note_ids))
                    )
                    await db.execute(
                        delete(NoteLink).where(NoteLink.note_id.in_(note_ids))
                    )
                    await db.execute(delete(Note).where(Note.id.in_(note_ids)))
                await db.execute(
                    delete(AuditLog).where(AuditLog.campaign_id == campaign_id)
                )
                await db.execute(
                    delete(Invite).where(Invite.campaign_id == campaign_id)
                )
                await db.execute(
                    delete(CampaignMember).where(
                        CampaignMember.campaign_id == campaign_id
                    )
                )
                await db.execute(
                    delete(Campaign).where(Campaign.id == campaign_id)
                )
            if user_ids:
                await db.execute(delete(Session).where(Session.user_id.in_(user_ids)))
                await db.execute(delete(User).where(User.id.in_(user_ids)))
            await db.commit()
