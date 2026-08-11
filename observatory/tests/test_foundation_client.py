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


@pytest.mark.asyncio
async def test_foundation_client_lists_modules() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/auth/token":
            return httpx.Response(200, json={"access_token": "token"})
        if request.url.path == "/modules":
            assert request.headers["Authorization"] == "Bearer token"
            return httpx.Response(
                200,
                json=[
                    {
                        "name": "forge",
                        "version": "0.1.0",
                        "status": "online",
                        "health": {"status": "ok", "details": {"port": "8010"}},
                        "capabilities": ["git"],
                        "dependencies": ["foundation"],
                    }
                ],
            )
        return httpx.Response(404)

    client = FoundationClient(
        base_url="http://foundation.test",
        username="admin",
        password="secret",
        transport=httpx.MockTransport(handler),
    )

    modules = await client.list_modules()

    assert [request.url.path for request in requests] == ["/auth/token", "/modules"]
    assert len(modules) == 1
    assert modules[0].name == "forge"
    assert modules[0].health.status == "ok"
    assert modules[0].health.details == {"port": "8010"}
