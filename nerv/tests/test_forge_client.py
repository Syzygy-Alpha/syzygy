from datetime import UTC, datetime

import httpx
import pytest

from syzygy_nerv.forge_client import ForgeClient, ForgeClientError


@pytest.mark.asyncio
async def test_forge_client_lists_projects_and_commands() -> None:
    now = datetime.now(UTC).isoformat()

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/projects":
            return httpx.Response(
                200,
                json=[{"name": "demo", "path": "C:/demo", "created_at": now, "updated_at": now}],
            )
        if request.url.path == "/projects/demo/commands":
            return httpx.Response(
                200,
                json={
                    "project": "demo",
                    "manifest_path": "C:/demo/syzygy.project.toml",
                    "commands": [{"name": "test", "command": "python -m pytest"}],
                },
            )
        return httpx.Response(404, json={"detail": "missing"})

    client = ForgeClient(
        base_url="http://forge.test",
        timeout_seconds=1.0,
        transport=httpx.MockTransport(handler),
    )

    projects = await client.list_projects()
    commands = await client.project_commands("demo")

    assert projects[0].name == "demo"
    assert commands.commands[0].name == "test"


@pytest.mark.asyncio
async def test_forge_client_refuses_to_run_blocked_plan() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/projects/demo/commands/build/plan":
            return httpx.Response(
                200,
                json={
                    "project": "demo",
                    "command_name": "build",
                    "command": "npm run build",
                    "cwd": "C:/demo",
                    "argv": ["npm", "run", "build"],
                    "allowed": False,
                    "reason": "command executable is not allowed",
                },
            )
        raise AssertionError("A blocked plan must not reach the Forge run endpoint")

    client = ForgeClient(
        base_url="http://forge.test",
        timeout_seconds=1.0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ForgeClientError, match="not allowed"):
        await client.run_command("demo", "build", 30)
