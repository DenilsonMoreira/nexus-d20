from fastapi import APIRouter

from app.api.v1.routes import (
    audits,
    auth,
    campaigns,
    characters,
    inventory,
    master,
    notes,
    rules,
    world,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(audits.router, prefix="/campaign-audits", tags=["audit"])
api_router.include_router(
    campaigns.invite_router, prefix="/campaign-invites", tags=["campaigns"]
)
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(
    characters.campaign_router, prefix="/campaigns", tags=["characters"]
)
api_router.include_router(characters.router, prefix="/characters", tags=["characters"])
api_router.include_router(inventory.campaign_router, prefix="/campaigns", tags=["inventory"])
api_router.include_router(inventory.character_router, prefix="/characters", tags=["inventory"])
api_router.include_router(inventory.router, prefix="/items", tags=["inventory"])
api_router.include_router(notes.campaign_router, prefix="/campaigns", tags=["notes"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(master.campaign_router, prefix="/campaigns", tags=["master"])
api_router.include_router(master.character_router, prefix="/characters", tags=["master"])
api_router.include_router(world.campaign_router, prefix="/campaigns", tags=["world"])
api_router.include_router(
    world.presentation_router, prefix="/presentations", tags=["presentations"]
)
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
