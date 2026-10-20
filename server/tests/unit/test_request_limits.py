import httpx
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_chunked_json_body_cannot_bypass_limit():
    async def payload():
        for _ in range(20):
            yield b" "*65536
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://test") as client:
        response=await client.post("/api/v1/projects",content=payload(),headers={"Content-Type":"application/json"})
    assert response.status_code == 413,response.text
    assert response.json()["error"]["code"]=="request_too_large"


@pytest.mark.asyncio
async def test_identity_headers_do_not_authenticate_requests():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://test") as client:
        response=await client.get("/api/v1/users/me",headers={"X-User-ID":"unverified"})
    assert response.status_code == 401
