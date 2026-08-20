import httpx
import pytest

from syzygy_nerv.catalog import SurfaceCatalog
from syzygy_nerv.config import Settings
from syzygy_nerv.surface_actions import SurfaceActionExecutor


@pytest.mark.asyncio
async def test_surface_action_executor_returns_json_payload() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/projects/current":
            return httpx.Response(200, json={"path": "C:/syzygy", "dirty": False})
        return httpx.Response(404, json={"detail": "missing"})

    catalog = SurfaceCatalog(Settings())
    executor = SurfaceActionExecutor(
        catalog=catalog,
        timeout_seconds=1.0,
        transport=httpx.MockTransport(handler),
    )

    result = await executor.execute("forge", "current-project")

    assert result.ok is True
    assert result.status_code == 200
    assert result.payload == {"path": "C:/syzygy", "dirty": False}


@pytest.mark.asyncio
async def test_surface_action_executor_surfaces_http_errors() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"detail": "offline"})

    catalog = SurfaceCatalog(Settings())
    executor = SurfaceActionExecutor(
        catalog=catalog,
        timeout_seconds=1.0,
        transport=httpx.MockTransport(handler),
    )

    result = await executor.execute("observatory", "health-summary")

    assert result.ok is False
    assert result.status_code == 503
    assert result.error == "offline"
