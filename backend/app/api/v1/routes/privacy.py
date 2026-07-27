import logging

from fastapi import APIRouter, Response

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.privacy import (
    AccountDeletionRequest,
    AccountDeletionResponse,
    AccountExportResponse,
)
from app.services.privacy import (
    delete_account_data,
    export_account_data,
    export_timestamp,
)
from app.services.storage import delete_object

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/export", response_model=AccountExportResponse)
async def export_account(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> AccountExportResponse:
    return AccountExportResponse(
        generated_at=export_timestamp(),
        data=await export_account_data(db, current_user),
    )


@router.delete("", response_model=AccountDeletionResponse)
async def delete_account(
    payload: AccountDeletionRequest,
    response: Response,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> AccountDeletionResponse:
    del payload
    media_keys = await delete_account_data(db, current_user)
    await db.commit()
    for object_key in media_keys:
        try:
            delete_object(object_key)
        except Exception:
            logger.exception("Falha ao remover objeto após exclusão de conta.")
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return AccountDeletionResponse(
        retained=[
            "eventos de auditoria pseudonimizados durante o prazo de retenção",
            "campanhas próprias arquivadas para integridade referencial",
        ]
    )
