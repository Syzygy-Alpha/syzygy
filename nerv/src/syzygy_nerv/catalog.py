from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from syzygy_nerv.config import Settings


class SurfaceLinks(BaseModel):
    root_url: str
    health_url: str
    capabilities_url: str


class SurfaceAction(BaseModel):
    name: str
    label: str
    description: str
    method: str = "GET"
    path: str
    body: dict[str, Any] = Field(default_factory=dict)


class SurfaceEntry(BaseModel):
    name: str
    label: str
    group: str
    description: str
    accent: str
    cwd: str
    launch_command: list[str] = Field(default_factory=list)
    launch_enabled: bool = True
    links: SurfaceLinks
    actions: list[SurfaceAction] = Field(default_factory=list)


class SurfaceCatalog:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.workspace_root = settings.workspace_root.resolve()
        self.entries = {entry.name: entry for entry in self._build_entries()}

    def list(self) -> list[SurfaceEntry]:
        return list(self.entries.values())

    def get(self, name: str) -> SurfaceEntry | None:
        return self.entries.get(name)

    def _build_entries(self) -> list[SurfaceEntry]:
        return [
            self._entry(
                name="foundation",
                label="FOUNDATION",
                group="core",
                description="Core contracts, auth, scheduler, and module lifecycle.",
                accent="#f6d64a",
                module_dir="foundation",
                package="syzygy_foundation",
                port=8000,
                actions=[
                    self._action(
                        name="health",
                        label="Health",
                        description="Read the Foundation health contract.",
                        path="/health",
                    ),
                    self._action(
                        name="version",
                        label="Version",
                        description="Read Foundation version metadata.",
                        path="/version",
                    ),
                ],
            ),
            self._entry(
                name="forge",
                label="FORGE",
                group="engineering",
                description="Projects, commands, Git workflows, and automation.",
                accent="#ff7b39",
                module_dir="forge",
                package="syzygy_forge",
                port=8010,
                actions=[
                    self._action(
                        name="current-project",
                        label="Current Project",
                        description="Inspect the configured Forge workspace.",
                        path="/projects/current",
                    ),
                    self._action(
                        name="projects",
                        label="Projects",
                        description="List registered local Forge projects.",
                        path="/projects",
                    ),
                    self._action(
                        name="outbox-summary",
                        label="Outbox Summary",
                        description="Read the Forge event outbox summary.",
                        path="/events/outbox/summary",
                    ),
                ],
            ),
            self._entry(
                name="observatory",
                label="OBSERVATORY",
                group="observability",
                description="Health observations, polling, and local operational visibility.",
                accent="#f04d5e",
                module_dir="observatory",
                package="syzygy_observatory",
                port=8020,
                actions=[
                    self._action(
                        name="health-summary",
                        label="Health Summary",
                        description="Read the latest local health summary.",
                        path="/health-observations/summary",
                    ),
                    self._action(
                        name="health-trends",
                        label="Health Trends",
                        description="Read aggregated health trend information.",
                        path="/health-observations/trends",
                    ),
                    self._action(
                        name="polling-status",
                        label="Polling Status",
                        description="Check Foundation polling status in Observatory.",
                        path="/ingest/foundation/modules/polling",
                    ),
                ],
            ),
            self._entry(
                name="mycelium",
                label="MYCELIUM",
                group="mesh",
                description="Local mesh identity and manually known peer registry.",
                accent="#49c7b6",
                module_dir="mycelium",
                package="syzygy_mycelium",
                port=8030,
                actions=[
                    self._action(
                        name="local-node",
                        label="Local Node",
                        description="Read the local Hypha node descriptor.",
                        path="/node",
                    ),
                    self._action(
                        name="known-peers",
                        label="Known Peers",
                        description="List manually registered Mycelium peers.",
                        path="/peers",
                    ),
                ],
            ),
            self._entry(
                name="nerv",
                label="NERV",
                group="operations",
                description="Operational command center for local SYZYGY surfaces.",
                accent="#ff2038",
                module_dir="nerv",
                package="syzygy_nerv",
                port=8040,
                launch_enabled=False,
                actions=[
                    self._action(
                        name="dashboard-state",
                        label="Dashboard State",
                        description="Read the current NERV operational snapshot.",
                        path="/api/dashboard",
                    ),
                    self._action(
                        name="capabilities",
                        label="Capabilities",
                        description="Read the NERV capability descriptor.",
                        path="/capabilities",
                    ),
                ],
            ),
        ]

    def _entry(
        self,
        *,
        name: str,
        label: str,
        group: str,
        description: str,
        accent: str,
        module_dir: str,
        package: str,
        port: int,
        launch_enabled: bool = True,
        actions: list[SurfaceAction] | None = None,
    ) -> SurfaceEntry:
        cwd = self.workspace_root / module_dir
        base_url = f"http://{self.settings.module_host}:{port}"
        command = [
            self.settings.python_executable,
            "-m",
            "uvicorn",
            f"{package}.main:app",
            "--host",
            self.settings.module_host,
            "--port",
            str(port),
        ]
        return SurfaceEntry(
            name=name,
            label=label,
            group=group,
            description=description,
            accent=accent,
            cwd=str(cwd),
            launch_command=command,
            launch_enabled=launch_enabled,
            links=SurfaceLinks(
                root_url=f"{base_url}/",
                health_url=f"{base_url}/health",
                capabilities_url=f"{base_url}/capabilities",
            ),
            actions=actions or [],
        )

    def _action(
        self,
        *,
        name: str,
        label: str,
        description: str,
        path: str,
        method: str = "GET",
        body: dict[str, Any] | None = None,
    ) -> SurfaceAction:
        return SurfaceAction(
            name=name,
            label=label,
            description=description,
            method=method,
            path=path,
            body=body or {},
        )
