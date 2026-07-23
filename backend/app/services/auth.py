import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.models import Session, User

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    return password_hash.verify(password, encoded)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user: User) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(user.id),
            "type": "access",
            "ver": user.auth_version,
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
        },
        settings.jwt_secret,
        algorithm="HS256",
    )


async def create_session(db: AsyncSession, user: User) -> tuple[str, Session]:
    raw_token = secrets.token_urlsafe(48)
    session = Session(
        user_id=user.id,
        refresh_token_hash=token_digest(raw_token),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days),
    )
    db.add(session)
    await db.flush()
    return raw_token, session


async def consume_refresh_token(db: AsyncSession, raw_token: str) -> User:
    result = await db.execute(
        select(Session).where(Session.refresh_token_hash == token_digest(raw_token))
    )
    session = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if session is None or session.revoked_at is not None or session.expires_at <= now:
        raise AppError(401, "invalid_session", "Sessão inválida ou expirada.")
    user = await db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise AppError(401, "invalid_session", "Sessão inválida ou expirada.")
    session.revoked_at = now
    return user


async def revoke_refresh_token(db: AsyncSession, raw_token: str) -> None:
    result = await db.execute(
        select(Session).where(Session.refresh_token_hash == token_digest(raw_token))
    )
    session = result.scalar_one_or_none()
    if session is not None and session.revoked_at is None:
        session.revoked_at = datetime.now(UTC)


def decode_access_token(token: str) -> tuple[uuid.UUID, int]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise ValueError
        return uuid.UUID(payload["sub"]), int(payload["ver"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as error:
        raise AppError(401, "invalid_access_token", "Acesso não autenticado.") from error
