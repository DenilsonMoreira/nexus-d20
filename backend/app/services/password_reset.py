import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.models import PasswordResetToken, Session, User
from app.services.auth import hash_password, token_digest


async def create_password_reset_token(db: AsyncSession, user: User) -> str:
    now = datetime.now(UTC)
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    raw_token = secrets.token_urlsafe(48)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=token_digest(raw_token),
            expires_at=now + timedelta(minutes=settings.password_reset_ttl_minutes),
        )
    )
    await db.flush()
    return raw_token


async def reset_password(db: AsyncSession, raw_token: str, new_password: str) -> None:
    reset_token = await db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_digest(raw_token)
        )
    )
    now = datetime.now(UTC)
    if (
        reset_token is None
        or reset_token.used_at is not None
        or reset_token.expires_at <= now
    ):
        raise AppError(400, "invalid_password_reset", "Link inválido ou expirado.")
    user = await db.get(User, reset_token.user_id)
    if user is None or not user.is_active:
        raise AppError(400, "invalid_password_reset", "Link inválido ou expirado.")
    user.password_hash = hash_password(new_password)
    user.auth_version += 1
    reset_token.used_at = now
    await db.execute(
        update(Session)
        .where(Session.user_id == user.id, Session.revoked_at.is_(None))
        .values(revoked_at=now)
    )
