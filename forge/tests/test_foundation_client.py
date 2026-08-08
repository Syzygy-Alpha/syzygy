import json

import httpx
import pytest

from syzygy_forge.foundation_client import FoundationClient
from syzygy_forge.module import forge_descriptor


@pytest.mark.asyncio
async def test_foundation_client_registers_module() -> None:
    requests: list[tuple[str, str, dict[str, object]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = dict(json.loads(request.content.decode("utf-8")))
        requests.append((request.method, request.url.path, payload))
        if request.url.path == "/auth/token":
            return httpx.Response(200, json={"access_token": "token"})
        if request.url.path == "/modules/register":
            assert request.headers["Authorization"] == "Bearer token"
            return httpx.Response(200, json=payload)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = FoundationClient("http://foundation", "admin", "password", transport=transport)
    await client.register_module(forge_descriptor("0.1.0"))

    assert requests[0][1] == "/auth/token"
    assert requests[1][1] == "/modules/register"
    assert requests[1][2]["name"] == "forge"
