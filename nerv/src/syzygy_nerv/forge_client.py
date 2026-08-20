from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field


class ForgeProject(BaseModel):
    name: str
    path: str
    created_at: datetime
    updated_at: datetime


class ForgeProjectCommand(BaseModel):
    name: str
    command: str


class ForgeProjectCommandSet(BaseModel):
    project: str
    manifest_path: str
    commands: list[ForgeProjectCommand] = Field(default_factory=list)


class ForgeProjectCommandPlan(BaseModel):
    project: str
    command_name: str
    command: str
    cwd: str
    argv: list[str] = Field(default_factory=list)
    allowed: bool
    reason: str


class ForgeProjectCommandRunResult(BaseModel):
    run_id: int | None = None
    plan: ForgeProjectCommandPlan
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    started_at: datetime
    completed_at: datetime


class ForgeClientError(ValueError):
    pass


class ForgeClient:
    """Typed client for the small Forge project-command contract used by NERV."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def list_projects(self) -> list[ForgeProject]:
        payload = await self._request("GET", "/projects")
        if not isinstance(payload, list):
            msg = "Forge projects response was not a list"
            raise ForgeClientError(msg)
        return [ForgeProject.model_validate(project) for project in payload]

    async def project_commands(self, project_name: str) -> ForgeProjectCommandSet:
        project_segment = self._path_segment(project_name)
        payload = await self._request("GET", f"/projects/{project_segment}/commands")
        return ForgeProjectCommandSet.model_validate(payload)

    async def command_plan(
        self,
        project_name: str,
        command_name: str,
    ) -> ForgeProjectCommandPlan:
        project_segment = self._path_segment(project_name)
        command_segment = self._path_segment(command_name)
        payload = await self._request(
            "GET",
            f"/projects/{project_segment}/commands/{command_segment}/plan",
        )
        return ForgeProjectCommandPlan.model_validate(payload)

    async def run_command(
        self,
        project_name: str,
        command_name: str,
        timeout_seconds: int,
    ) -> ForgeProjectCommandRunResult:
        plan = await self.command_plan(project_name, command_name)
        if not plan.allowed:
            msg = f"Forge command plan is not allowed: {plan.reason}"
            raise ForgeClientError(msg)
        project_segment = self._path_segment(project_name)
        command_segment = self._path_segment(command_name)
        payload = await self._request(
            "POST",
            f"/projects/{project_segment}/commands/{command_segment}/runs",
            json={"confirm": True, "timeout_seconds": timeout_seconds},
        )
        return ForgeProjectCommandRunResult.model_validate(payload)

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
    ) -> Any:
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.request(method, path, json=json)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ForgeClientError(self._response_error(exc.response)) from exc
        except httpx.HTTPError as exc:
            raise ForgeClientError(str(exc)) from exc
        try:
            return response.json()
        except ValueError as exc:
            raise ForgeClientError("Forge response was not valid JSON") from exc

    def _response_error(self, response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return f"Forge request failed with HTTP {response.status_code}"
        if isinstance(payload, dict) and isinstance(payload.get("detail"), str):
            return payload["detail"]
        return f"Forge request failed with HTTP {response.status_code}"

    def _path_segment(self, value: str) -> str:
        return quote(value, safe="")
