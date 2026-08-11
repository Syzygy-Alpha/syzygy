import httpx
import pytest

from syzygy_observatory.foundation_client import FoundationClient
from syzygy_observatory.module import observatory_descriptor


@pytest.mark.asyncio
async def test_foundation_client_registers_module() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/auth/token":
            return httpx.Response(200, json={"access_token": "token"})
        if request.url.path == "/modules/register":
            assert request.headers["Authorization"] == "Bearer token"
            payload = request.read()
            assert b"observatory" in payload
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(404)

    client = FoundationClient(
        base_url="http://foundation.test",
        username="admin",
        password="secret",
        transport=httpx.MockTransport(handler),
    )

    await client.register_module(observatory_descriptor("0.1.0"))

    assert [request.url.path for request in requests] == [
        "/auth/token",
        "/modules/register",
    ]
