from __future__ import annotations

import asyncio

from pydantic import BaseModel, Field

from syzygy_nerv.forge_client import (
    ForgeClient,
    ForgeClientError,
    ForgeProject,
    ForgeProjectCommand,
)


class ForgeWorkbenchProject(BaseModel):
    project: ForgeProject
    manifest_path: str | None = None
    commands: list[ForgeProjectCommand] = Field(default_factory=list)
    error: str | None = None


class ForgeWorkbenchSnapshot(BaseModel):
    reachable: bool
    projects: list[ForgeWorkbenchProject] = Field(default_factory=list)
    error: str | None = None


class ForgeWorkbenchService:
    def __init__(self, forge_client: ForgeClient) -> None:
        self.forge_client = forge_client

    async def snapshot(self) -> ForgeWorkbenchSnapshot:
        try:
            projects = await self.forge_client.list_projects()
        except ForgeClientError as exc:
            return ForgeWorkbenchSnapshot(reachable=False, error=str(exc))

        project_surfaces = await asyncio.gather(
            *(self._project_surface(project) for project in projects)
        )
        return ForgeWorkbenchSnapshot(reachable=True, projects=project_surfaces)

    async def _project_surface(self, project: ForgeProject) -> ForgeWorkbenchProject:
        try:
            command_set = await self.forge_client.project_commands(project.name)
        except ForgeClientError as exc:
            return ForgeWorkbenchProject(project=project, error=str(exc))
        return ForgeWorkbenchProject(
            project=project,
            manifest_path=command_set.manifest_path,
            commands=command_set.commands,
        )
