import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_swagger_has_a_compatible_content_security_policy() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/docs")

    assert response.status_code == 200
    assert "SwaggerUIBundle" in response.text
    policy = response.headers["content-security-policy"]
    assert "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" in policy
    assert "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" in policy


@pytest.mark.asyncio
async def test_api_responses_keep_the_strict_policy() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.headers["content-security-policy"] == (
        "default-src 'self'; frame-ancestors 'none'; object-src 'none'"
    )
