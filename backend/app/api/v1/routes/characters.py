import uuid

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.dependencies import CampaignAccessDependency, CurrentUser, DatabaseSession
from app.core.errors import AppError
from app.models import CampaignMember, Character
from app.schemas.characters import (
    CharacterCreateRequest,
    CharacterListResponse,
    CharacterResponse,
    CharacterUpdateRequest,
)
from app.services.audit import record_audit
from app.services.characters import (
    character_response,
    character_snapshot,
    get_visible_character,
)

campaign_router = APIRouter()
router = APIRouter()


@campaign_router.post(
    "/{campaign_id}/characters",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_character(
    payload: CharacterCreateRequest,
    access: CampaignAccessDependency,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CharacterResponse:
    if access.member.role == "observer":
        raise AppError(403, "character_write_forbidden", "Observadores não editam fichas.")
    owner_user_id = payload.owner_user_id or current_user.id
    if access.member.role != "master" and owner_user_id != current_user.id:
        raise AppError(403, "character_write_forbidden", "Você não pode atribuir esta ficha.")
    owner_role = await db.scalar(
        select(CampaignMember.role).where(
            CampaignMember.campaign_id == access.campaign.id,
            CampaignMember.user_id == owner_user_id,
        )
    )
    if owner_role not in {"master", "player"}:
        raise AppError(
            422,
            "character_owner_invalid",
            "O responsável pela ficha deve ser mestre ou jogador da campanha.",
        )

    values = payload.model_dump(exclude={"abilities", "owner_user_id"})
    values.update(payload.abilities.model_dump())
    for field in (
        "name",
        "race_name",
        "class_name",
        "subclass_name",
        "background",
        "alignment",
    ):
        values[field] = values[field].strip()
    character = Character(
        campaign_id=access.campaign.id,
        owner_user_id=owner_user_id,
        **values,
    )
    db.add(character)
    await db.flush()
    record_audit(
        db,
        campaign_id=access.campaign.id,
        actor_user_id=current_user.id,
        entity_type="character",
        entity_id=character.id,
        action="character.created",
        after_data=character_snapshot(character),
    )
    await db.commit()
    await db.refresh(character)
    return character_response(character)


@campaign_router.get(
    "/{campaign_id}/characters",
    response_model=CharacterListResponse,
)
async def list_characters(
    access: CampaignAccessDependency,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CharacterListResponse:
    if access.member.role == "observer":
        return CharacterListResponse(items=[])
    query = select(Character).where(Character.campaign_id == access.campaign.id)
    if access.member.role != "master":
        query = query.where(Character.owner_user_id == current_user.id)
    characters = list(
        (await db.scalars(query.order_by(Character.created_at, Character.id))).all()
    )
    return CharacterListResponse(items=[character_response(item) for item in characters])


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: uuid.UUID,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CharacterResponse:
    character, _ = await get_visible_character(
        db, character_id=character_id, user_id=current_user.id
    )
    return character_response(character)


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: uuid.UUID,
    payload: CharacterUpdateRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> CharacterResponse:
    character, role = await get_visible_character(
        db, character_id=character_id, user_id=current_user.id
    )
    if role == "observer":
        raise AppError(403, "character_write_forbidden", "Observadores não editam fichas.")

    before = character_snapshot(character)
    changes = payload.model_dump(exclude_unset=True, exclude={"abilities", "reason"})
    for field, value in changes.items():
        setattr(character, field, value.strip() if isinstance(value, str) else value)
    if payload.abilities is not None:
        ability_changes = payload.abilities.model_dump(exclude_unset=True)
        for field, value in ability_changes.items():
            setattr(character, field, value)
    if character.hit_points_current > character.hit_points_max:
        raise AppError(
            422,
            "character_hit_points_invalid",
            "PV atuais não podem superar os PV máximos.",
        )
    after = character_snapshot(character)
    if after != before:
        record_audit(
            db,
            campaign_id=character.campaign_id,
            actor_user_id=current_user.id,
            entity_type="character",
            entity_id=character.id,
            action="character.updated",
            before_data=before,
            after_data=after,
            reason=payload.reason.strip() if payload.reason else None,
        )
    await db.commit()
    await db.refresh(character)
    return character_response(character)
