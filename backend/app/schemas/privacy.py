from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class AccountExportResponse(BaseModel):
    format_version: Literal["1.0"] = "1.0"
    generated_at: datetime
    data: dict[str, Any]


class AccountDeletionRequest(BaseModel):
    confirmation: Literal["EXCLUIR"]


class AccountDeletionResponse(BaseModel):
    status: Literal["deleted"] = "deleted"
    retained: list[str]
