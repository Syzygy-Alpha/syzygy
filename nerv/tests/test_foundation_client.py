import httpx
import pytest

from syzygy_nerv.foundation_client import FoundationClient
from syzygy_nerv.module import nerv_descriptor


@pytest.mark.asyncio
async def test_foundation_client_registers_module() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/auth/token":
            return httpx.Response(200, json={"access_token": "token"})
        if request.url.path == "/modules/register":
            assert request.headers["Authorization"] == "Bearer token"
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(404)

    client = FoundationClient(
        base_url="http://foundation.test",
        username="admin",
        password="secret",
        transport=httpx.MockTransport(handler),
    )

    await client.register_module(nerv_descriptor("0.1.0"))

    assert [request.url.path for request in requests] == ["/auth/token", "/modules/register"]


@pytest.mark.asyncio
async def test_foundation_client_lists_modules() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/auth/token":
            return httpx.Response(200, json={"access_token": "token"})
        if request.url.path == "/modules":
            return httpx.Response(
                200,
                json=[
                    {
                        "name": "foundation",
                        "version": "0.1.0",
                        "status": "online",
                        "health": {"status": "ok", "details": {}},
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

    assert modules[0].name == "foundation"
