import asyncio
import uuid
from pathlib import Path

from fastapi import APIRouter, Response, status
from sqlalchemy import delete, or_, select

from app.api.dependencies import CampaignAccessDependency, CurrentUser, DatabaseSession
from app.core.config import settings
from app.core.errors import AppError
from app.models import MediaAsset, Note, NoteLink
from app.schemas.notes import (
    MediaDownloadResponse,
    MediaUploadRequest,
    MediaUploadResponse,
    NoteCreate,
    NoteResponse,
    NoteUpdate,
)
from app.services.storage import delete_object, presigned_download, presigned_upload

campaign_router = APIRouter()
router = APIRouter()


async def accessible_note(
    db: DatabaseSession, note_id: uuid.UUID, user_id: uuid.UUID
) -> Note:
    note = await db.scalar(
        select(Note).where(
            Note.id == note_id,
            or_(Note.owner_user_id == user_id, Note.visibility == "shared"),
        )
    )
    if note is None:
        raise AppError(404, "note_not_found", "Nota não encontrada.")
    return note


async def note_response(db: DatabaseSession, note: Note) -> dict[str, object]:
    links = list(
        (
            await db.scalars(
                select(NoteLink)
                .where(NoteLink.note_id == note.id)
                .order_by(NoteLink.entity_type)
            )
        ).all()
    )
    media = list(
        (
            await db.scalars(
                select(MediaAsset)
                .where(MediaAsset.note_id == note.id)
                .order_by(MediaAsset.created_at)
            )
        ).all()
    )
    return {
        "id": note.id,
        "campaign_id": note.campaign_id,
        "owner_user_id": note.owner_user_id,
        "title": note.title,
        "body": note.body,
        "visibility": note.visibility,
        "links": links,
        "media": media,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }


@campaign_router.post(
    "/{campaign_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED
)
async def create_note(
    payload: NoteCreate,
    access: CampaignAccessDependency,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    note = Note(
        campaign_id=access.campaign.id,
        owner_user_id=current_user.id,
        title=payload.title,
        body=payload.body,
        visibility=payload.visibility,
    )
    db.add(note)
    await db.flush()
    db.add_all(
        [NoteLink(note_id=note.id, **link.model_dump()) for link in payload.links]
    )
    await db.commit()
    await db.refresh(note)
    return await note_response(db, note)


@campaign_router.get("/{campaign_id}/notes", response_model=list[NoteResponse])
async def list_notes(
    access: CampaignAccessDependency,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[dict[str, object]]:
    notes = (
        await db.scalars(
            select(Note)
            .where(
                Note.campaign_id == access.campaign.id,
                or_(
                    Note.owner_user_id == current_user.id,
                    Note.visibility == "shared",
                ),
            )
            .order_by(Note.updated_at.desc())
        )
    ).all()
    return [await note_response(db, note) for note in notes]


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: uuid.UUID, current_user: CurrentUser, db: DatabaseSession
) -> dict[str, object]:
    return await note_response(
        db, await accessible_note(db, note_id, current_user.id)
    )


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    payload: NoteUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    note = await db.get(Note, note_id)
    if note is None or note.owner_user_id != current_user.id:
        raise AppError(404, "note_not_found", "Nota não encontrada.")
    values = payload.model_dump(exclude_unset=True, exclude={"links"})
    for key, value in values.items():
        setattr(note, key, value.strip() if isinstance(value, str) else value)
    if payload.links is not None:
        await db.execute(delete(NoteLink).where(NoteLink.note_id == note.id))
        db.add_all(
            [NoteLink(note_id=note.id, **link.model_dump()) for link in payload.links]
        )
    await db.commit()
    await db.refresh(note)
    return await note_response(db, note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_note(
    note_id: uuid.UUID, current_user: CurrentUser, db: DatabaseSession
) -> Response:
    note = await db.get(Note, note_id)
    if note is None or note.owner_user_id != current_user.id:
        raise AppError(404, "note_not_found", "Nota não encontrada.")
    assets = (
        await db.scalars(select(MediaAsset).where(MediaAsset.note_id == note.id))
    ).all()
    for asset in assets:
        await asyncio.to_thread(delete_object, asset.object_key)
    await db.delete(note)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{note_id}/media",
    response_model=MediaUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_media_upload(
    note_id: uuid.UUID,
    payload: MediaUploadRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    note = await db.get(Note, note_id)
    if note is None or note.owner_user_id != current_user.id:
        raise AppError(404, "note_not_found", "Nota não encontrada.")
    if payload.size_bytes > settings.media_max_bytes:
        raise AppError(413, "media_too_large", "A imagem excede o limite permitido.")
    safe_name = Path(payload.filename).name.replace(" ", "-")
    asset_id = uuid.uuid4()
    object_key = f"campaigns/{note.campaign_id}/notes/{note.id}/{asset_id}-{safe_name}"
    asset = MediaAsset(
        id=asset_id,
        campaign_id=note.campaign_id,
        note_id=note.id,
        owner_user_id=current_user.id,
        object_key=object_key,
        filename=payload.filename,
        content_type=payload.content_type,
        size_bytes=payload.size_bytes,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return {
        "id": asset.id,
        "filename": asset.filename,
        "content_type": asset.content_type,
        "size_bytes": asset.size_bytes,
        "created_at": asset.created_at,
        "upload_url": presigned_upload(
            object_key, payload.content_type, payload.size_bytes
        ),
        "upload_headers": {
            "Content-Type": payload.content_type,
            "Content-Length": str(payload.size_bytes),
        },
    }


@router.get("/{note_id}/media/{asset_id}", response_model=MediaDownloadResponse)
async def get_media_download(
    note_id: uuid.UUID,
    asset_id: uuid.UUID,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> dict[str, object]:
    await accessible_note(db, note_id, current_user.id)
    asset = await db.scalar(
        select(MediaAsset).where(
            MediaAsset.id == asset_id,
            MediaAsset.note_id == note_id,
        )
    )
    if asset is None:
        raise AppError(404, "media_not_found", "Imagem não encontrada.")
    return {
        "download_url": presigned_download(asset.object_key),
        "expires_in_seconds": 900,
    }
