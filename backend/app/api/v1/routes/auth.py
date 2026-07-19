from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.errors import AppError
from app.models import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import (
    consume_refresh_token,
    create_access_token,
    create_session,
    hash_password,
    revoke_refresh_token,
    verify_password,
)

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_session)]
RefreshCookie = Annotated[str | None, Cookie()]


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.access_token_ttl_minutes * 60,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.refresh_token_ttl_days * 86400,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/api/v1/auth",
    )


async def authenticate(response: Response, db: AsyncSession, user: User) -> AuthResponse:
    refresh_token, _ = await create_session(db, user)
    set_auth_cookies(response, create_access_token(user), refresh_token)
    await db.commit()
    await db.refresh(user)
    return AuthResponse(user=user, access_expires_in_seconds=settings.access_token_ttl_minutes * 60)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    response: Response,
    db: DatabaseSession,
) -> AuthResponse:
    existing = await db.scalar(select(User.id).where(User.email == payload.email))
    if existing is not None:
        raise AppError(409, "email_already_registered", "Este e-mail já está cadastrado.")
    user = User(
        email=payload.email,
        display_name=payload.display_name.strip(),
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return await authenticate(response, db, user)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: DatabaseSession,
) -> AuthResponse:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
        raise AppError(401, "invalid_credentials", "E-mail ou senha inválidos.")
    return await authenticate(response, db, user)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    response: Response,
    db: DatabaseSession,
    refresh_token: RefreshCookie = None,
) -> AuthResponse:
    if refresh_token is None:
        raise AppError(401, "invalid_session", "Sessão inválida ou expirada.")
    user = await consume_refresh_token(db, refresh_token)
    return await authenticate(response, db, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    db: DatabaseSession,
    refresh_token: RefreshCookie = None,
) -> None:
    if refresh_token is not None:
        await revoke_refresh_token(db, refresh_token)
        await db.commit()
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth")
