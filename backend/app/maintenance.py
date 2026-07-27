import argparse
import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import AuditLog, PasswordResetToken, Session


async def apply_retention(*, dry_run: bool) -> dict[str, int]:
    now = datetime.now(UTC)
    session_cutoff = now - timedelta(days=settings.session_retention_days)
    audit_cutoff = now - timedelta(days=settings.audit_retention_days)
    async with SessionLocal() as db:
        expired_sessions = int(
            await db.scalar(
                select(func.count(Session.id)).where(
                    (Session.expires_at < now)
                    | (
                        Session.revoked_at.is_not(None)
                        & (Session.revoked_at < session_cutoff)
                    )
                )
            )
            or 0
        )
        expired_reset_tokens = int(
            await db.scalar(
                select(func.count(PasswordResetToken.id)).where(
                    (PasswordResetToken.expires_at < now)
                    | (PasswordResetToken.used_at < session_cutoff)
                )
            )
            or 0
        )
        audit_review_candidates = int(
            await db.scalar(
                select(func.count(AuditLog.id)).where(AuditLog.created_at < audit_cutoff)
            )
            or 0
        )
        if not dry_run:
            await db.execute(
                delete(Session).where(
                    (Session.expires_at < now)
                    | (
                        Session.revoked_at.is_not(None)
                        & (Session.revoked_at < session_cutoff)
                    )
                )
            )
            await db.execute(
                delete(PasswordResetToken).where(
                    (PasswordResetToken.expires_at < now)
                    | (PasswordResetToken.used_at < session_cutoff)
                )
            )
            await db.commit()
    return {
        "expired_sessions": expired_sessions,
        "expired_password_reset_tokens": expired_reset_tokens,
        "audit_review_candidates": audit_review_candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Manutenção operacional do Nexus d20.")
    parser.add_argument("command", choices=["retention"])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = asyncio.run(apply_retention(dry_run=not args.apply))
    mode = "aplicado" if args.apply else "simulação"
    print(f"Retenção ({mode}): {result}")


if __name__ == "__main__":
    main()
