import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.main import app
from app.models import Session, User
from app.services.auth import hash_password, verify_password


def test_password_is_hashed_with_argon2() -> None:
    encoded = hash_password("uma-senha-segura")

    assert encoded.startswith("$argon2")
    assert verify_password("uma-senha-segura", encoded)
    assert not verify_password("senha-incorreta", encoded)


@pytest.mark.asyncio
async def test_register_refresh_rotation_and_logout() -> None:
    email = f"aventureiro-{uuid.uuid4()}@example.com"
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            register = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "display_name": "Aventureiro",
                    "password": "segredo-com-12-caracteres",
                },
            )
            assert register.status_code == 201
            assert register.json()["user"]["email"] == email
            assert register.cookies["access_token"]
            original_refresh = register.cookies["refresh_token"]

            duplicate = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "display_name": "Duplicado",
                    "password": "outra-senha-segura",
                },
            )
            assert duplicate.status_code == 409
            assert duplicate.json()["error"]["code"] == "email_already_registered"

            refreshed = await client.post("/api/v1/auth/refresh")
            assert refreshed.status_code == 200
            assert refreshed.cookies["refresh_token"] != original_refresh

            stale = await client.post(
                "/api/v1/auth/refresh",
                headers={"cookie": f"refresh_token={original_refresh}"},
            )
            assert stale.status_code == 401
            assert stale.json()["error"]["code"] == "invalid_session"

            logout = await client.post("/api/v1/auth/logout")
            assert logout.status_code == 204
    finally:
        async with SessionLocal() as db:
            user_id = await db.scalar(select(User.id).where(User.email == email))
            if user_id is not None:
                await db.execute(delete(Session).where(Session.user_id == user_id))
                await db.execute(delete(User).where(User.id == user_id))
                await db.commit()


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nao-existe@example.com", "password": "senha-invalida"},
        )

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "invalid_credentials",
            "message": "E-mail ou senha inválidos.",
            "details": {},
        }
    }
